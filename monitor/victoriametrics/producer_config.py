import logging
import os
from typing import Any
from confluent_kafka.serialization import StringSerializer

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
