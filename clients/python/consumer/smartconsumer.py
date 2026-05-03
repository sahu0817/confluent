#!/usr/bin/env python3
#
# Smart consumer to switch between primary & secondary sites with no restarts/config changes 
# Uses a topic in secondary site as traffic router - A event (failover/failback) in this topic triggers a switch to the primary/secondary cluster 
#
# Dependencies:
# Kafka cluster configuration for primary & secondary
# Confluent Cloud REST API, cluster, clusterlink configuration for primary & secondary
#
# Updates:
# Retrieving last event and monitoring traffic-router topic is modularized in topic_library - for resuability
#
import os
import json
import sys
import logging
import threading
import time
from pprint import pformat
from datetime import datetime,timedelta
from confluent_kafka import Consumer, TopicPartition, KafkaException
from smartconsumer_config import kafka_config_primary, kafka_config_secondary
from victoria_metrics import KafkaMetricsReporter

class SmartConsumer:

    from topic_library import topic_last_event, traffic_router_monitor

    def __init__ (
            self, group_id: str, group_instance_id: str, topics: list[str], traffic_group_id: str, traffic_group_instance_id: str, topics_tr: list[str]
    ):
        self.group_id=group_id
        self.group_instance_id=group_instance_id
        self.topics=topics
        self.traffic_group_id=traffic_group_id
        self.traffic_group_instance_id=traffic_group_instance_id
        self.topics_tr=topics_tr

        self.clientid='smartconsumerv2'
        self.site=None         #-- Global (updated by traffic_router thread)
        self.tr_thread_name='traffic_router'
        self.vm_thread_name='consumer_vm'
        self.prev_site=None
        self.kafka_vm_metrics=KafkaMetricsReporter()

    def run(self):

        # Create logger for consumer (logs will be emitted when poll() is called)
        logger = logging.getLogger('consumer')
        logging.basicConfig(filename='smartconsumer_{:%Y%m%d}.log'.format(datetime.now()), format='%(asctime)-15s %(levelname)-8s %(message)s', encoding='utf-8', level=logging.DEBUG)
        handler = logging.StreamHandler()
        #handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
        logger.addHandler(handler)
        
        logging.debug ('MAIN ------- START --------')
        config_primary = {
            **kafka_config_primary(),
            "group.id": self.group_id,
            "group.instance.id": self.group_instance_id,
            "stats_cb": self.stats_cb
        }

        config_secondary = {
            **kafka_config_secondary(),
            "group.id": self.group_id,
            "group.instance.id": self.group_instance_id,
            "stats_cb": self.stats_cb
        }

        config_secondary_traffic = {
            **kafka_config_secondary(),
            "group.id": self.traffic_group_id,
            "group.instance.id": self.traffic_group_instance_id,
            "stats_cb": self.stats_cb,
            "client.id": "SmartConsumer_traffic"
        }

        def print_assignment(consumer, partitions):
            print('Assignment:', partitions)
        
        #=== check the traffic-router topic for the site to boot intially
        logging.debug ('MAIN - Check the site to boot ')
        event_msg = self.topic_last_event(config_secondary_traffic, topics_tr)
        if event_msg is not None:       #-- If No events found produce to primary site
            try:
                self.prev_site=self.site=json.loads(event_msg.value())['SITE']
            except (ValueError, TypeError, KeyError):
                logging.debug ('Corrupt message ' + str(message) + ' in topic: ' + topics_tr )

        logging.debug ('MAIN - Initial site : ' + str(self.site) )

        #=== Monitor the traffic-router topic for any new events ( Ops team to insert a event to trigger a DR failover/failback)
        logging.debug ('MAIN - Launch daemon to monitor traffic_router')
        tr_thread = threading.Thread(name=self.tr_thread_name, target=self.traffic_router_monitor, args=(config_secondary_traffic, topics_tr), daemon=True)
        tr_thread.start()

        #=== VictoriaMetrics reporter  
        logging.debug ('MAIN - Launch daemon to report kafka client metrics to VictoriaMetrics')
        vm_thread = threading.Thread(name=self.vm_thread_name, target=self.kafka_vm_metrics.run, daemon=True)
        vm_thread.start()

        c_primary=None
        c_secondary=None

        c_primary = Consumer(config_primary, logger=logger)
        c = c_primary               
        if self.site == 'secondary':
            c_secondary = Consumer(config_secondary, logger=logger)
            c = c_secondary

        c.subscribe(self.topics, on_assign=print_assignment)
        self.prev_site = self.site

        try:
            while True:
                logging.debug ('MAIN - prev site : ' + str(self.prev_site) + ', switch site : ' +  str(self.site))
                if self.site != self.prev_site:    #--- While the consumer is running - DR situation  
                    c.close()                   #-- Close the previous site before switching sites
                    logging.debug ('MAIN - switch to site (sleep10): ' + str(self.site))
                    if self.site == 'primary':
                        time.sleep(10)
                        c_primary = Consumer(config_primary, logger=logger)
                        c = c_primary
                        c.subscribe(self.topics, on_assign=print_assignment)
                    elif self.site == 'secondary':
                        time.sleep(10)
                        c_secondary = Consumer(config_secondary, logger=logger)
                        c = c_secondary
                        c.subscribe(self.topics, on_assign=print_assignment)
                    self.prev_site=self.site

                msg = c.poll(timeout=1.0)
 
                if msg is None:
                    continue

                if msg.error():
                    raise KafkaException(msg.error())
                else:
                    # Proper message
                    sys.stderr.write('%% %s [%d] at offset %d with key %s:\n' % (msg.topic(), msg.partition(), msg.offset(), str(msg.key())))

                    message=msg.value().decode('UTF-8')
                    try:
                        event_msg=json.loads(message)
                        event = event_msg['FIELD1']
                        logging.debug ('MAIN - Event ' + event )
                    except (ValueError, TypeError, KeyError):
                        logging.debug ('MAIN - Corrupt message ' + str(message))
                    
                    # Store the offset associated with msg to a local cache. Stored offsets are committed to Kafka by a background thread every 'auto.commit.interval.ms'.
                    # Explicitly storing offsets after processing gives at-least once semantics.
                    c.store_offsets(msg)

                #-- Ensure traffic_router thread is alive
                if not tr_thread.is_alive():
                    logging.debug ('MAIN - traffic_router thread dead, starting now')
                    tr_thread.start()

        except KeyboardInterrupt:
            #TODO: Resilient exception handling needed here
            #print ( "An exception of type {0} occurred. Arguments:\n{1!r}".format(type(ex).__name__, ex.args))
            print ( "User Interrupt")
        except KafkaException as e:
            logging.debug ('MAIN - consumer.poll KafkaException: ' + str(e.args[0]))
            sys.stderr.write ('MAIN - consumer.poll KafkaException: ' + str(e.args[0]) + '\n')
        finally:
            # Close down consumer to commit final offsets. There could be unreferenced object, hence check.
            logging.debug ('MAIN - closing')
            if ( isinstance (c_primary, Consumer) ):
                c_primary.close()
            if ( isinstance (c_secondary, Consumer) ):
                c_secondary.close()


    '''
    ------------------------------------------------------------------------------------------
     Callback Function to report statistics
    ------------------------------------------------------------------------------------------
    '''
    def stats_cb(self, stats_json_str):
        #logging.debug (json.dumps(json.loads(stats_json_str),indent=2))
        self.kafka_vm_metrics.report(self.clientid, stats_json_str)

if __name__ == "__main__":

    logging.basicConfig

    group_id=os.environ["KAFKA_GROUP_ID"]
    group_instance_id=os.environ["KAFKA_GROUP_INSTANCE_ID"]
    topics=os.environ["KAFKA_TOPICS"].split(",")

    traffic_group_id=os.environ["KAFKA_TRAFFIC_GROUP_SC_ID"]
    traffic_group_instance_id=os.environ["KAFKA_TRAFFIC_GROUP_INSTANCE_ID"]
    topics_tr=os.environ["KAFKA_TOPICS_TRAFFIC_ROUTER"].split(",")

    SmartConsumer(group_id, group_instance_id, topics, traffic_group_id, traffic_group_instance_id, topics_tr).run()
