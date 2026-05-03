#!/usr/bin/env python
'''
@author     : Confluent Inc, Srinivas Sahu
Date        : 20231206
Usage       : dr_mgr.py [-h] -o {status,failover,failback,prep_failover,prep_failback} [-t {force,validate_only}]
Dependency  : clusterlink_mgr.py mirror_topics.py switch_traffic.py
Description : A comprehensive tool to manage dr failover/failback process. Inserts a event in traffic-router topic for producers/consumers to switch between sites seameless.
'''

import os
import sys
import json
import time
import base64
import logging
import requests
import argparse
from contextlib import contextmanager
from datetime import datetime 
from confluent_kafka import Producer, KafkaException
from config_mgr import *
from clusterlink_mgr import *
from mirror_topic_mgr import *
from switch_traffic import TrafficRouterProducer

def main(args):
    operation = args.operation
    op_type = args.op_type

    logging.basicConfig(filename='dr_mgr_{:%Y%m%d}.log'.format(datetime.now()), format='%(asctime)s %(message)s', encoding='utf-8', level=logging.DEBUG)

    cluster_info={}
    #-- Cluster Link ID
    cluster_info = { **clusterlink_config() }

    #-- Primary cluster configuration
    primary_cluster = { **cluster_config_primary() }
    primary_api_auth = base64.b64encode(f"{primary_cluster['api_key']}:{primary_cluster['api_secret']}".encode()).decode()
    primary_headers = { 'Authorization': f"Basic {primary_api_auth}" }    
    primary_cluster['header'] = primary_headers
    cluster_info['primary'] = primary_cluster

    #-- Secondary cluster configuration
    secondary_cluster = { **cluster_config_secondary() }
    secondary_api_auth = base64.b64encode(f"{secondary_cluster['api_key']}:{secondary_cluster['api_secret']}".encode()).decode()
    secondary_headers = { 'Authorization': f"Basic {secondary_api_auth}" }    
    secondary_cluster['header'] = secondary_headers
    cluster_info['secondary'] = secondary_cluster

    kafka_info={}
    #-- health check topic
    kafka_info = { **healthcheck_config() }
    #-- Primary kafka configuration
    kafka_info['primary'] = { **kafka_config_primary() }
    #-- Secondary kafka configuration
    kafka_info['secondary'] = { **kafka_config_secondary() }

    #WARNING: Uncommenting the below will write api key/secrets to the log
    #logging.debug ('cluster config:' + json.dumps(cluster_info, indent=2))
    if operation != 'status' and operation != 'healthcheck' and op_type == 'force':
            print ('!!!!!!!!!! This operation ' + operation.upper() + ' can disrupt the data pipeline !!!!!!!')
            choice = input('Do you want to continue (y/n): ')
            if choice not in {'y','Y'}:
                exit()

    if operation == 'status':
        status( cluster_info )
    elif operation == 'healthcheck':
        healthcheck( kafka_info )
    elif operation == 'failover':
        failover( cluster_info, operation, op_type)
    elif operation == 'prep_failover':
        prep_failover( cluster_info, operation, op_type)
    elif operation == 'failback':
        failback( cluster_info, operation, op_type)
    elif operation == 'prep_failback':
        prep_failback( cluster_info, operation, op_type)
   
'''
-----------------------------------------------------------------------------------------------------------
Supress stdout from the sub modules
-----------------------------------------------------------------------------------------------------------
'''
@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

