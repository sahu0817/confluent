#!/usr/bin/env python3
#
# Report Kafka client metrics to VictoriaMetrics
# Designed to report 'brokers', 'topics', 'cgrp' & 'eos' metrics only.
#
# Dependencies:
#   Integration of this class in a client producer/consumer stats_cb callback method.
#   VictoriaMetrics Rest URL
# Usage:
#   In producer/consumer clients 
#    - Run the thread in a daemon mode
#       kafka_vm_metrics=KafkaMetricsReporter()
#       vm_thread = threading.Thread(target=kafka_vm_metrics.run, daemon=True)
#       vm_thread.start()
#    - Report metrics in stats_cb callback method
#       kafka_vm_metrics.report(clientid, stats_json_str)
#
import os
import json
import sys
import logging
import time
import threading
import base64
import requests
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
from queue import Empty, Full, Queue

kafka_instances = []

class KafkaMetricsReporter(threading.Thread):
    @dataclass
    class VictoriaMetric:
        key: str
        value: Any
        tags: List[str]

    def __init__(self, report_to_vm: bool = True) -> None:
        super().__init__(daemon=True)
        self.metrics_to_log: Queue[Tuple[str, str]] = Queue(maxsize=100)
        self.metrics_report_interval_ms = 60000
        self.vm_report_cooldown_ms = 4000
        self.report_to_vm = report_to_vm
        self.vm_rest_url="http://localhost:8428"
        self.vm_rest_endpoint=self.vm_rest_url + "/api/v1/import/prometheus"
        self.vm_rest_headers = { 'Content-Type': 'application/x-www-form-urlencoded', }
        self.vm_timeout_s = 3
        self.vm_up = True
        self.session=requests.Session()

    def run(self) -> None:
        while True:
            try:
                (kafka_instance_id, metrics_to_log) = self.metrics_to_log.get( block=True, timeout=10)
                self._report(kafka_instance_id, metrics_to_log)
                time.sleep(self.vm_report_cooldown_ms / 1000)
                self.vm_up = True
                try:
                    requests.get(self.vm_rest_url)
                except requests.exceptions.ConnectionError:
                    self.vm_up=False
                    logging.info ('KAFKA_METRICS_REPORTER - ' + self.vm_rest_url + ' is DOWN')
            except Empty:
                pass
            except Exception as e:
                print(e)

    def report(self, kafka_instance_id: str, metrics_json_str: str) -> None:
        try:
            self.metrics_to_log.put((kafka_instance_id, metrics_json_str))
        except Full as e:
            print(e)
            for _ in range(self.metrics_to_log.qsize()):
                self.metrics_to_log.get_nowait()
        except Exception as e:
            print(e)

    def _report( self, kafka_instance_id: str, metrics_json_str: str) -> List["KafkaMetricsReporter.VictoriaMetric"]:
        try:
            if kafka_instance_id not in kafka_instances:
                kafka_instances.append(kafka_instance_id)
            instance_idx = kafka_instances.index(kafka_instance_id)
            library_metrics: Dict[str, Any] = json.loads(metrics_json_str)
            vm_metrics_to_report: List[KafkaMetricsReporter.VictoriaMetric] = []
            top_level_tags: List[str] = [
                f"instance_id:{instance_idx}",
            ]

            for key, metric in library_metrics.items():
                if isinstance(metric, str):
                    top_level_tags.append(f"{key}:{metric}")

            # log top level metrics for now
            for key, metric in library_metrics.items():
                if key == "brokers":
                    vm_metrics_to_report.extend( self.extract_broker_metrics(metric, library_metrics))
                elif key == "topics":
                    vm_metrics_to_report.extend(self.extract_topic_metrics(metric, library_metrics))
                elif key == "cgrp":
                    vm_metrics_to_report.extend(self.extract_cgrp_metrics(metric, library_metrics))
                elif key == "eos":
                    vm_metrics_to_report.extend(self.extract_eos_metrics(metric, library_metrics))
                elif isinstance(metric, str):
                    continue
                else:
                    vm_metrics_to_report.append( KafkaMetricsReporter.VictoriaMetric(key=key, value=metric, tags=[]))

            reported_metrics = []
            for metric in vm_metrics_to_report:
                cleaned_tags = [ tag.replace("#", "__") for tag in (metric.tags + top_level_tags) if tag != "" ]
                reported_metric = KafkaMetricsReporter.VictoriaMetric(
                    f"kafka.client_metrics.{metric.key}", metric.value, cleaned_tags
                )
                reported_metrics.append(reported_metric)
                if self.report_to_vm and self.vm_up:
                    self.vm_post(reported_metric)

            return reported_metrics
        except Exception as e:
            print(e)
            return []

    '''
    ===== REST API Post to VictoriaMetrics
    '''
    def vm_post( self, reported_metric: Dict[str, Any]) -> "request.Response().status_code":

        labels='{'
        for tag in reported_metric.tags:
            (key, value)=tag.split(':', 1)
            labels+= key + '=' + '"' + value + '", '
        labels+= '}'

        data = f'{reported_metric.key}{labels} {reported_metric.value}'
        #logging.debug ('KAFKA_METRICS_REPORTER - ' + data )
        res=self.session.post(self.vm_rest_endpoint, headers=self.vm_rest_headers, data=data, timeout=self.vm_timeout_s)

        if not res.status_code < 300:       #-- expect 204
            logging.info ('KAFKA_METRICS_REPORTER - ERROR HTTP:' + str(res.status_code))

        return res.status_code


    '''
    ===== Extract broker metrics from the json object
    '''
    def extract_broker_metrics( self, library_broker_metrics: Dict[str, Any], all_library_metrics: Dict[str, Any],) -> List["KafkaMetricsReporter.VictoriaMetric"]:

        if library_broker_metrics is None or library_broker_metrics == {}:
            return []

        broker_metrics: List["KafkaMetricsReporter.VictoriaMetric"] = []
        for name, value in library_broker_metrics.items():
            tags: List[str] = [f"broker_name:{name}"]
            if value.get("connects", -1) == 0 and value.get("disconnects", -1) == 0:
                # broker is unused, no need to report metrics
                continue
            for key, value in value.items():
                if key.endswith("_latency") or key == "rtt" or key == "throttle":
                    """if (value.get("cnt") or 0) == 0:
                        # if no requests, then don't report latency values
                        continue"""
                    object_metrics = self._process_simple_object(value)
                    for object_metric in object_metrics:
                        object_metric.key = f"broker_metrics.{key}.{object_metric.key}"
                        object_metric.tags.extend(tags)
                        broker_metrics.append(object_metric)
                elif isinstance(value, int):
                    broker_metrics.append(
                        self.VictoriaMetric(key=f"broker_metrics.{key}", value=value, tags=tags)
                    )

        return broker_metrics


    '''
    ===== Extract topic metrics from the json object
    '''
    def extract_topic_metrics( self, library_topic_metrics: Dict[str, Any], all_library_metrics: Dict[str, Any]) -> List["KafkaMetricsReporter.VictoriaMetric"]:

        if library_topic_metrics is None or library_topic_metrics == {}:
            return []
        topic_metrics: List["KafkaMetricsReporter.VictoriaMetric"] = []
        for name, value in library_topic_metrics.items():
            tags: List[str] = [f"topic_name:{name}"]
            for key, value in value.items():
                if key == "batchsize" or key == "batchcnt":
                    object_metrics = self._process_simple_object(value)
                    for object_metric in object_metrics:
                        object_metric.key = f"topic_metrics.{key}.{object_metric.key}"
                        object_metric.tags.extend(tags)
                        topic_metrics.append(object_metric)
                elif key == "partitions":
                    for partition_name, stats in value.items():
                        if partition_name == "-1":
                            # unassigned partition
                            continue
                        partition_tags = [f"partition_name:{partition_name}"]
                        broker_id: int = stats["broker"]
                        if broker_id >= 0:
                            for key, value in all_library_metrics["brokers"].items():
                                if value["nodeid"] == broker_id:
                                    partition_tags.append(f"broker_name:{key}")
                                    break

                        leader_id: int = stats["leader"]
                        if leader_id >= 0:
                            for key, value in all_library_metrics["brokers"].items():
                                if value["nodeid"] == leader_id:
                                    partition_tags.append(f"leader_name:{key}")
                                    break

                        partition_tags.extend(tags)
                        for key, value in stats.items():
                            if isinstance(value, int) or isinstance(value, bool):
                                topic_metrics.append(
                                    self.VictoriaMetric(
                                        key=f"topic_metrics.partition_metrics.{key}",
                                        value=(1 if value else 0)
                                        if isinstance(value, bool)
                                        else value,
                                        tags=partition_tags,
                                    )
                                )

                elif isinstance(value, int):
                    topic_metrics.append(
                        self.VictoriaMetric(key=f"topic_metrics.{key}", value=value, tags=tags)
                    )
        return topic_metrics

    '''
    ===== Extract consumer group metrics from the json object
    '''
    def extract_cgrp_metrics( self, library_cgrp_metrics: Dict[str, Any], all_library_metrics: Dict[str, Any]) -> List["KafkaMetricsReporter.VictoriaMetric"]:

        if library_cgrp_metrics is None or library_cgrp_metrics == {}:
            return []
        cgrp_metrics: List["KafkaMetricsReporter.VictoriaMetric"] = []
        tags: List[str] = [
            f"state:{library_cgrp_metrics['state']}",
            f"join_state:{library_cgrp_metrics['join_state']}",
        ]
        for key, value in library_cgrp_metrics.items():
            if isinstance(value, int):
                cgrp_metrics.append(
                    self.VictoriaMetric(key=f"cgrp_metrics.{key}", value=value, tags=tags)
                )
        return cgrp_metrics    

    '''
    ===== Exactly Once Semantics Metrics
    '''
    def extract_eos_metrics( self, library_eos_metrics: Dict[str, Any], all_library_metrics: Dict[str, Any]) -> List["KafkaMetricsReporter.VictoriaMetric"]:

        eos_metrics: List["KafkaMetricsReporter.VictoriaMetric"] = []
        tags: List[str] = [
            f"idemp_state:{library_eos_metrics['idemp_state']}",
            f"txn_state:{library_eos_metrics['txn_state']}",
        ]
        for key, value in library_eos_metrics.items():
            if isinstance(value, int):
                eos_metrics.append(
                    self.VictoriaMetric(key=f"eos_metrics.{key}", value=value, tags=tags)
                )
        return eos_metrics


    '''
    ==== normalize by extracting simple key,value objects, ignore any nested objects
    '''
    def _process_simple_object( self, simple_object: Dict[str, Any]) -> List["KafkaMetricsReporter.VictoriaMetric"]:

        metrics: List["KafkaMetricsReporter.VictoriaMetric"] = []
        for key, metric in simple_object.items():
            if isinstance(metric, dict) or isinstance(metric, list) or isinstance(metric, str):
                raise Exception(f"Unexpected object type in terminal object: {metric}")
            else:
                metrics.append(KafkaMetricsReporter.VictoriaMetric(key=key, value=metric, tags=[]))
        return metrics
