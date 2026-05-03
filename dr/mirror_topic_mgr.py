#!/usr/bin/env python
'''
@author     : Confluent Inc, Srinivas Sahu
Date        : 20231206
Usage       : mirror_topic_mgr.py
Dependency  : Cluster URL, APIKey, Secret
Description : A comprehensive tool to manage mirror topics during a DR event and normal times.
'''

import json
import base64
import logging
import requests
import argparse
from datetime import datetime 
from config_mgr import *

def main(args):
    rest_url = args.rest_url
    api_key = args.cluster_api_key
    api_secret = args.cluster_api_secret
    cluster_id = args.cluster_id
    cluster_link_id = args.link_id
    operation = args.operation
    mirror_status = args.mirror_status
    topic = args.topic
    site = args.site

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

    cluster_link_id = cluster_info['link_id'] if cluster_link_id is None else cluster_link_id
    rest_url = cluster_info[site]['rest_url'] if rest_url is None else rest_url
    api_key = cluster_info[site]['api_key'] if api_key is None else api_key
    api_secret = cluster_info[site]['api_secret'] if api_secret is None else api_secret
    cluster_id = cluster_info[site]['cluster_id'] if cluster_id is None else cluster_id

    logging.basicConfig(filename='topic_mgr_{:%Y%m%d}.log'.format(datetime.now()), format='%(asctime)s %(message)s', encoding='utf-8', level=logging.DEBUG)

    # Set up the headers with basic authentication
    api_auth = base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()
    headers = { 'Authorization': f"Basic {api_auth}" }

    if operation == 'create':
        #TODO: Enhance this to allow 1. specific mirror topic name 2. configuration changes, with validations.
        mirror_topic_create (rest_url, headers, cluster_id, cluster_link_id, topic) 
    elif operation == 'describe':
        mirror_topic_describe (rest_url, headers, cluster_id, cluster_link_id, topic) 
    elif operation == 'list':
        mirror_topic_list (rest_url, headers, cluster_id, cluster_link_id, mirror_status) 
    elif operation == 'lag':
        mirror_topic_lag (rest_url, headers, cluster_id, cluster_link_id, topic) 
    elif operation in {'promote', 'failover', 'pause', 'resume', 'delete'}:
        print ('!!!!!!!!!! This operation ' + operation.upper() + ' can break the data pipeline !!!!!!!')
        choice = input('Do you want to continue (y/n): ')
        if choice not in {'y','Y'}:
            exit()
        if operation == 'delete':
            print ('!!!!!!!!!! If you are deleting a mirror topic, delete the source topic first !!!!!!!')
            choice = ''
            choice = input('Do you want to continue (y/n): ')
            if choice not in {'y','Y'}:
                exit()
            mirror_topic_delete (rest_url, headers, cluster_id, cluster_link_id, topic) 
        else:
            #TODO: Enhance this to allow 1. speicific mirror topic name/list 2. Topic Pattern, with validations.
            mirror_topic_operations (rest_url, headers, cluster_id, cluster_link_id, topic, operation) 
   

'''
-------------------------------------------------------------------------
Create a mirror topic
------------------------------------------------------------------------- 
'''
def mirror_topic_create( rest_url, headers, cluster_id, cluster_link_id, source_topic):
   
    url= rest_url + "/kafka/v3/clusters/" + cluster_id + "/links/" + cluster_link_id + "/mirrors" 
    params = {'source_topic_name': source_topic }
    body=params 

    logging.debug ('url:' + url)
    res=requests.post(url, params=params, json=body, headers=headers)
    
    logging.info(f"{res.status_code}: {res.text}")
    if (res.status_code == 200 or res.status_code == 201):
        try: 
            print (json.dumps(json.loads(res.text),indent=2)) 
        except ValueError:
            print ('SUCCESS HTTP:' + str(res.status_code))
    else:
        print ('ERROR HTTP:' + str(res.text))