'''
-----------------------------------------------------------------------------------------------------------
healthcheck function to check the availability of primary & secondary clusters
Alerts the ops team if any of these clusters are down.
-----------------------------------------------------------------------------------------------------------
'''
def healthcheck( kafka_info ):

    success_cnt=0 

    def delivery_callback(err, msg):
        nonlocal success_cnt
        if err:
            success_cnt-=1
            #sys.stderr.write('%% Message failed delivery: %s\n' % err)
        else:
            success_cnt+=1
            #sys.stderr.write('%% Message delivered to %s %s [%d] @ %d, value: %s, timestamp: %s\n' % (site, msg.topic(), msg.partition(), msg.offset(), msg.value(), msg.timestamp()))

            
    sites = ["primary", "secondary"]
    
    for site in sites:
        cnt=1
        p = Producer(kafka_info[site])
        while True:
            try:
                logging.debug ('Health Check site : ' + site + ' topic: ' + kafka_info['hc_topic'] ) 
                key=datetime.today().strftime('%Y%m%d%H%M')
                value=key + ',' + site + ',' + 'healthcheck'
                p.produce(''.join(kafka_info['hc_topic']), value.rstrip(), key.rstrip(), callback=delivery_callback)

            except BufferError:
                #TODO: Alert Ops Team
                sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' % len(p))
                logging.debug ('Reason: ' + 'Local producer queue is full (%d messages awaiting delivery): try again' % len(p))
            except KeyboardInterrupt:
                sys.stderr.write('Exit with Keyboard Interrupt\n')
                logging.debug ('Reason: ' + 'Exit with Keyboard Interrupt')
            except Exception as e:
                logging.debug ('Reason: ' + 'Unknown Exception' + e)
                #TODO: Alert Ops Team

            cnt+=1
            if cnt > 10:
                break
        p.flush()        
        if success_cnt < 10:
            logging.debug ('HEALTHCHECK FAIL - site : ' + site + ' Success Count : ' + str(success_cnt) ) 
            print ('FAIL - ' + site)
            #TODO: Alert Ops Team     
        else:
            logging.debug ('HEALTHCHECK PASS - site : ' + site + ' Success Count : ' + str(success_cnt) ) 
            print ('PASS - ' + site)
        success_cnt=0   

