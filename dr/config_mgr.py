import os
from typing import Any

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

def clusterlink_config() -> dict[str, Any]:
    return {
        'link_id': __get_env("CC_CLUSTERLINK_ID"),
    }

def healthcheck_config() -> dict[str, Any]:
    return {
        'hc_topic': __get_env("KAFKA_TOPICS_HEALTHCHECK")
    }
def cluster_config_primary() -> dict[str, Any]:
    return {
        'cluster_id': __get_env("CC_CLUSTER_ID_PRIMARY"),
        'bootstrap_server': __get_env("KAFKA_BOOTSTRAP_SERVERS_PRIMARY"),
        'rest_url': __get_env("CC_REST_URL_PRIMARY"),
        'api_key': __get_env("KAFKA_USER_PRIMARY"),
        'api_secret': __get_env("KAFKA_PASSWORD_PRIMARY")
    }

def cluster_config_secondary() -> dict[str, Any]:
    return {
        'cluster_id': __get_env("CC_CLUSTER_ID_SECONDARY"),
        'bootstrap_server': __get_env("KAFKA_BOOTSTRAP_SERVERS_SECONDARY"),
        'rest_url': __get_env("CC_REST_URL_SECONDARY"),
        'api_key': __get_env("KAFKA_USER_SECONDARY"),
        'api_secret': __get_env("KAFKA_PASSWORD_SECONDARY")
    }