'''
-------------------------------------------------------------------------
Describe a mirror topic
------------------------------------------------------------------------- 
'''
def mirror_topic_describe( rest_url, headers, cluster_id, cluster_link_id, mirror_topic):
   
    url= rest_url + "/kafka/v3/clusters/" + cluster_id + "/links/" + cluster_link_id + "/mirrors/" + mirror_topic

    logging.debug ('url:' + url)
    res=requests.get(url, headers=headers)
    
    logging.info(f"{res.status_code}: {res.text}")
    if (res.status_code == 200):
        print (json.dumps(json.loads(res.text),indent=2))
    else:
        print ('HTTP:' + str(res.status_code) + str(res.text))
    
    return res

'''
-------------------------------------------------------------------------
Lists all the mirror topics in a cluster link id
------------------------------------------------------------------------- 
'''
def mirror_topic_list( rest_url, headers, cluster_id, cluster_link_id, mirror_status):
    if mirror_status is None:
        url= rest_url + "/kafka/v3/clusters/" + cluster_id + "/links/" + cluster_link_id + "/mirrors" 
    else:
        url= rest_url + "/kafka/v3/clusters/" + cluster_id + "/links/" + cluster_link_id + "/mirrors?mirror_status=" + mirror_status
    
    logging.debug ('url:' + url)
    res=requests.get(url, headers=headers)
    
    logging.info(f"{res.status_code}: {res.text}")
    if (res.status_code == 200):
        #print ('SUCCESS')
        print (json.dumps(json.loads(res.text),indent=2))
    else:
        print ('ERROR HTTP:' + str(res.status_code))

    return res
'''
-------------------------------------------------------------------------
Captures min and max lag along with the partition# of the topic requested
------------------------------------------------------------------------- 
'''
def mirror_topic_lag( rest_url, headers, cluster_id, cluster_link_id, topic):

        url= rest_url + "/kafka/v3/clusters/" + cluster_id + "/links/" + cluster_link_id + "/mirrors" 
        
        logging.debug ('url:' + url)
        res=requests.get(url, headers=headers)
        result={}
        if (res.status_code == 200):
            mt_o=json.loads(res.text)['data']
            num_topics=len(mt_o)
            for x in range(num_topics):
                mirror_topic_name=mt_o[x]['mirror_topic_name']
                if topic is None or mirror_topic_name in topic:
                    mirror_status=mt_o[x]['mirror_status']
                    num_partitions=len((mt_o)[x]['mirror_lags'])
                    minlag=99999999
                    maxlag=0
                    minpart = maxpart = None
                    for y in range(num_partitions):
                        partition=mt_o[x]['mirror_lags'][y]['partition']
                        lag=mt_o[x]['mirror_lags'][y]['lag']
                        if lag >= maxlag:
                            maxpart=partition
                            maxlag=lag
                        if lag <= minlag:
                            minpart=partition
                            minlag=lag
                    print ('topic:'+mirror_topic_name+' status:'+mirror_status+' partition#:'+str(num_partitions)+' minpart:'+str(minpart)+' minlag:'+str(minlag)+' maxpart:'+str(maxpart)+' maxlag:'+str(maxlag))
                    result[mirror_topic_name]=mirror_status+','+str(num_partitions)+','+str(minpart)+','+str(minlag)+','+str(maxpart)+','+str(maxlag)
        else:
            print ('ERROR HTTP:' + str(res.status_code))

        return result

