#!/usr/bin/env python3
#
# Smart producer built to meet the following requirements
# 1. During a DR event, should switch between primary & secondary sites with no restarts/config changes
# 2. RPO=0 Preferably No duplicates
# 3. RTO>0 Acceptable
# Uses a topic in secondary cluster as traffic router - An event in this topic triggers a switch to failover-secondary / failback-primary clusters.
#
# Dependencies:
# Kafka cluster configuration for primary & secondary
# Confluent Cloud REST API, cluster, clusterlink configuration for primary & secondary
# A datavolume to create a local cache (for k8s deployment)
#
# Updates:
# - Retrieving last event and monitoring traffic-router topic is modularized in topic_library - for resuability
# - Rewrite the code to do the poll in a background thread.
# - Improve the cache replay logic based on last event in the mirror topic from the inactive site
# 
#
import os
import json
import sys
import re
import logging
import threading
import time
import base64
import requests
from datetime import datetime
from confluent_kafka import Producer, Consumer, TopicPartition, KafkaException
from smartproducer_config import kafka_config_primary, kafka_config_secondary, cc_config_primary, cc_config_secondary
from victoria_metrics import KafkaMetricsReporter
from cache_mgr import CacheManager

class SmartProducer:

    from topic_library import topic_last_event, topic_last_event_by_ts, traffic_router_monitor

    def __init__ ( self, topics: list[str], traffic_group_id: str, traffic_group_instance_id: str, topics_tr: list[str], lag_group_id: str, lag_group_instance_id: str):

        #-- produce to this topic
        self.topics=topics
        #-- poll this this topic for failover/failback
        self.traffic_group_id=traffic_group_id
        self.traffic_group_instance_id=traffic_group_instance_id
        self.topics_tr=topics_tr
        #-- consume from topic on inactive site to determine the last event for cache_replay
        self.lag_group_id=lag_group_id
        self.lag_group_instance_id=lag_group_instance_id

        self.clientid='smartproducerv2'
        self.site=None
        self.prev_site=None
        self.switch_msg=None
        self.tr_thread_name='traffic_router'
        self.vm_thread_name='producer_vm'
        self.poll_thread_name='producer_poll'
        self.poll_cancel = False
        self.poll_sleeptime = 0.5
        self.poll_timeout = 0.1
        self.sleeptime=30
        self.log_ts=None
        self.cache_dir="/home/ubuntu/customer/openai/python/producer"
        self.cache_fd=None
        self.cache_delimeter='|'

        #--- Define logger before instantiating other classes
        logger = logging.getLogger('producer')
        logging.basicConfig(filename='smartproducer_{:%Y%m%d}.log'.format(datetime.now()), 
                            format='%(asctime)-15s %(levelname)-8s %(message)s', 
                            encoding='utf-8', 
                            level=logging.DEBUG)
        handler = logging.StreamHandler()
        logger.addHandler(handler)

        #--- MetricsReporter
        self.kafka_vm_metrics=KafkaMetricsReporter()
        
        #--- CacheManager
        self.cache_mgr=CacheManager(self.cache_dir, self.cache_delimeter, self.topics)

        custom_producer_config = {                                  #-- kafka producer customization - tune for performance optimization. TODO: move this to a config file
            "batch.size": 102400,
            "compression.type": "zstd",
            "linger.ms": 100,
            "delivery.timeout.ms": 100000,
            "request.timeout.ms": 30000,
            "client.id": "SmartProducer"
        }
        #"debug": "broker,topic,msg"                                #-- include this line in the customer_producer_config to debug

        self.config_primary = {                                     #-- kafka producer config - primary
            **kafka_config_primary(),
            "stats_cb": self.stats_cb,
            **custom_producer_config
        }
        self.config_secondary = {                                   #-- kafka producer config - secondary
            **kafka_config_secondary(),
            "stats_cb": self.stats_cb,
            **custom_producer_config
        }
        self.consumer_config_primary = {                            #-- kafka consumer config - primary ( consume last event in inactive site - lag)
            **kafka_config_primary(),
            "group.id": self.lag_group_id,
            "group.instance.id": self.lag_group_instance_id,
            "auto.offset.reset": "latest",
            "enable.auto.offset.store": False,
            "stats_cb": self.stats_cb,
            "client.id": "SmartProducer_lagconsumer"
        }
        self.consumer_config_secondary = {                          #-- kafka consumer config - secondary ( consume last event in inactive site - lag)
            **kafka_config_secondary(),
            "group.id": self.lag_group_id,
            "group.instance.id": self.lag_group_instance_id,
            "auto.offset.reset": "latest",
            "enable.auto.offset.store": False,
            "stats_cb": self.stats_cb,
            "client.id": "SmartProducer_lagconsumer"
        }
        self.config_secondary_traffic = {                           #-- kafka consumer config - secondary (always secondary - to detect failover/failback)
            **kafka_config_secondary(),
            "group.id": self.traffic_group_id,
            "group.instance.id": self.traffic_group_instance_id,
            "auto.offset.reset": "latest",
            "enable.auto.offset.store": False,
            "stats_cb": self.stats_cb,
            "client.id": "SmartProducer_trconsumer"
        }
        self.cc_config_primary = { **cc_config_primary() }          #-- rest api config - primary
        self.cc_config_secondary = { **cc_config_secondary() }      #-- rest api config - secondary

        #--- check the traffic-router topic for the site to boot intially
        logging.debug ('MAIN - Check the site to produce ')
        event_msg = self.topic_last_event(self.config_secondary_traffic, topics_tr)
        if event_msg is not None:       #-- If No events found produce to primary site
            try:
                self.prev_site=self.site=json.loads(event_msg.value())['SITE']
            except (ValueError, TypeError, KeyError):
                logging.error ('Corrupt message ' + str(message) + ' in topic: ' + topics_tr )

        logging.debug ('MAIN - Initial site : ' + str(self.site) )

        #--- Monitor the traffic-router topic for any new events ( Ops team to insert a event to trigger a DR failover/failback)
        logging.debug ('MAIN - Launch daemon to monitor traffic_router')
        self.tr_thread = threading.Thread(name=self.tr_thread_name, target=self.traffic_router_monitor, args=(self.config_secondary_traffic, topics_tr), daemon=True)
        self.tr_thread.start()

        #--- VictoriaMetrics reporter  
        logging.debug ('MAIN - Launch daemon to report kafka client metrics to VictoriaMetrics')
        vm_thread = threading.Thread(name=self.vm_thread_name, target=self.kafka_vm_metrics.run, daemon=True)
        vm_thread.start()

        conf=self.config_primary
        if self.site == 'secondary':
            conf=self.config_secondary

        self.producer = Producer(**conf)
        self.poll_thread = threading.Thread(name=self.poll_thread_name, target=self._poll_loop)
        self.poll_thread.start()         #--- Start the background Poll


    '''
    ------------------------------------------------------------------------------------------
    Produce events to confluent cloud
    ------------------------------------------------------------------------------------------
    '''
    def produce(self, event):

        logging.debug ('MAIN ------- Produce --------')

        #--- Optional per-message delivery callback (triggered by poll() or flush())when a message has been successfully delivered or permanently failed delivery (after retries).
        def delivery_callback(err, msg):
            if err:
                sys.stderr.write('FAILURE:Delivery site[%s] : %s\n' % (self.site, err))
            else:
                #sys.stderr.write('SUCCESS:Delivery site[%s] topic[%s] partition[%d] offset[%d] timestamp[%s] value[%s]\n' % (self.site, msg.topic(), msg.partition(), msg.offset(), msg.timestamp(), msg.value()))
                sys.stderr.write('SUCCESS:Delivery site[%s] topic[%s] partition[%d] offset[%d] timestamp[%s]\n' % (self.site, msg.topic(), msg.partition(), msg.offset(), msg.timestamp()))

        site_change=None
        p=None

        try:
            if event is not None:
                site_change=False
                #--- Determine if we need to switch sites
                if self.site != self.prev_site:     #--- DR/Planned failover situation
                    logging.info ('MAIN - switch to site : ' + str(self.site) + ' after sleep seconds :' + str(self.sleeptime))
                    if self.site == 'primary':
                        conf=self.config_primary
                        consumer_conf=self.consumer_config_primary
                    elif self.site == 'secondary':
                        conf=self.config_secondary
                        consumer_conf=self.consumer_config_secondary
                    site_change=True
                    self.prev_site=self.site

                if site_change:
                    self.flush()                    #-- Close the previous site and stop the poll, before switching sites
                    self.producer = Producer(**conf)
                    self.poll_cancel = False
                    self.poll_thread = threading.Thread(name=self.poll_thread_name, target=self._poll_loop)
                    self.poll_thread.start()        #--- Start the background Poll
                    time.sleep(self.sleeptime)

                    #--- Check if the msgs in inactive site is behind(lag) cache. Replay events (that didnt make it via CL) from cache to inactive site before switching.
                    logging.debug ('MAIN - Switch to site[' + self.site + '], Get the last event from topic[' + ''.join(self.topics) + '] to determine lag')
                    last_msg = self.topic_last_event_by_ts(consumer_conf, self.topics)
                    if last_msg is not None:
                        logging.debug ('offset[' + str(last_msg.offset()) +']' + ' timestamp[' + str(last_msg.timestamp()) + ']')
                        logging.debug ('message Key[' + str(last_msg.key().decode('UTF-8')) + ']')
                        logging.debug ('message Value[' + str(last_msg.value().decode('UTF-8')) + ']')
                        self.cache_mgr.replay_cache(self.producer, self.site, ''.join(self.topics), last_msg)
                    else:
                        logging.debug ('This should never happen - If it happens just skip replaying cache')


                #--- Write Cache
                key, value = event.split(',', 1)
                epoch_ms=round(datetime.utcnow().timestamp() * 1000)    #-- This timestamp in cache is used to determine the records that need to re-produce to DR site.
                self.cache_mgr.write_cache(''.join(self.topics), epoch_ms, key.rstrip(), value.rstrip())

                #--- Produce event
                logging.debug ('MAIN - producing to : ' + str(self.site))
                try:
                    self.producer.produce(''.join(self.topics), value.rstrip(), key.rstrip(), timestamp=epoch_ms, callback=delivery_callback)  #-- override the broker timestamp
                except KafkaException as e:
                    logging.debug ('MAIN - producer.produce KafkaException: ' + str(e.args[0]))
                    sys.stderr.write ('MAIN - producer.produce KafkaException: ' + str(e.args[0]) + '\n')
                    exit()     #TODO: exit or continue when the broker rejects a message ???

                #-- Ensure traffic_router thread is alive
                if not self.tr_thread.is_alive():
                    logging.debug ('MAIN - traffic_router thread dead, starting now')
                    self.tr_thread.start()

        except BufferError:
            sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' % len(p))
            logging.error ('MAIN - Local producer queue is full')
        except KeyboardInterrupt:
            sys.stderr.write('Exit with Keyboard Interrupt\n')
            logging.error ('MAIN - Keyboard Interrupt')

    '''
    ------------------------------------------------------------------------------------------
    Poll - background thread
    ------------------------------------------------------------------------------------------
    '''
    def _poll_loop(self):
        logging.debug ('POLL_LOOP - BACKGROUND THREAD START')
        while not self.poll_cancel:
            logging.debug ('POLL_LOOP - loop ')
            self.producer.poll(self.poll_timeout)
            time.sleep(self.poll_sleeptime)  #-- Sleep between polls
        logging.debug ('POLL_LOOP - exit ')

    '''
    ------------------------------------------------------------------------------------------
    CleanUP
    ------------------------------------------------------------------------------------------
    '''
    def flush(self):
        logging.debug ('FLUSH - Flush produce buffer, cancel poll, flush cache')
        # Wait until all messages have been delivered
        sys.stderr.write('%% Waiting for %d deliveries\n' % len(self.producer))
        self.producer.flush()  #-- blocking
        self.poll_cancel = True
        self.poll_thread.join()
        if self.cache_fd is not None:
            self.cache_fd.close()

    '''
    ------------------------------------------------------------------------------------------
    Callback Method to report client statistics
    ------------------------------------------------------------------------------------------
    '''
    def stats_cb(self, stats_json_str):
        #logging.debug (json.dumps(json.loads(stats_json_str),indent=2))
        self.kafka_vm_metrics.report(self.clientid, stats_json_str)

    '''
    ------------------------------------------------------------------------------------------
     Method to get the lag on mirror topics
     This method is an alternative way to measure the lag. For future use only.
    ------------------------------------------------------------------------------------------
    '''
    def mirror_topic_lag( self, cc_config, topic: list[str]):

        rest_url=cc_config['cc.rest.url']
        cluster_id=cc_config['cc.cluster.id']
        clusterlink_id=cc_config['cc.clusterlink.id']
        api_key=cc_config['cc.api.key']
        api_secret=cc_config['cc.api.secret']
        logging.debug ('MIRROR_TOPIC_LAG - cluster_id:' + cluster_id + ' link_id:' + clusterlink_id)

        #--- Create the header with basic authentication string
        api_auth = base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()
        headers = { 'Authorization': f"Basic {api_auth}" }

        url= rest_url + "/kafka/v3/clusters/" + cluster_id + "/links/" + clusterlink_id + "/mirrors"

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
                    logging.debug ('topic:'+mirror_topic_name+' status:'+mirror_status+' partition#:'+str(num_partitions)+' minpart:'+str(minpart)+' minlag:'+str(minlag)+' maxpart:'+str(maxpart)+' maxlag:'+str(maxlag))
                    result[mirror_topic_name]=mirror_status+','+str(num_partitions)+','+str(minpart)+','+str(minlag)+','+str(maxpart)+','+str(maxlag)
        else:
            print ('ERROR HTTP:' + str(res.status_code))

        return result


