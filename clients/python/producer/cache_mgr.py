#!/usr/bin/env python3
#
# Cache managment module to write & replay from the cache
#
# Dependencies:
# Kafka cluster configuration for primary & secondary
# A datavolume to create a local cache (for k8s deployment)
#
# Updates:
# - Improve the cache replay logic based on last event in the mirror topic from the inactive site
# 
#
import os
import sys
import re
import logging
import threading
import time
#from datetime import datetime
import datetime
from confluent_kafka import Producer, Message, KafkaException
from smartproducer_config import kafka_config_primary, kafka_config_secondary
from victoria_metrics import KafkaMetricsReporter

class CacheManager:

    def __init__ ( self, cache_dir: str, cache_delimeter: str, topics: list[str]): 

        #-- produce to this topic
        self.chk_thread_name='cache_hk'
        self.sleeptime=30
        self.cache_log_ts=None
        self.cache_dir="/home/ubuntu/customer/openai/python/producer"
        self.cache_fd=None
        self.cache_delimeter='|'
        self.cache_topics=topics
        self.cache_age_threshold_mm=60  #-- delete cache older than 60 minutes
        self.cache_age_threshold_mm=1440  #-- test
        self.vm_thread_name='cachereplay_vm'
        self.kafka_vm_metrics=KafkaMetricsReporter()

        #--- Create logger for cachemanager 
        logger = logging.getLogger(__name__)
        #logging.basicConfig(filename='cachemanager_{:%Y%m%d}.log'.format(datetime.datetime.now()), format='%(asctime)-15s %(levelname)-8s %(module)s %(message)s', encoding='utf-8', level=logging.DEBUG)
        #logger.addHandler(logging.StreamHandler())

        #--- HouseKeeping of cache files - daemon thread
        logging.debug ('CACHEMANAGER - Launch daemon to housekeeping of cache')
        self.chk_thread = threading.Thread(name=self.chk_thread_name, target=self.housekeeping, daemon=True)
        self.chk_thread.start()
 
 

    '''
    ------------------------------------------------------------------------------------------
    Write to local cache
    ------------------------------------------------------------------------------------------
    '''
    def write_cache( self, topic: str, epoch_ms: str, key, value):

        #TODO: rudimentary cache writing. Replace this with a intelligent cache implementaiton, if this doesnt scale.
        logging.debug ('WRITE_CACHE')
        current_log_ts=datetime.datetime.today().strftime('%Y%m%d%H%M')
        if current_log_ts != self.cache_log_ts:
            if self.cache_fd is not None:
                self.cache_fd.close()
            self.cache_log_ts=current_log_ts
            cache_file='cache_{}_{}.log'.format(topic,self.cache_log_ts)
            self.cache_fd = open(cache_file, 'a', 1)    #-- line buffering, potential performance bottleneck.

        entry=self.cache_delimeter.join([str(epoch_ms), key, value])+'\n'
        self.cache_fd.write(entry)
    '''
    --------------------------------------------------------------------------------------------------------------------
    During a DR event, Replay those events from cache that didnt replicate (inflight-cluster_link) to secondary cluster.
    --------------------------------------------------------------------------------------------------------------------
    '''
    def replay_cache( self, producer: Producer, site: str, topic: str, last_msg: Message):

        logging.debug ('REPLAY_CACHE - producing to  site : ' + site)

        def delivery_callback(err, msg):
            if err:
                sys.stderr.write('REPLAY_CACHE FAILURE:Delivery site[%s] : %s\n' % (site, err))
            else:
                sys.stderr.write('REPLAY_CACHE SUCCESS:Delivery site[%s] topic[%s] partition[%d] offset[%d] timestamp[%s] value[%s]\n' % (site, msg.topic(), msg.partition(), msg.offset(), msg.timestamp(), msg.value()))


        # Identify the cache files ( rotated by minute ). Filter those that have events before the disaster ( last event in DR site ) 
        regex=re.compile('cache_{}.*\.log'.format(topic))
        files=[]
        for entry in os.scandir(self.cache_dir):
            if regex.match(entry.name):
                files.append(entry.name)

        if not files:
            logging.debug ('REPLAY_CACHE - no cache files found to replay')
            return None

        (_, last_msg_ts)=last_msg.timestamp()

        for file in sorted(files):
            num_newlines=0
            dirfile=self.cache_dir+'/'+file
            try:
                if os.stat(dirfile).st_size == 0:
                    files.remove(file)
                    continue
                with open(dirfile, 'rb') as f:
                    try:
                        f.seek(-2, os.SEEK_END)
                        while num_newlines < 1:
                            f.seek(-2, os.SEEK_CUR)
                            if f.read(1) == b'\n':
                                num_newlines += 1
                    except OSError:
                        f.seek(0)
                    last_line = f.readline().decode().strip()
                    if last_line is None:
                        continue
                    last_ts=last_line.split(self.cache_delimeter)[0]
                    if int(last_ts) < last_msg_ts:
                        files.remove(file)
            except OSError:
                continue    #--- file could have been deleted as part of housekeeping

        # Retrieve the events in cache files that needs to be replayed to DR site
        for file in sorted(files):
            try:
                dirfile=self.cache_dir+'/'+file
                logging.debug ('REPLAY_CACHE - cache file:'+ dirfile )
                with open(dirfile, 'r') as f:
                    for line in f:
                        (cache_ts,cache_key,cache_value)=line.rstrip("\n").split(self.cache_delimeter)
                        logging.debug ('REPLAY_CACHE - cache ts:'+ cache_ts + ' last_msg_ts:' + str(last_msg_ts))
                        cache_ts_int=int(cache_ts)
                        if cache_ts_int > last_msg_ts:
                            logging.debug ('REPLAY_CACHE - producing key:'+ cache_key + ' value:' + cache_value) 
                            producer.produce(topic, cache_value.rstrip(), cache_key.rstrip(), timestamp=cache_ts_int, callback=delivery_callback)
            except (IOError, OSError) as e:
                logging.debug('cache file :' + file + ' not found. ERROR:' + str(e.errno))

    '''
    ------------------------------------------------------------------------------------------
    Cache House Keeping
    ------------------------------------------------------------------------------------------
    '''
    def housekeeping(self):
        logging.debug ('CACHE_HOUSEKEEPING')
        while True:
            topic=''.join(self.cache_topics)
            regex=re.compile('cache_{}.*\.log'.format(topic))
            files=[]
            for entry in os.scandir(self.cache_dir):
                if regex.match(entry.name):
                    files.append(entry.name)

            if not files:
                logging.debug ('CACHE_HOUSEKEEPING - no cache files found to housekeep')
            else:
                for file in sorted(files):
                    logging.debug ('CACHE_HOUSEKEEPING - file ' + file)
                    age_minutes = (datetime.datetime.today() - datetime.datetime.fromtimestamp(os.path.getmtime(file))).total_seconds() / 60
                    logging.debug ('CACHE_HOUSEKEEPING - age ' + str(age_minutes) )
                    if age_minutes > self.cache_age_threshold_mm:
                        try:
                            os.remove(file)
                            logging.debug ('CACHE_HOUSEKEEPING - file deleted ' + file)
                        except FileNotFoundError:
                            logging.debug ('CACHE_HOUSEKEEPING - file disappeared ' + file)
        
            time.sleep(self.sleeptime)