'''
-----------------------------------------------------------------------------------------------------------
status function displays the current status of clusterlinks and mirror topics from both sites
Run this option first for a holistic view before executing failover/failback
-----------------------------------------------------------------------------------------------------------
'''
def status( cluster_info):

    logging.debug ('DR_MGR-STATUS')
    sites = ["primary", "secondary"]

    clusterdata={}
    mirrordata={}
    for site in sites:
        rest_url=cluster_info[site]['rest_url'] 
        header=cluster_info[site]['header']
        cluster_id=cluster_info[site]['cluster_id']
        cluster_link_id= cluster_info['link_id']

        mirrordata[site]={}
        mirror_data_found = False
        with suppress_stdout():
            logging.debug ('DR_MGR-STATUS  mirror_topic_list site: ' + site)
            res=mirror_topic_list (rest_url, header, cluster_id, cluster_link_id, None)
        if res.status_code == 200:
            mt_o=json.loads(res.text)['data']
            for x in range(len(mt_o)):
                mirror_data_found = True
                link_name=mt_o[x]['link_name']
                mirror_topic_name=mt_o[x]['mirror_topic_name']
                source_topic_name=mt_o[x]['source_topic_name']
                if link_name not in mirrordata[site]:
                    mirrordata[site][link_name]={}
                mirrordata[site][link_name][mirror_topic_name]={}
                mirrordata[site][link_name][mirror_topic_name]['status']=mt_o[x]['mirror_status']
                mirrordata[site][link_name][mirror_topic_name]['pcount']=mt_o[x]['num_partitions']
                mirrordata[site][link_name][mirror_topic_name]['source']=source_topic_name
        else:
            print ('mirror_topic_list : ' + str(res.status_code) + ':' + res.reason)
            exit()

        logging.debug ('DR_MGR-STATUS rest_url: ' + rest_url + ', cluster_id: ' + cluster_id)

        clusterdata[site]={}
        with suppress_stdout():
            logging.debug ('DR_MGR-STATUS  clusterlink_list site: ' + site)
            res=clusterlink_list (rest_url, header, cluster_id)
        if res.status_code == 200:
            cl_o=json.loads(res.text)['data']
            mt_list=[]
            for x in range(len(cl_o)):
                this_cluster_id=cl_o[x]['metadata']['self'].split('/')[-3]
                source_cluster_id=cl_o[x]['source_cluster_id']
                link_name=cl_o[x]['link_name']
                link_state=cl_o[x]['link_state']

                clusterdata[site][link_name]={}
                clusterdata[site][link_name]['state']=link_state
                clusterdata[site][link_name]['local_cid']=this_cluster_id
                clusterdata[site][link_name]['source_cid']=source_cluster_id
                clusterdata[site][link_name]['topic']={}
                if mirror_data_found:
                    for topic in mirrordata[site][link_name]:
                        clusterdata[site][link_name]['topic'][topic]={}
                        clusterdata[site][link_name]['topic'][topic]['pcount']=''
                        clusterdata[site][link_name]['topic'][topic]['status']=''
                        clusterdata[site][link_name]['topic'][topic]['source']=''
                        if mirror_data_found:
                            clusterdata[site][link_name]['topic'][topic]['pcount']=mirrordata[site][link_name][topic]['pcount']
                            clusterdata[site][link_name]['topic'][topic]['status']=mirrordata[site][link_name][topic]['status']
                            clusterdata[site][link_name]['topic'][topic]['source']=mirrordata[site][link_name][topic]['source']
        else:
            print ('clusterlink_list : ' + str(res.status_code) + ':' + res.reason)
            exit()

    #--- Pretty Report the cluster link status 
    primary_link = secondary_link = state = None
    for key in clusterdata['primary']:
        primary_link=key
        primary_link+= ' (' + clusterdata['primary'][key]['state'] + ')'
        primary_cluster_id=clusterdata['primary'][key]['local_cid']
        secondary_cluster_id=clusterdata['primary'][key]['source_cid']
    for key in clusterdata['secondary']:
        secondary_link=key
        secondary_link+= ' (' + clusterdata['secondary'][key]['state'] + ')'
        secondary_cluster_id=clusterdata['secondary'][key]['local_cid']
        primary_cluster_id=clusterdata['secondary'][key]['source_cid']

    if primary_link == secondary_link == None:
        print ( 'No cluster links found in primary & secondary site')
        exit()

    p2s, s2p, hyphen = '==>>', '<<==', '-'
    pcid='CLUSTER:' + primary_cluster_id + ' (PRIMARY) '
    scid='CLUSTER:' + secondary_cluster_id + ' (SECONDARY) '

    print ( pcid.center(45, hyphen) + '   |   ' +  scid.center(45, hyphen) )
    if primary_link is None:
        slink='LINK:' + secondary_link
        print ( hyphen.center(45, hyphen) + '   |   ' + slink.center(45, hyphen) )
        print ( 'SOURCE TOPIC'.center(45, hyphen) + '   |   '  +  'MIRROR TOPIC'.center(30, hyphen) + ' ' + 'P#'.center(4, hyphen) + ' ' + 'STATUS'.center(9, hyphen) )
        if len(clusterdata['secondary'][link_name]['topic'].keys()) > 0:        #-- After a cluster link is created it takes ~5min for the mirroring to start
            for topic in clusterdata['secondary'][link_name]['topic']:
                pcount= str(clusterdata['secondary'][link_name]['topic'][topic]['pcount']) or 'NA'
                status= clusterdata['secondary'][link_name]['topic'][topic]['status'] or 'NA'
                source= clusterdata['secondary'][link_name]['topic'][topic]['source'] or 'NA'
                print ( source.ljust(45, ' ') + p2s.center(7,' ') + topic.ljust(30, ' ') + ' ' + pcount.rjust(4, ' ') + ' ' + status.rjust(9, ' '))
        else:
            print ( 'Wait ~5min for auto-mirror thread to start')
    else:
        plink='LINK:' + primary_link
        print ( plink.center(45, hyphen) + '   |   ' + hyphen.center(45, hyphen) )
        print ( 'MIRROR TOPIC'.center(30, hyphen) + ' ' + 'P#'.center(4, hyphen) + ' ' + 'STATUS'.center(9, hyphen) + '   |   ' + 'SOURCE TOPIC'.center(45, hyphen))
        if len(clusterdata['primary'][link_name]['topic'].keys()) > 0:          #-- After a cluster link is created it takes ~5min for the mirroring to start
            for topic in clusterdata['primary'][link_name]['topic']:
                pcount= str(clusterdata['primary'][link_name]['topic'][topic]['pcount'])
                status= clusterdata['primary'][link_name]['topic'][topic]['status']
                source= clusterdata['primary'][link_name]['topic'][topic]['source']
                print ( topic.ljust(30, ' ') + ' ' + pcount.rjust(4, ' ') + ' ' + status.rjust(9, ' ') + s2p.center(7,' ') + source.ljust(45, ' '))
        else:
            print ( 'Wait ~5min for auto-mirror thread to start')

