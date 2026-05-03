#!/usr/bin/env python
#
# Demo counsumer that can switch between primary(prod) & secondary(dr) clusters based on a message in a topic (traffic-router)
#
from confluent_kafka import Consumer, KafkaException
import sys
import getopt
import json
import logging
import threading
import time
import re
from pprint import pformat
from configs import CONF, TOPIC


def stats_cb(stats_json_str):
    stats_json = json.loads(stats_json_str)
    print('\nKAFKA Stats: {}\n'.format(pformat(stats_json)))

#------------------------------------------------------------------------------------------
# Main thread to consume from primary/secondary based on traffic router
#------------------------------------------------------------------------------------------
def main(conf_primary, conf_secondary):
    global switch_msg
    global site

    print (' MAIN ')

    #def stats_cb(stats_json_str):
    #    stats_json = json.loads(stats_json_str)
    #    print('\nKAFKA Stats: {}\n'.format(pformat(stats_json)))

    def print_assignment(consumer, partitions):
        #print('Assignment:', partitions)
        pass

    # Create logger for consumer (logs will be emitted when poll() is called)
    logger = logging.getLogger('consumer')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
    logger.addHandler(handler)

    topic_primary = TOPIC.get('PRIMARY')
    topic_secondary = TOPIC.get('SECONDARY')
    topic_traffic = TOPIC.get('TRAFFICROUTER')

    #=== This runs the thread_consume function in background and be able to read the count updated by the thread
    th = threading.Thread(name='traffic_router', target=traffic_router, args=(conf_secondary, topic_traffic))
    th.daemon = True
    th.start()

    switch_msg=None     #-- Global (updated by traffic_router thread)
    site=None           #-- Global (updated by traffic_router thread)
    prev_site=None

    try:
        while True:
            print (' MAIN: prev_site: ' + str(prev_site) + ' | traffic switch site: ' + str(site))
            if site is None:            #--- Initial start/restart
                print (' MAIN: initial boot ')
                # Create Consumer instance.
                c_primary = Consumer(**conf_primary, logger=logger)
                c = c_primary           #--- TODO:restart while on secondary will result in switching to primary, do a onetime check in traffic-router topic
                c.subscribe(topic_primary, on_assign=print_assignment)
                prev_site='primary'
                site='primary'
            elif site != prev_site:     #--- DR situation
                prev_site=site
                c.close()
                if site == 'primary':
                    print (' MAIN: switch to primary - sleep 10s - establish a connection')
                    time.sleep(10)
                    # Create Consumer instance.
                    c_primary = Consumer(**conf_primary, logger=logger)
                    c = c_primary
                    c.subscribe(topic_primary, on_assign=print_assignment)
                elif site == 'secondary':
                    print (' MAIN: switch to secondary - sleep 10s - establish a connection')
                    # Create Consumer instance.
                    time.sleep(10)
                    c_secondary = Consumer(**conf_secondary, logger=logger)
                    c = c_secondary
                    c.subscribe(topic_secondary, on_assign=print_assignment)

            msg = c.poll(timeout=1.0)
            if msg is None:
                #print (' MAIN - No msg' )
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                # Proper message
                sys.stderr.write('%% %s [%d] at offset %d with key %s:\n' %
                                 (msg.topic(), msg.partition(), msg.offset(),
                                  str(msg.key())))

                message=msg.value().decode('UTF-8')
                events=json.loads(message)
                event = events['EVENT']
                print ( ' MAIN - message, EVENT:'+ event)

                # Store the offset associated with msg to a local cache.
                # Stored offsets are committed to Kafka by a background thread every 'auto.commit.interval.ms'.
                # Explicitly storing offsets after processing gives at-least once semantics.
                c.store_offsets(msg)

            #-- Check if the traffic_router thread is alive
            tr_thread_alive=False
            for line in threading.enumerate():
                if type(line) is threading.Thread and line.name == 'traffic_router':
                    tr_thread_alive=True
            if not tr_thread_alive:
                print (' MAIN - traffic_router thread dead')
                #TODO: If traffic_router thread dies due to some uncaught exception, need to restart 

    except:
        #TODO: Resilient exception handling needed here
        raise KafkaException(msg.error())
    finally:
        # Close down consumer to commit final offsets.
        c_primary.close()
        c_secondary.close()

#------------------------------------------------------------------------------------------
# Function to subscribe to traffic-router topic and inform the main thread to switch traffic
#------------------------------------------------------------------------------------------
def traffic_router(conf_secondary, topic_traffic):
    global switch_msg
    global site

    print (' -- THREAD ')

    def print_assignment(consumer, partitions):
        #print('Assignment:', partitions)
        pass
    
    # Create logger for consumer (logs will be emitted when poll() is called)
    logger = logging.getLogger('consumer')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
    logger.addHandler(handler)

    c_secondary = Consumer(**conf_secondary, logger=logger)
    # Subscribe to topics
    c_secondary.subscribe(topic_traffic, on_assign=print_assignment)

    # Read messages from Kafka, print to stdout
    try:
        prev_event=None
        while True:
            time.sleep(10)  #-- Do we need frequent polls to traffic-router topic. 10s is reasonable ???
            msg = c_secondary.poll(timeout=1.0)
            if msg is None:
                print (' -- traffic_router thread - No msg' )
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                # Proper message
                sys.stderr.write('%% %s [%d] at offset %d with key %s:\n' %
                                 (msg.topic(), msg.partition(), msg.offset(),
                                  str(msg.key())))
                #'{ "EVENT":"yyyymmddhhmm","LAG":"10","SITE":"secondary"}'
                message=msg.value().decode('UTF-8')
                if (prev_event != message):
                    events=json.loads(message)
                    event = events['EVENT']
                    lag = events['LAG']
                    site = events['SITE']
                    switch_msg=event
                    print ( ' -- thread - event:'+event+' lag:'+lag+' site:'+site) 

                # Store the offset associated with msg to a local cache.
                # Stored offsets are committed to Kafka by a background thread every 'auto.commit.interval.ms'.
                # Explicitly storing offsets after processing gives at-least once semantics.
                c_secondary.store_offsets(msg)
                prev_event=message

    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')
    finally:
        # Close down consumer to commit final offsets.
        c_secondary.close()

if __name__ == '__main__':
    
    conf_primary = { **CONF.get('PRIMARY') }
    conf_secondary = { **CONF.get('SECONDARY') }

    main(conf_primary, conf_secondary)