if __name__ == "__main__":

    from random import randint

    '''
    ------------------------------------------------------------------------------------------
    stats_cb
    ------------------------------------------------------------------------------------------
    '''
    def stats_cb(self, stats_json_str):
        ##logging.debug (json.dumps(json.loads(stats_json_str),indent=2))
        kafka_vm_metrics.report(self.clientid, stats_json_str)

    #--- cache for this topic 
    topics=os.environ["KAFKA_TOPICS"].split(",")
    topic=''.join(topics)
    cache_dir=r"/home/ubuntu/customer/openai/python/producer"
    cache_delimeter='|'
    
    custom_producer_config = {    
        "batch.size": 102400,
        "compression.type": "zstd",
        "linger.ms": 100,
        "delivery.timeout.ms": 100000,
        "request.timeout.ms": 30000,
        "client.id": "SmartProducer"
    }

    config_primary = {                                  
        **kafka_config_primary(),
        "stats_cb": stats_cb,
        **custom_producer_config
    }
    config_secondary = {                                 
        **kafka_config_secondary(),
        "stats_cb": stats_cb,
        **custom_producer_config
    }
    conf=config_secondary
    producer = Producer(**conf)
    

    try:
        cm=CacheManager(cache_dir, cache_delimeter, topics)
        cnt=1
        run=randint(1, 100)
        while True:
            epoch_ms=round(datetime.datetime.now(datetime.UTC).timestamp() * 1000)
            event=str(cnt) +',' + '{"FIELD1": "event' + str(cnt) + '_' + str(run) + ' - produce", "FIELD2": "bla", "FIELD3": "mock data from smart producer" }'
            key, value = event.split(',', 1)
            #cm.write_cache(topic, epoch_ms, key, value)
            cnt+=1
            #time.sleep(1)
            if cnt > 50:
                break
        last_msg=1710631775834 
        site="secondary"
        #cm.replay_cache(producer, site, topic, last_msg)

    except KeyboardInterrupt:
        sys.stderr.write('Exit with Keyboard Interrupt\n')