'''
-----------------------------------------------------------------------------------------------------------
prep_failover function performs the following tasks
    1. Get the list of mirror topics from clusterlink in primary, these will be in STOPPED state
    2. Delete the list of topics from step#1 in secondary
    3. Delete the clusterlink secondary -> primary in primary     (old destination)
    4. Create the clusterlink primary -> secondary in secondary, with the list of mirror topics from step#1   (new destination)
-----------------------------------------------------------------------------------------------------------
'''
def prep_failover( cluster_info, operation, op_type):

    #-- Get the mirror topics from primary cluster
    print ('======== ' + operation.upper() + ' -IDENTIFY MIRROR TOPICS')
    link_id= cluster_info['link_id']

    rest_url=cluster_info['primary']['rest_url'] 
    header=cluster_info['primary']['header']
    cluster_id=cluster_info['primary']['cluster_id']

    mirror_status=None  #-- None for All statuses (active, failed, paused, stopped, pending_stopped)
    with suppress_stdout():
        res=mirror_topic_list( rest_url, header, cluster_id, link_id, mirror_status)
    topic_list={}
    if res.status_code == 200:
        mt_o=json.loads(res.text)['data']
        num_topics=len(mt_o)
        logging.debug ('topics to mirror : ' + str(num_topics))
        active_mirror_topics=0
        for x in range(num_topics):
            mirror_topic_name=mt_o[x]['mirror_topic_name']
            source_topic_name=mt_o[x]['source_topic_name']
            mirror_status=mt_o[x]['mirror_status']
            topic_list[mirror_topic_name]=mirror_status
            if mirror_status == 'ACTIVE':       #--- All mirror topics should be in STOPPED state during this phase of DR
                active_mirror_topics+=1
        print ('Total Topics :' + str(num_topics) + ' Active Topics :' + str(active_mirror_topics))
        if active_mirror_topics > 0:
            print ('ERROR: Cluster link cannot be deleted when ACTIVE mirror topics found in the cluster link')
            exit()
    else:
        print (json.loads(res.text)['message'])
        exit()

    #-- Delete the list of topics in secondary
    if op_type == 'validate_only':
        print ('not deleting the topics in primary for operation:validate_only')
    else:
        print ('======== ' + operation.upper() + ' -DELETING TOPICS IN SECONDARY')
        rest_url=cluster_info['secondary']['rest_url'] 
        header=cluster_info['secondary']['header']
        cluster_id=cluster_info['secondary']['cluster_id']

        if len(topic_list) > 0:
            for topic in topic_list:
                mirror_topic_delete( rest_url, header, cluster_id, link_id, topic)
        else:
            print ('Topics already deleted or not found in secondary')

    #-- sleep before creating the clusterlink as the topic deletion is not instanteneous leading to cluster link creation failures
    print ('Sleeping 15s to allow the topic deletions to complete, before cluster link creation' )
    time.sleep(15)

    #-- Create the clusterlink primary -> secondary in secondary, with the list of mirror topics from step#1
    #-- Create the clusterlink in secondary before deleting in primary (this link has no mirror), so the mirror topic list is not lost
    print ('======== ' + operation.upper() + ' -CREATING CLUSTERLINK ' + link_id + ' IN SECONDARY')
    rest_url=cluster_info['secondary']['rest_url'] 
    header=cluster_info['secondary']['header']
    cluster_id=cluster_info['secondary']['cluster_id']

    source_cluster_id=cluster_info['primary']['cluster_id']
    source_bootstrap_server=cluster_info['primary']['bootstrap_server']
    source_api_key=cluster_info['primary']['api_key'] 
    source_api_secret=cluster_info['primary']['api_secret'] 

    if len(topic_list) == 0:
        topic_filters=None
    else:
        topic_filters={}
        acmt_configs=[]
        for topic in topic_list:
            acmt_configs.append({ 'name' : topic, 'patternType' : 'LITERAL', 'filterType' : 'INCLUDE'})
        topic_filters[ 'topicFilters' ]= acmt_configs

    res=clusterlink_create( rest_url, header, cluster_id, link_id, source_cluster_id, source_bootstrap_server, source_api_key, source_api_secret, topic_filters)
    if (res.status_code != 200 and res.status_code != 201):
        #{"error_code":400,"message":"A cluster link already exists with the provided link name: Unable to validate cluster link due to error: Cluster link 'cl-test-ps' already exists."}
        #{"error_code":40002,"message":"The server experienced an unexpected error when processing the request."}
        if res.status_code == 400 and json.loads(res.text)['message'].startswith("A cluster link already exists"):
            choice = input('Do you want to continue (y/n): ')
            if choice not in {'y','Y'}:
                exit()
        else:
            exit()
    
    #-- Delete the clusterlink secondary -> primary in primary
    print ('======== ' + operation.upper() + ' -DELETING CLUSTERLINK ' + link_id + ' IN PRIMARY')
    rest_url=cluster_info['primary']['rest_url']
    header=cluster_info['primary']['header']
    cluster_id=cluster_info['primary']['cluster_id']

    with suppress_stdout():
        res=clusterlink_delete (rest_url, header, cluster_id, link_id, op_type)     #-- op_type of 'validate_only' will not delete the cluster, use 'force'

    if (res.status_code < 300):   # 200, 201, 204
        print ('SUCCESS: Deleted the Cluster link ' + link_id + ' in primary site')
    elif res.status_code == 404:
        print ('SUCCESS: Cluster link ' + link_id + ' does not exist')
    else:
        print ('ERROR: ' + str(res.status_code) + str(res.text))

