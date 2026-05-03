#!/usr/bin/env python3
#
# A helper library to do the following
# 1. Monitor traffic-router topic to look for failover/failback events and inform the main thread
# 2. Retrieve the last produced event of a topic  
#    a. to determine the site to boot for producer/consumer 
#    b. to determine the last event of a topic in DR site to identify the events that need to be replayed from cache
#
# Dependencies:
# Kafka cluster configuration for primary & secondary
#
#
import os
import json
import sys
import logging
import time
from datetime import datetime
from confluent_kafka import Producer, Consumer, TopicPartition, KafkaException
from confluent_kafka.admin import AdminClient
'''
-------------------------------------------------------------------------------------------------------
 Method to retrieve the last event produced to a topic by offset. Works well for single partition topic
-------------------------------------------------------------------------------------------------------
'''
def topic_last_event(self, conf, topic):
    logging.debug ('TOPIC_LAST_EVENT')

    try:
        kafka_admin = AdminClient(conf)
        x = kafka_admin.list_topics(topic=''.join(topic), timeout=10)
        pcount=0
        for key, value in x.topics.items():
            pcount=len( list(value.partitions.items()))
    except KafkaException as e:
        logging.debug ('TOPIC_LAST_EVENT - AdminClient.list_topics KafkaException: ' + str(e.args[0]))
        sys.stderr.write ('TOPIC_LAST_EVENT - AdminClient.list_topics KafkaException: ' + str(e.args[0]) + '\n')
        exit(1)

    if pcount == 0:
        logging.debug (' TOPIC_LAST_EVENT - No topic found: Wrong topic name or cluster config')
        sys.stderr.write (' TOPIC_LAST_EVENT - No topic found: Wrong topic name or cluster config')
        exit(1)

    logging.debug ('TOPIC_LAST_EVENT - partition count:' + str(pcount))
    c = Consumer(conf)
    partition = None
    offset = 0
    for partition_num in range(pcount):
        topic_partition= TopicPartition(''.join(topic), partition_num)
        low,high = c.get_watermark_offsets(topic_partition)

        if high >= offset:
            offset=high
            partition=partition_num

    logging.debug ('TOPIC_LAST_EVENT - last msg partition:' + str(partition) + ' offset:' + str(offset-1))
    tpartition = TopicPartition(''.join(topic), partition, offset-1)
    c.assign([tpartition])
    c.seek(tpartition)
    msg = c.poll(timeout=1.0)
    if msg is None:             #-- topic with a high watermark but events are deleted due to retention period
        logging.debug ('TOPIC_LAST_EVENT - Empty topic OR a high watermark but events are deleted due to retention period')
        c.close()
        return None
    try:
        c.close()
        return msg
    except (ValueError, TypeError, KeyError):
        c.close()
        return None

'''
-------------------------------------------------------------------------------------------------------------------------------
 Method to retrieve the last event produced to a topic based on message timestamp. Use this for topics with multiple partitions.
-------------------------------------------------------------------------------------------------------------------------------
'''
def topic_last_event_by_ts (self, conf, topic):

    logging.debug ('TOPIC_LAST_EVENT_BY_TS')
    #This approach works only if msgs are perfectly round robin across partitions
    try:
        kafka_admin = AdminClient(conf)
        x = kafka_admin.list_topics(topic=''.join(topic), timeout=10)
        pcount=0
        for key, value in x.topics.items():    
            pcount=len( list(value.partitions.items()))  
    except KafkaException as e:
        logging.debug ('TOPIC_LAST_EVENT_BY_TS - AdminClient.list_topics KafkaException: ' + str(e.args[0]))
        sys.stderr.write ('TOPIC_LAST_EVENT_BY_TS - AdminClient.list_topics KafkaException: ' + str(e.args[0]) + '\n')
        exit(1)

    logging.debug ( 'TOPIC_LAST_EVENT_BY_TS - partition count : ' + str(pcount))

    if pcount == 0:             #-- No partitions found / wrong topic name
        logging.debug ( 'TOPIC_LAST_EVENT_BY_TS - No partitions found, Check the config & topic name')
        return None

    #-- instantiate for each partition in the loop.
    #-- Consumer poll is not reliable when switching partitions: cimpl.KafkaException: KafkaError{code=_STATE,val=-172,str="Failed to seek to offset 78: Local: Erroneous state"}
    #c = Consumer(conf)
    partition = None
    latest_ts = 0
    for partition_num in range(pcount):
        c = Consumer(conf)
        topic_partition= TopicPartition(''.join(topic), partition_num)
        low,high = c.get_watermark_offsets(topic_partition)
        offset=high-1
        logging.debug ('TOPIC_LAST_EVENT_BY_TS - partition_num : ' + str(partition_num) + ' low : ' +  str(low) + ' offset:' + str(offset))
        tpartition = TopicPartition(''.join(topic), partition_num, offset)
        c.assign([tpartition])
        c.seek(tpartition)
        msg = c.poll(timeout=1.0)
        if msg is None:             #-- topic with a high watermark but events are deleted due to retention period
            logging.debug ('TOPIC_LAST_EVENT_BY_TS - topic with a high watermark but events are deleted due to retention period')
        try:
            msg_offset=str(msg.offset())
            (bla, msg_ts)=msg.timestamp()
            msg_key=str(msg.key().decode('UTF-8'))
            msg_value=str(msg.value().decode('UTF-8'))
            logging.debug ('ts: ' + str(msg_ts) + ' offset:' + msg_offset + ' key:' + msg_key + ' value:' + msg_value)
            if msg_ts > latest_ts:
                logging.debug ('LATEST ts: ' + str(msg_ts) + ' offset:' + msg_offset + ' key:' + msg_key + ' value:' + msg_value)
                latest_ts=msg_ts
                latest_msg=msg
        except (ValueError, TypeError, KeyError):
            logging.debug ('TOPIC_LAST_EVENT_BY_TS - Error' )
            c.close()
            return None
        c.close()

    return latest_msg

