#!/usr/bin/env python3
#
# Producer client to insert a event in traffic-router topic to trigger a failover/failback
#
# Dependencies:
# Kafka cluster configuration for primary & secondary
#
import os
import json
import sys
import logging
import time
import base64
import requests
import argparse
from datetime import datetime
from confluent_kafka import Producer, Consumer, TopicPartition, KafkaException
#from observer_kafka.producer.smartproducer_config import kafka_config_primary, kafka_config_secondary, cc_config_primary, cc_config_secondary
from config_mgr import kafka_config_primary, kafka_config_secondary, cluster_config_primary, cluster_config_secondary, clusterlink_config

class TrafficRouterProducer:

    def __init__ ( self, topics: list[str], traffic_group_id: str, traffic_group_instance_id: str, switch_site: str):

        #-- produce to this topic
        self.topics=topics

        self.traffic_group_id=traffic_group_id
        self.traffic_group_instance_id=traffic_group_instance_id

        self.switch_site=switch_site
        self.site=None

        if self.switch_site not in {'secondary','primary'}:
            logging.debug ('TRAFFICROUTERPRODUCER - Invalid site ' + self.switch_site)
            exit()

        #-- traffic-router producer
        self.config_secondary = { **kafka_config_secondary() }

        #-- traffic-router consumer
        self.config_secondary_traffic = {                         
            **kafka_config_secondary(),
            "group.id": self.traffic_group_id,
            "group.instance.id": self.traffic_group_instance_id,
            "auto.offset.reset": "latest",
            "enable.auto.offset.store": False,
        }
        #-- rest api config to retrieve mirror topic lag
        self.cc_config_primary = { 
                **cluster_config_primary(),
                **clusterlink_config()
        }
        self.cc_config_secondary = { 
                **cluster_config_secondary(),
                **clusterlink_config()
        }

        #--- Create logger for consumer (logs will be emitted when poll() is called)
        logger = logging.getLogger('producer')
        logging.basicConfig(filename='trafficrouter_producer_{:%Y%m%d}.log'.format(datetime.now()), format='%(asctime)-15s %(levelname)-8s %(message)s', encoding='utf-8', level=logging.DEBUG)
        #logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        #handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
        logger.addHandler(handler)

        #--- check the current site, based on last event in traffic-router topic
        logging.debug ('TRAFFICROUTERPRODUCER - Check the current site')
        event_msg = self.traffic_router_event(self.config_secondary_traffic, self.topics)
        if event_msg is not None:
            self.site = event_msg['SITE']
            if self.site == self.switch_site:
                print ('TRAFFICROUTERPRODUCER - Invalid switch request, Already at :' +   self.switch_site)
                logging.debug ('TRAFFICROUTERPRODUCER - Invalid switch request, Already at :' +   self.switch_site)
                exit()

        conf=self.config_secondary
        self.producer = Producer(**conf)

    '''
    ------------------------------------------------------------------------------------------
     Method to produce event to traffic-router topic
    ------------------------------------------------------------------------------------------
    '''
    def produce(self):

        logging.debug ('TRAFFICROUTERPRODUCER - Produce ')

        #--- Optional per-message delivery callback (triggered by poll() or flush())when a message has been successfully delivered or permanently
        #--- failed delivery (after retries).
        def delivery_callback(err, msg):
            if err:
                sys.stderr.write('%% Message failed delivery: %s\n' % err)
            else:
                sys.stderr.write('%% Message delivered to %s %s [%d] @ %d, value: %s, timestamp: %s\n' % (self.site, msg.topic(), msg.partition(), msg.offset(), msg.value(), msg.timestamp()))

        p=None
        now=datetime.now().strftime('%Y%m%d%H%M%S')

        try:
            logging.info ('TRAFFICROUTERPRODUCER - switch to site (sleep10): ' + str(self.switch_site))
            if self.switch_site == 'primary':
                event=str(now) +',' + '{"EVENT": "switch site", "LAG": "N/A", "SITE": "primary" }'
            elif self.switch_site == 'secondary':
                event=str(now) +',' + '{"EVENT": "switch site", "LAG": "N/A", "SITE": "secondary" }'

            #--- Check Lag
            cc_conf=self.cc_config_primary
            if self.site == 'primary' or self.site is None:              #-- cluster link is present in the destination site
                cc_conf=self.cc_config_secondary
            result=self.mirror_topic_lag(cc_conf, None)
            #print ('result:' + str(result))
            #TODO: Add LAG information if available, when source cluster is down LAG is always 0

            #--- Produce event
            logging.debug ('TRAFFICROUTERPRODUCER - producing switch event to : ' + str(self.switch_site))
            key, value = event.split(',', 1)
            self.producer.produce(''.join(self.topics), value.rstrip(), key.rstrip(), callback=delivery_callback)

            # Serve delivery callback queue.  NOTE: Since produce() is an asynchronous API this poll() call  will most likely
            # not serve the delivery callback for the last produce()d message.
            self.producer.poll(0) #-- nonblocking

        except BufferError:
            sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' % len(p))
        except KeyboardInterrupt:
            sys.stderr.write('Exit with Keyboard Interrupt\n')

    '''
    ------------------------------------------------------------------------------------------
     Method to retrieve the last event in traffic-router topic
    ------------------------------------------------------------------------------------------
    '''
    def traffic_router_event(self, config_secondary_traffic, topic_tr):

        logging.debug ('TRAFFIC_ROUTER   ')
        #def stats_cb(stats_json_str):
        #    stats_json = json.loads(stats_json_str)
        #    print('\nKAFKA Stats: {}\n'.format(pformat(stats_json)))

        def print_assignment(consumer, partitions):
            print('Assignment:', partitions)

        logger = logging.getLogger('producer')
        logging.debug ('TRAFFIC_ROUTER - Seek the last event in traffic-router topic')
        c_secondary = Consumer(config_secondary_traffic, logger=logger)
        partition_tr=0
        topic_partition= TopicPartition(''.join(topic_tr), partition_tr)
        low,high = c_secondary.get_watermark_offsets(topic_partition)
        if low == high == 0:        #-- Empty topic
            logging.debug ('TRAFFIC_ROUTER - No events (Day1), start with primary site')
            c_secondary.close()
            return None
        partition = TopicPartition(''.join(topic_tr), partition_tr, high-1)
        c_secondary.assign([partition])
        c_secondary.seek(partition)
        msg = c_secondary.poll(timeout=1.0)
        if msg is None:             #-- topic with a high watermark but events are deleted due to retention period
            c_secondary.close()
            logging.debug ('TRAFFIC_ROUTER - No events (due to retention period ???), goto primary site')
            return None
        try:
            message=msg.value().decode('UTF-8')
            logging.debug ('TRAFFIC_ROUTER - Last event : ' + str(msg.partition()) + ' ' + str(msg.offset()) + ' ' + str(msg.value()))
            event_msg=json.loads(message)
            site = event_msg['SITE']
            c_secondary.close()
            return event_msg
        except (ValueError, TypeError, KeyError):
            logging.debug ('TRAFFIC_ROUTER - Corrupt message ' + str(message))
            c_secondary.close()
            return None

    '''
    ------------------------------------------------------------------------------------------
     Method to flush any events in the buffer
    ------------------------------------------------------------------------------------------
    '''
    def flush(self):
        logging.debug ('FLUSH - finally')
        # Wait until all messages have been delivered
        sys.stderr.write('%% Waiting for %d deliveries\n' % len(self.producer))
        self.producer.flush()  #-- blocking

    '''
    ------------------------------------------------------------------------------------------
     Method to get the lag on mirror topics
    ------------------------------------------------------------------------------------------
    '''
    def mirror_topic_lag( self, cc_config, topic: list[str]):

        rest_url=cc_config['rest_url']
        cluster_id=cc_config['cluster_id']
        clusterlink_id=cc_config['link_id']
        api_key=cc_config['api_key']
        api_secret=cc_config['api_secret']
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

    parser = argparse.ArgumentParser(description="Disaster Recovery Manager")
    parser.add_argument('-s', dest="site", required=True,
                        choices=['primary', 'secondary'],
                        help="Site to switch")

    switch_site = parser.parse_args().site

    logging.basicConfig

    #--- produce to this topic
    tr_topic=os.environ["KAFKA_TOPICS_TRAFFIC_ROUTER"].split(",")

    #--- consume from this topic to get the last site
    traffic_group_id=os.environ["KAFKA_TRAFFIC_GROUP_DR_ID"]
    traffic_group_instance_id=os.environ["KAFKA_TRAFFIC_GROUP_INSTANCE_ID"]

    try:
        trp=TrafficRouterProducer(tr_topic, traffic_group_id, traffic_group_instance_id, switch_site)
        trp.produce()
        trp.flush()
    except KeyboardInterrupt:
        sys.stderr.write('Exit with Keyboard Interrupt\n')