'''
-----------------------------------------------------------------------------------------------------------
failover function performs the following tasks
    1. promote/failover the topics in secondary
    2. insert event in traffic-router for producer/consumer to switch to secondary
-----------------------------------------------------------------------------------------------------------
'''
def failover( cluster_info, operation, op_type):

    #-- Check for ACTIVE clusterlink in secondary cluster (primary -> secondary) before promoting topics in secondary cluster
    print ('======== ' + operation.upper() + ' -VALIDATE CLUSTER LINK')
    link_id= cluster_info['link_id']

    rest_url=cluster_info['secondary']['rest_url'] 
    header=cluster_info['secondary']['header']
    cluster_id=cluster_info['secondary']['cluster_id']

    logging.debug ('cluster config: rest_url: ' + rest_url + ', cluster_id: ' + cluster_id)
    res=clusterlink_list (rest_url, header, cluster_id)
    if res.status_code == 200:
        cl_o=json.loads(res.text)['data']
        cluster=json.loads(res.text)['metadata']['self'].split('/')[-2]
        num_cls=len(cl_o)
        active_cluster_links=0
        mirror_topic_list=[]
        for x in range(num_cls):
            clusterlink_name=cl_o[x]['link_name']
            clusterlink_state=cl_o[x]['link_state']
            mirror_topic_list=cl_o[x]['topic_names']
            if clusterlink_state == 'ACTIVE':
                active_cluster_links+=1
        print ('Total ClusterLinks :' + str(num_cls) + ' Active ClusterLInks :' + str(active_cluster_links))
        if active_cluster_links == 0:
            print ('No active clusterlink mirroring topics found - NOT consistent state for failover to secondary')
            exit()
    else:
        print (json.loads(res.text)['message'])
        exit()

    #-- exit if the request is validate_only
    if op_type == 'validate_only':
        print ('======== ' + operation.upper() + ' -VALIDATE ONLY')
        print ('Valid cluster link for FAILOVER')
        print ('There are '+ str(len(mirror_topic_list)) + ' mirrored topic(s) in ' + clusterlink_name + ' cluster link')
        exit()

    #-- promote/failover the mirror topics in secondary ( failover prefered in DR - doesnt wait for lag to become 0, promote during migration - waits for lag to become 0)
    print ('======== ' + operation.upper() + ' - MIRROR TOPICS')
    if len(mirror_topic_list) > 0:
        failover_type='failover'     # failover/promote #TODO dont hardcode
        #mirror_topic_list=None      # None= all topics, or pass an array of topics for specific topics
        print ('Promoting the following mirror topics : ' + str(mirror_topic_list))
        #with suppress_stdout():
        res=mirror_topic_operations( rest_url, header, cluster_id, link_id, mirror_topic_list, failover_type)

        print (json.dumps(json.loads(res.text),indent=2))
        if res.status_code > 299:    # 200, 201
            exit()
    else:
        print (link_id + ' has NO mirrored topics. mirror topic failover is already done or Empty clusterlink. Link will be deleted as part of prep_failback')

    #-- insert  event in traffic-router for producer/consumer to switch to secondary
    print ('======== ' + operation.upper() + ' -INSERT A EVENT IN TRAFFIC-ROUTER TOPIC TO TRIGGER A SWITCH TO SECONDARY SITE')

    tr_topic=os.getenv("KAFKA_TOPICS_TRAFFIC_ROUTER").split(",") or sys.exit('KAFKA_TOPICS_TRAFFIC_ROUTER not exported')
    traffic_group_id=os.getenv("KAFKA_TRAFFIC_GROUP_DR_ID") or sys.exit('KAFKA_TRAFFIC_GROUP_DR_ID not exported')
    traffic_group_instance_id=os.getenv("KAFKA_TRAFFIC_GROUP_INSTANCE_ID") or sys.exit('KAFKA_TRAFFIC_GROUP_INSTANCE_ID not exported')
    switch_site='secondary'

    trp=TrafficRouterProducer(tr_topic, traffic_group_id, traffic_group_instance_id, switch_site)
    trp.produce()
    trp.flush()