'''
----------------------------------------------------------------------------------------------------
 Method to monitor traffic-router topic and the switch the site based a event produced to this topic
----------------------------------------------------------------------------------------------------
'''
def traffic_router_monitor(self, config_secondary_traffic, topic_tr):

    logging.debug ('TRAFFIC_ROUTER_MONITOR ')

    def print_assignment(consumer, partitions):
        print('Assignment:', partitions)

    logger = logging.getLogger('consumer')
    try:
        c_secondary = Consumer(config_secondary_traffic, logger=logger)
        c_secondary.subscribe(topic_tr, on_assign=print_assignment)
    except KafkaException as e:
        logging.debug ('TRAFFIC_ROUTER_MONITOR - Consumer.subscribe KafkaException: ' + str(e.args[0]))
        sys.stderr.write ('TRAFFIC_ROUTER_MONITOR - Consumer.subscribe KafkaException: ' + str(e.args[0]) + '\n')
        exit(1)

    # Read messages from Kafka, print to stdout
    try:
        prev_event=None
        while True:
            msg = c_secondary.poll(timeout=1.0)
            if msg is None:
                if prev_event is not None:
                    logging.debug ('TRAFFIC_ROUTER_MONITOR - Polling found event')
                    self.site = event_msg['SITE']
                    self.switch_msg=event
                    prev_event=None
                    #time.sleep(10)  #-- Do we need frequent polls to traffic-router topic. 10s is reasonable ???
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                # Proper message
                #'{ "EVENT":"yyyymmddhhmm","LAG":"10","SITE":"secondary"}'
                message=msg.value().decode('UTF-8')
                sys.stderr.write(' -- topic:%s partition:[%d] offset:%d key:%s \n' %(msg.topic(), msg.partition(), msg.offset(), str(msg.key())))
                if (prev_event != message):
                    try:
                        event_msg=json.loads(message)
                        event = event_msg['EVENT']
                        lag = event_msg['LAG']
                        logging.info ('TRAFFIC_ROUTER_MONITOR - Event:' + event + ' site:' + event_msg['SITE'])
                    except (ValueError, TypeError, KeyError):
                        logging.debug ('TRAFFIC_ROUTER_MONITOR - Corrupt Event')
                # Store the offset associated with msg to a local cache.
                # Stored offsets are committed to Kafka by a background thread every 'auto.commit.interval.ms'.
                # Explicitly storing offsets after processing gives at-least once semantics.
                c_secondary.store_offsets(msg)
                prev_event=message

    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')
    except KafkaException as e:
        logging.debug ('TRAFFIC_ROUTER_MONITOR - poll KafkaException: ' + str(e.args[0]))
        sys.stderr.write ('TRAFFIC_ROUTER_MONITOR - poll KafkaException: ' + str(e.args[0]) + '\n')
        exit(1)
    finally:
        # Close down consumer to commit final offsets.
        c_secondary.close()
