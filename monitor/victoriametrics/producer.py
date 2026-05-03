#!/usr/bin/env python3
#
# Demo Producer to produce events to Confluent Cloud and PUSH metrics to VictoriaMetrics
# PreRequisites:
#  - A Kafka cluster in Confluent Cloud
#  - A topic named victoria-metric-test
# 
#
import os
import json
import sys
import logging
import threading
import time
import base64
import requests
from datetime import datetime
from confluent_kafka import Producer, Consumer, TopicPartition, KafkaException
from producer_config import kafka_config_primary 
from victoria_metrics import KafkaMetricsReporter

class VMProducer:

    def __init__ ( self, topics: list[str]):

        #-- produce to this topic
        self.topics=topics

        self.clientid='vmproducer'
        self.site=None
        self.prev_site=None
        self.switch_msg=None
        self.thread_name='vm'
        self.poll_thread_name='producer_poll'
        self.poll_cancel = False
        self.poll_sleeptime = 0.5
        self.poll_timeout = 0.1
        self.sleeptime=30
        self.log_ts=datetime.today().strftime('%Y%m%d%H%M')
        self.cache_delimeter='|'
        self.vmkafka=KafkaMetricsReporter()

        custom_producer_config = {                                  #-- kafka producer customization - tune for performance optimization. TODO: move this to a config file
            "batch.size": 102400,
            "compression.type": "zstd",
            "linger.ms": 100,
            "delivery.timeout.ms": 100000,
            "request.timeout.ms": 30000,
            "client.id": self.clientid
        }

        self.config_primary = {                                     #-- kafka producer config - primary
            **kafka_config_primary(),
            "stats_cb": self.stats_cb,
            **custom_producer_config
        }

        #--- Create logger for producer (logs will be emitted when poll() is called)
        logger = logging.getLogger('producer')
        logging.basicConfig(filename='vmproducer_{:%Y%m%d}.log'.format(datetime.now()), format='%(asctime)-15s %(levelname)-8s %(message)s', encoding='utf-8', level=logging.DEBUG)
        handler = logging.StreamHandler()
        logger.addHandler(handler)


        #--- Run the VM Reporter in background thread.
        logging.debug ('MAIN - Launch daemon to report metrics to VictoriaMetric')
        vm_thread = threading.Thread(name=self.thread_name, target=self.vmkafka.run, daemon=True)
        vm_thread.start()
        
        conf=self.config_primary
        self.producer = Producer(**conf)
        self.poll_thread = threading.Thread(name=self.poll_thread_name, target=self._poll_loop)
        self.poll_thread.start()         #--- Start the background Poll


    '''
    ------------------------------------------------------------------------------------------
     Method to produce events to confluent cloud
    ------------------------------------------------------------------------------------------
    '''
    def produce(self, event):

        logging.debug ('MAIN ------- Produce --------')

        #--- Optional per-message delivery callback (triggered by poll() or flush())when a message has been successfully delivered or permanently failed delivery (after retries).
        def delivery_callback(err, msg):
            if err:
                sys.stderr.write('FAILURE:Delivery site[%s] : %s\n' % (self.site, err))
            else:
                sys.stderr.write('SUCCESS:Delivery site[%s] topic[%s] partition[%d] offset[%d] timestamp[%s] value[%s]\n' % (self.site, msg.topic(), msg.partition(), msg.offset(), msg.timestamp(), msg.value()))

        site_change=None
        p=None

        try:
            if event is not None:
                key, value = event.split(',', 1)
                #--- Produce event
                logging.debug ('MAIN - producing to : ' + str(self.site))
                try:
                    epoch_ms=round(datetime.utcnow().timestamp() * 1000)
                    self.producer.produce(''.join(self.topics), value.rstrip(), key.rstrip(), timestamp=epoch_ms, callback=delivery_callback)  #-- override the broker timestamp
                except KafkaException as e:
                    logging.debug ('MAIN - producer.produce KafkaException: ' + str(e.args[0]))
                    sys.stderr.write ('MAIN - producer.produce KafkaException: ' + str(e.args[0]) + '\n')
                    exit()     #TODO: exit or continue when the broker rejects a message ???

        except BufferError:
            sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' % len(p))
        except KeyboardInterrupt:
            sys.stderr.write('Exit with Keyboard Interrupt\n')

    '''
    ------------------------------------------------------------------------------------------
     Method to poll - background thread
    ------------------------------------------------------------------------------------------
    '''
    def _poll_loop(self):
        logging.debug ('POLL_LOOP - BACKGROUND THREAD ')
        while not self.poll_cancel:
            logging.debug ('POLL_LOOP - loop ')
            self.producer.poll(self.poll_timeout)
            time.sleep(self.poll_sleeptime)  #-- Sleep between polls
        logging.debug ('POLL_LOOP - exit ')

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
        self.poll_cancel = True
        self.poll_thread.join()

    '''
    ------------------------------------------------------------------------------------------
     Callback Method to report client statistics
    ------------------------------------------------------------------------------------------
    '''
    def stats_cb(self, stats_json_str):
        print ('stats_cb')
        logging.debug (json.dumps(json.loads(stats_json_str),indent=2))
        self.vmkafka.report(self.clientid, stats_json_str)

if __name__ == "__main__":

    from random import randint

    logging.basicConfig

    #--- produce to this topic
    topics=os.environ["KAFKA_TOPICS"].split(",")
    topics='victoria-metric-test'

    try:
        sp=VMProducer(topics)
        cnt=1
        run=randint(1, 100)
        while True:
            event=str(cnt) +',' + '{"FIELD1": "event' + str(cnt) + '_' + str(run) + ' - produce", "FIELD2": "bla", "FIELD3": "mock data from producer" }'
            sp.produce(event)
            cnt+=1
            time.sleep(1)
            if cnt > 15:
                break

        sp.flush()
    except KeyboardInterrupt:
        sys.stderr.write('Exit with Keyboard Interrupt\n')