if __name__ == "__main__":

    from random import randint

    logging.basicConfig

    #--- produce to this topic
    topics=os.environ["KAFKA_TOPICS"].split(",")
    #--- consume from this topic to monitor for traffic switch
    traffic_group_id=os.environ["KAFKA_TRAFFIC_GROUP_SP_ID"]
    traffic_group_instance_id=os.environ["KAFKA_TRAFFIC_GROUP_INSTANCE_ID"]
    topics_tr=os.environ["KAFKA_TOPICS_TRAFFIC_ROUTER"].split(",")
    #--- consume from this topic to retrieve the last event from mirror topic to identify the lag.
    lag_group_id=os.environ["KAFKA_LAG_GROUP_ID"]
    lag_group_instance_id=os.environ["KAFKA_LAG_GROUP_INSTANCE_ID"]

    try:
        sp=SmartProducer(topics, traffic_group_id, traffic_group_instance_id, topics_tr, lag_group_id, lag_group_instance_id)
        cnt=1
        run=randint(1, 100)
        while True:
            event=str(cnt) +',' + '{"FIELD1": "event' + str(cnt) + '_' + str(run) + ' - produce", "FIELD2": "bla", "FIELD3": "mock data from smart producer" }'
            sp.produce(event)
            cnt+=1
            time.sleep(1)
            if cnt > 50:
                break

        sp.flush()
    except KeyboardInterrupt:
        sys.stderr.write('Exit with Keyboard Interrupt\n')