'''
-----------------------------------------------------------------------------------------------------------
prep_failback function perfroms the following tasks
    1. Get the list of mirror topics from clusterlink in secondary, these will be in STOPPED state
    2. Delete the list of topics from step#1 in primary
    3. Delete the clusterlink primary -> secondary in secondary (old destination)
    4. Create the clusterlink secondary -> primary in primary, with the list of mirror topics from step#1   (new destination)
-----------------------------------------------------------------------------------------------------------
'''
def prep_failback( cluster_info, operation, op_type):

    #-- Get the mirror topics from secondary cluster
    print ('======== ' + operation.upper() + ' -IDENTIFY MIRROR TOPICS')
    link_id= cluster_info['link_id']

    rest_url=cluster_info['secondary']['rest_url'] 
    header=cluster_info['secondary']['header']
    cluster_id=cluster_info['secondary']['cluster_id']

    mirror_status=None  #-- None for All statuses (active, failed, paused, stopped, pending_stopped)
    with suppress_stdout():
        res=mirror_topic_list( rest_url, header, cluster_id, link_id, mirror_status)
    topic_list={}
    if res.status_code == 200:
        mt_o=json.loads(res.text)['data']
        num_topics=len(mt_o)
        logging.debug ('topics to mirror : ' + str(num_topics))
        active_mirror_topics=0
        for x in range(num_topics):
            mirror_topic_name=mt_o[x]['mirror_topic_name']
            source_topic_name=mt_o[x]['source_topic_name']
            mirror_status=mt_o[x]['mirror_status']
            topic_list[mirror_topic_name]=mirror_status
            if mirror_status == 'ACTIVE':       #--- All mirror topics should be in STOPPED state during this phase of DR
                active_mirror_topics+=1
        print ('Total Topics :' + str(num_topics) + ' Active Topics :' + str(active_mirror_topics))
        if active_mirror_topics > 0:
            print ('ERROR: Cluster link cannot be deleted when ACTIVE mirror topics found in the cluster link')
            exit()
    else:
        print (json.loads(res.text)['message'])
        exit()

    #-- Delete the list of topics in primary
    if op_type == 'validate_only':
        print ('not deleting the topics in primary for operation:validate_only')
    else:
        print ('======== ' + operation.upper() + ' -DELETING TOPICS IN PRIMARY')
        rest_url=cluster_info['primary']['rest_url'] 
        header=cluster_info['primary']['header']
        cluster_id=cluster_info['primary']['cluster_id']

        if len(topic_list) > 0:
            for topic in topic_list:
                mirror_topic_delete( rest_url, header, cluster_id, link_id, topic)
        else:
            print ('Topics already deleted or not found in primary')

    #-- sleep before creating the clusterlink as the topic deletion is not instanteneous leading to cluster link creation failures
    print ('Sleeping 10s to allow the topic deletions to complete, before cluster link creation' )
    time.sleep(10)

    #-- Create the clusterlink secondary -> primary in primary, with the list of mirror topics from step#1
    #-- Create the clusterlink in primary before deleting in secondary(this link has no mirror), so the mirror topic list is not lost
    print ('======== ' + operation.upper() + ' -CREATING CLUSTERLINK ' + link_id + ' IN PRIMARY')
    rest_url=cluster_info['primary']['rest_url'] 
    header=cluster_info['primary']['header']
    cluster_id=cluster_info['primary']['cluster_id']

    source_cluster_id=cluster_info['secondary']['cluster_id'] 
    source_bootstrap_server=cluster_info['secondary']['bootstrap_server'] 
    source_api_key=cluster_info['secondary']['api_key'] 
    source_api_secret=cluster_info['secondary']['api_secret'] 

    if len(topic_list) == 0:
        topic_filters=None
    else:
        topic_filters={}
        acmt_configs=[]
        for topic in topic_list:
            acmt_configs.append({ 'name' : topic, 'patternType' : 'LITERAL', 'filterType' : 'INCLUDE'})
        topic_filters[ 'topicFilters' ]= acmt_configs

    res=clusterlink_create( rest_url, header, cluster_id, link_id, source_cluster_id, source_bootstrap_server, source_api_key, source_api_secret, topic_filters)
    if (res.status_code != 200 and res.status_code != 201):
        #{"error_code":400,"message":"A cluster link already exists with the provided link name: Unable to validate cluster link due to error: Cluster link 'cl-test-ps' already exists."}
        #{"error_code":40002,"message":"The server experienced an unexpected error when processing the request."}
        if res.status_code == 400 and json.loads(res.text)['message'].startswith("A cluster link already exists"):
            choice = input('Do you want to continue (y/n): ')
            if choice not in {'y','Y'}:
                exit()
        else:
            exit()

    #-- Delete the clusterlink primary -> secondary in secondary
    print ('======== ' + operation.upper() + ' -DELETING CLUSTERLINK ' + link_id + ' IN SECONDARY')
    rest_url=cluster_info['secondary']['rest_url'] 
    header=cluster_info['secondary']['header']
    cluster_id=cluster_info['secondary']['cluster_id']

    with suppress_stdout():
        res=clusterlink_delete (rest_url, header, cluster_id, link_id, op_type)     #-- op_type of 'validate_only' will not delete the cluster, use 'force'

    if (res.status_code < 300):   # 200, 201, 204
        print ('SUCCESS: Deleted the Cluster link ' + link_id + ' in secondary site')
    elif res.status_code == 404:
        print ('SUCCESS: Cluster link ' + link_id + ' does not exist')
    else:
        print ('ERROR: ' + str(res.status_code) + str(res.text))


