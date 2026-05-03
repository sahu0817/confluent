#!/usr/bin/env python
'''
@author     : Confluent Inc, Srinivas Sahu
Date        : 20231206
Usage e.g   : clusterlink_mgr.py -o list
            : clusterlink_mgr.py -o delete -l cl-test -d validation_only
Dependency  : Cluster URL, Destination cluster id, APIKey, Secret, Source cluster id, APIKey, Secret and bootstrap server
Description : A comprehensive tool to manage cluster links  during a DR event and normal times.
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
    source_cluster_id = args.source_cluster_id
    source_api_key = args.source_api_key
    source_api_secret = args.source_api_secret
    source_bootstrap_server = args.source_bootstrap_server
    cluster_link_id = args.link_id
    operation = args.operation
    delete_type = args.delete_type
    site = args.site

    #-- default cluster link in secondary  (primary -> secondary)
    source='primary'
    destination='secondary'
    if site == 'primary':    #-- cluster link in primary (primary <- secondary)
        source='secondary'
        destination='primary'

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

    #-- Destination cluster configuration
    cluster_link_id = cluster_info['link_id'] if cluster_link_id is None else cluster_link_id
    rest_url = cluster_info[destination]['rest_url'] if rest_url is None else rest_url
    api_key = cluster_info[destination]['api_key'] if api_key is None else api_key
    api_secret = cluster_info[destination]['api_secret'] if api_secret is None else api_secret
    cluster_id = cluster_info[destination]['cluster_id'] if cluster_id is None else cluster_id

    #-- Source cluster configuration
    source_cluster_id = cluster_info[source]['cluster_id'] if source_cluster_id is None else source_cluster_id
    source_api_key = cluster_info[source]['api_key'] if source_api_key is None else source_api_key
    source_api_secret = cluster_info[source]['api_secret'] if source_api_secret is None else source_api_secret
    source_bootstrap_server = cluster_info[source]['bootstrap_server'] if source_bootstrap_server is None else source_bootstrap_server
     
    logging.basicConfig(filename='clusterlink_mgr_{:%Y%m%d}.log'.format(datetime.now()), format='%(asctime)s %(message)s', encoding='utf-8', level=logging.DEBUG)

    #-- Set up the headers with basic authentication
    api_auth = base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()
    headers = { 'Authorization': f"Basic {api_auth}" }

    if operation == 'create':
        #TODO: Enhance this to allow 1. specific mirror topic name 2. configuration changes, with validations.
        clusterlink_create (rest_url, headers, cluster_id, cluster_link_id, source_cluster_id, source_bootstrap_server, source_api_key, source_api_secret, None) 
    elif operation == 'describe':
        clusterlink_describe (rest_url, headers, cluster_id, cluster_link_id) 
    elif operation == 'list':
        clusterlink_list (rest_url, headers, cluster_id) 
    elif operation == 'delete':
        if delete_type not in { 'force', 'validate_only'}:
            print ('Delete Type -d [force | validate_only] is mandatory for delete operation')
            exit()
        if delete_type == 'force':
            print ('!!!!!!!!!! This operation ' + operation.upper() + ' can break the data pipeline !!!!!!!')
            choice = input('Do you want to continue (y/n): ')
            if choice not in {'y','Y'}:
                exit()

        clusterlink_delete (rest_url, headers, cluster_id, cluster_link_id, delete_type) 
   

def clusterlink_create( rest_url, headers, cluster_id, cluster_link_id, source_cluster_id, source_bootstrap_server, source_api_key, source_api_secret, topic_filters):
   
    url= rest_url + "/kafka/v3/clusters/" + cluster_id + "/links/?link_name=" + cluster_link_id 
    params = {'source_cluster_id': source_cluster_id }
    configs = []
    configs.append({ 'name': 'bootstrap.servers', 'value': source_bootstrap_server })
    configs.append({ 'name': 'security.protocol', 'value': 'SASL_SSL' })
    configs.append({ 'name': 'sasl.mechanism', 'value': 'PLAIN' })
    sjc_value='org.apache.kafka.common.security.plain.PlainLoginModule required username="' + source_api_key + '" password="' + source_api_secret + '";'
    configs.append({ 'name': 'sasl.jaas.config', 'value':  sjc_value })
    configs.append({ 'name': 'acl.sync.enable', 'value': 'true' })
    configs.append({ 'name': 'consumer.offset.sync.enable', 'value': 'true' })
    configs.append({ 'name': 'consumer.offset.sync.ms', 'value': '5000' })
    configs.append({ 'name': 'auto.create.mirror.topics.enable', 'value': 'true' })
    if topic_filters is not None:
        configs.append({ 'name': 'auto.create.mirror.topics.filters', 'value': json.dumps(topic_filters)})

    params['configs']=configs
    body=params 

    logging.debug ('url:' + url)
    res=requests.post(url, params=params, json=body, headers=headers)
    
    logging.info(f"{res.status_code}: {res.text}")
    if (res.status_code == 200 or res.status_code == 201):
        try: 
            print (json.dumps(json.loads(res.text),indent=2)) 
        except ValueError:
            print ('SUCCESS: Cluster Link: ' + cluster_link_id + ' created')
    else:
        print ('ERROR: ' + str(res.status_code) + str(res.text))

    return res

def clusterlink_describe( rest_url, headers, cluster_id, cluster_link_id):
   
    url= rest_url + "/kafka/v3/clusters/" + cluster_id + "/links/" + cluster_link_id  

    logging.debug ('url:' + url)
    res=requests.get(url, headers=headers)
    
    logging.info(f"{res.status_code}: {res.text}")
    if (res.status_code == 200):
        print (json.dumps(json.loads(res.text),indent=2))
    else:
        print ('HTTP:' + str(res.status_code) + str(res.text))
    
    return res

def clusterlink_list( rest_url, headers, cluster_id):

    url= rest_url + "/kafka/v3/clusters/" + cluster_id + "/links" 

    logging.debug ('url:' + url)
    res=requests.get(url, headers=headers)
    
    logging.info(f"{res.status_code}: {res.text}")
    if (res.status_code == 200):
        print (json.dumps(json.loads(res.text),indent=2))
    else:
        print ('ERROR HTTP:' + str(res.status_code))

    return res

def clusterlink_delete( rest_url, headers, cluster_id, cluster_link_id, delete_type):
   
    url= rest_url + "/kafka/v3/clusters/" + cluster_id + "/links/" + cluster_link_id  
    headers['Content-Type']= 'application/json'

    if delete_type == 'force':
        params = { 'force' : True }
    elif delete_type == 'validate_only':
        params = { 'validate_only' : True }

    logging.debug ('url:' + url)
    res=requests.delete(url, params=params, headers=headers)
    
    logging.info(f"{res.status_code}: {res.text}")
    if (res.status_code < 300):   # 200, 201, 204
        try:
            print (json.dumps(json.loads(res.text),indent=2))
        except ValueError:
            print ('SUCCESS: Cluster Link: ' + cluster_link_id + ' deleted')
    else:
        print ('ERROR HTTP:' + str(res.status_code) + str(res.text))

    return res



if __name__ == '__main__':
    # Except for operation and delete_type you can pass the rest parameters in the configuration json file.
    parser = argparse.ArgumentParser(description="clusterlink Manager example")
    parser.add_argument('-u', dest="rest_url",   help="Confluent Cloud cluster rest url:  (https://pkc-xxxx)")
    parser.add_argument('-k', dest="cluster_api_key",  help="Destination Cluster API Key")
    parser.add_argument('-s', dest="cluster_api_secret",  help="Destination Cluster API Secret")
    parser.add_argument('-c', dest="cluster_id",  help="Cluster ID e.g lkc-xxxx")
    parser.add_argument('-l', dest="link_id",  help="Link ID e.g name used when ClusterLink was created")
    parser.add_argument('-g', dest="source_cluster_id",  help="Source Cluster ID e.g lkc-xxxx")
    parser.add_argument('-i', dest="source_api_key",  help="Source Cluster API_KEY ")
    parser.add_argument('-j', dest="source_api_secret",  help="Source Cluster API_SECRET ")
    parser.add_argument('-b', dest="source_bootstrap_server",  help="Source bootstrap server e.g pkc-xxxx:9092")
    parser.add_argument('-o', dest="operation", required=True, choices=['create', 'describe', 'list', 'delete'], help="Operation e.g create, describe, list, promote, failover, pause, resume")
    parser.add_argument('-d', dest="delete_type", choices=['force', 'validate_only'], help="Use validate_only and verify before a force delete")
    parser.add_argument('-x', dest="site", choices=['primary', 'secondary'], default='secondary', help="Use site to indicate destination cluster")

    main(parser.parse_args())
