import logging
import os
from typing import Any
from confluent_kafka.serialization import StringSerializer
#from confluent_kafka.schema_registry.avro import AvroSerializer

def __get_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value =="":
        raise ValueError(f"{name} must be set in environment")
    return value 

def kafka_config_primary() -> dict[str, Any]:
    return {
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'statistics.interval.ms': 10000,
        'bootstrap.servers': __get_env("KAFKA_BOOTSTRAP_SERVERS_PRIMARY"),
        'sasl.username': __get_env("KAFKA_USER_PRIMARY"),
        'sasl.password': __get_env("KAFKA_PASSWORD_PRIMARY")
    }

def kafka_config_secondary() -> dict[str, Any]:
    return {
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'statistics.interval.ms': 10000,
        'bootstrap.servers': __get_env("KAFKA_BOOTSTRAP_SERVERS_SECONDARY"),
        'sasl.username': __get_env("KAFKA_USER_SECONDARY"),
        'sasl.password': __get_env("KAFKA_PASSWORD_SECONDARY")
    }

def cc_config_primary() -> dict[str, Any]:
    return {
        'cc.rest.url': __get_env("CC_REST_URL_PRIMARY"),
        'cc.api.key': __get_env("KAFKA_USER_PRIMARY"),
        'cc.api.secret': __get_env("KAFKA_PASSWORD_PRIMARY"),
        'cc.cluster.id': __get_env("CC_CLUSTER_ID_PRIMARY"), 
        'cc.clusterlink.id': __get_env("CC_CLUSTERLINK_ID")
    }

def cc_config_secondary() -> dict[str, Any]:
    return {
        'cc.rest.url': __get_env("CC_REST_URL_SECONDARY"),
        'cc.api.key': __get_env("KAFKA_USER_SECONDARY"),
        'cc.api.secret': __get_env("KAFKA_PASSWORD_SECONDARY"),
        'cc.cluster.id': __get_env("CC_CLUSTER_ID_SECONDARY"),
        'cc.clusterlink.id': __get_env("CC_CLUSTERLINK_ID")
    }