'''
-----------------------------------------------------------------------------------------------------------
failback function performs the following tasks
    1. promote/failover the topics in primary
    2. insert event in traffic-router for producer/consumer to switch to primary
-----------------------------------------------------------------------------------------------------------
'''
def failback( cluster_info, operation, op_type):

    #-- Check for ACTIVE clusterlink in primary cluster (secondary -> primary) before promoting topics in primary cluster
    print ('======== ' + operation.upper() + ' -VALIDATE CLUSTER LINK')
    link_id= cluster_info['link_id']

    rest_url=cluster_info['primary']['rest_url'] 
    header=cluster_info['primary']['header']
    cluster_id=cluster_info['primary']['cluster_id']

    logging.debug ('cluster config: rest_url: ' + rest_url + ', cluster_id: ' + cluster_id)
    res=clusterlink_list (rest_url, header, cluster_id)
    if res.status_code == 200:
        cl_o=json.loads(res.text)['data']
        cluster=json.loads(res.text)['metadata']['self'].split('/')[-2]
        num_cls=len(cl_o)
        active_cluster_links=0
        mirror_topic_list=[]
        for x in range(num_cls):
            clusterlink_name=cl_o[x]['link_name']
            clusterlink_state=cl_o[x]['link_state']
            mirror_topic_list=cl_o[x]['topic_names']
            if clusterlink_state == 'ACTIVE':
                active_cluster_links+=1
        print ('Total ClusterLinks :' + str(num_cls) + ' Active ClusterLInks :' + str(active_cluster_links))
        if active_cluster_links == 0:
            print ('No active clusterlink mirroring topics found - NOT consistent state for failback to primary')
            exit()
    else:
        print (json.loads(res.text)['message'])
        exit()

    #-- exit if the request is validate_only
    if op_type == 'validate_only':
        print ('======== ' + operation.upper() + ' -VALIDATE ONLY')
        print ('Valid cluster link for FAILOVER')
        print ('There are '+ str(len(mirror_topic_list)) + ' mirrored topic(s) in ' + clusterlink_name + ' cluster link')
        exit()

    #-- promote/failover the mirror topics in primary ( failover prefered in DR - doesnt wait for lag to 0, promote during migration - waits for lag to 0)
    print ('======== ' + operation.upper() + ' -FAILOVER / PROMOTE')
    if len(mirror_topic_list) > 0:
        failover_type='failover'     # failover/promote #TODO dont hardcode
        #mirror_topic_list=None              # None= all topics, can pass comma seperated list of topics
        print ('Promoting the following mirror topics : ' + str(mirror_topic_list))
        #with supress_stdout():
        res=mirror_topic_operations( rest_url, header, cluster_id, link_id, mirror_topic_list, failover_type)

        print (json.dumps(json.loads(res.text),indent=2))
        if res.status_code > 299:    # 200, 201
            exit()
    else:
        print (link_id + ' has NO mirrored topics. mirror topic failover is already done or Empty clusterlink. Link will be deleted as part of prep_failover')

    #-- insert  event in traffic-router for producer/consumer to switch to primary
    print ('======== ' + operation.upper() + ' -INSERT A EVENT IN TRAFFIC-ROUTER TOPIC TO TRIGGER A SWITCH TO PRIMARY SITE')

    tr_topic=os.getenv("KAFKA_TOPICS_TRAFFIC_ROUTER").split(",") or sys.exit('KAFKA_TOPICS_TRAFFIC_ROUTER not exported')
    traffic_group_id=os.getenv("KAFKA_TRAFFIC_GROUP_DR_ID") or sys.exit('KAFKA_TRAFFIC_GROUP_DR_ID not exported')
    traffic_group_instance_id=os.getenv("KAFKA_TRAFFIC_GROUP_INSTANCE_ID") or sys.exit('KAFKA_TRAFFIC_GROUP_INSTANCE_ID not exported')
    switch_site='primary'

    trp=TrafficRouterProducer(tr_topic, traffic_group_id, traffic_group_instance_id, switch_site)
    trp.produce()
    trp.flush()



if __name__ == '__main__':
    # Except for operation and op_type you must configure the rest in json configuration file.
    parser = argparse.ArgumentParser(description="Disaster Recovery Manager")
    parser.add_argument('-o', dest="operation", required=True, 
                        choices=['status','healthcheck', 'failover', 'failback', 'prep_failover', 'prep_failback'],
                        help="Operation e.g status, healthcheck, failover, failback or prepare for failover/failback")
    parser.add_argument('-t', dest="op_type", default='validate_only', 
                        choices=['force', 'validate_only'],
                        help="Use validate_only and verify before a force failover/failback")

    main(parser.parse_args())