'''
-------------------------------------------------------------------------
promote, failover, pause, resume a mirror topic 
------------------------------------------------------------------------- 
'''    
def mirror_topic_operations( rest_url, headers, cluster_id, cluster_link_id, topic_list, operation):
   
    url= rest_url + "/kafka/v3/clusters/" + cluster_id + "/links/" + cluster_link_id + "/mirrors:"+ operation  
    headers['Content-Type']= 'application/json'

    logging.debug ('url:' + url)
    if topic_list is None:    # All topics or Toppic Pattern
        params = {'mirror_topic_name_pattern': '.*'}
    else:                     # One or comma seperated list of topics
        if type(topic_list) is str:
            params = {'mirror_topic_names': [ topic_list ]}
        elif len(topic_list) > 0:       #-- when a array is passed
            params = {'mirror_topic_names': topic_list }
    
    body=params 
    res=requests.post(url, params=params, json=body, headers=headers)
    
    logging.info(f"{res.status_code}: {res.text}")
    if (res.status_code == 200 or res.status_code == 201):
        print (json.dumps(json.loads(res.text),indent=2))
    else:
        print ('ERROR HTTP:' + str(res.status_code) + str(res.text))

    return res

'''
-------------------------------------------------------------------------
Delete a mirror topic 
------------------------------------------------------------------------- 
''' 
def mirror_topic_delete( rest_url, headers, cluster_id, cluster_link_id, topic):

    #--Though cluster_link_id is not needed to delete the topic, it is used to check if this topic is part of cluster link
    response=mirror_topic_describe (rest_url, headers, cluster_id, cluster_link_id, topic)

    if response.status_code == 200 and json.loads(response.text)['mirror_status'] != 'STOPPED': # Promote/failover results in STOPPED status
        print ('This is a ' + json.loads(response.text)['mirror_status'] + ' mirror topic in cluster link '+ cluster_link_id + ' You should not delete this topic')
    elif response.status_code == 404 and not json.loads(response.text)['message'].startswith("The mirror topic doesn't exist:"):   # Not a mirror topic, safe to delete
        #-- HTTP:404{"error_code":404,"message":"The cluster link doesn't exist: "} - this error is ok, means the clusterlink does not exist
        #-- HTTP:404{"error_code":404,"message":"The mirror topic doesn't exist: "} - this error is NOT ok, means the topic does not exist
        url= rest_url + "/kafka/v3/clusters/" + cluster_id + "/topics/" + topic 
        headers['Content-Type']= 'application/json'

        logging.debug ('url:' + url)
        res=requests.delete(url, headers=headers)
        
        logging.info(f"{res.status_code}: {res.text}")
        if (res.status_code == 200 or res.status_code == 204):
            try:
                print (json.dumps(json.loads(res.text),indent=2))   #-- Empty body on 204
            except ValueError:
                print ('SUCCESS : Deleted Topic ' + topic ) 
        else:
            print ('ERROR HTTP:' + str(res.status_code) + str(res.text))
    else:     # No such topic
        print ('Topic NOT Found')        

if __name__ == '__main__':
    # Except for operation, topic and mirror_status you can pass the rest parameters in the configuration json file.
    parser = argparse.ArgumentParser(description="topic Manager example")
    parser.add_argument('-u', dest="rest_url",   help="Confluent Cloud cluster rest url:  (https://pkc-xxxx)")
    parser.add_argument('-k', dest="cluster_api_key",  help="Cloud API Key --resource cloud")
    parser.add_argument('-s', dest="cluster_api_secret",  help="Cloud API Secret --resource cloud")
    parser.add_argument('-c', dest="cluster_id",  help="Cluster ID e.g lkc-xxxx")
    parser.add_argument('-l', dest="link_id",  help="Link ID e.g name used when ClusterLink was created")
    parser.add_argument('-o', dest="operation", required=True, 
                        choices=['create', 'describe', 'list', 'lag', 'promote', 'failover', 'pause', 'resume', 'delete'],
                        help="Operation e.g create, describe, list, promote, failover, pause, resume")
    parser.add_argument('-m', dest="mirror_status", 
                        choices=['active', 'failed', 'paused', 'stopped', 'pending_stopped'],
                        help="Topic Mirror Status e.g active, failed, paused, stopped, pending_stopped")
    parser.add_argument('-t', dest="topic", help="Topic Name")
    parser.add_argument('-x', dest="site", default='secondary', choices=['primary', 'secondary'], help="Site Name")

    main(parser.parse_args())
