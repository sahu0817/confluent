from confluent_kafka.serialization import StringSerializer
#from confluent_kafka.schema_registry.avro import AvroSerializer

CONF_BASE = {
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    #'stats_cb': 'stats_cb',
    'statistics.interval.ms': 10000,
    #'auto.register.schemas': False
}
conf_primary = {
    **CONF_BASE,
    'bootstrap.servers': 'pkc-6583q.eastus2.azure.confluent.cloud:9092',
    'sasl.username': 'WNSDDDXXXXXXXX',
    'sasl.password': 'Jjh3ZF9kA2YU133U0iZr9S78Dq3Iik5/3IN1Dsos9nrwpawR8EkXXXXXXXXXXX',
    'enable.auto.offset.store': False,
    'auto.offset.reset': 'latest',
    'group.id': 'consumer', 
    'session.timeout.ms': 6000
}
conf_secondary = {
    **CONF_BASE,
    'bootstrap.servers': 'pkc-ryzn9.westus3.azure.confluent.cloud:9092',
    'sasl.username': 'DJSPYEVXXXXXXX',
    'sasl.password': 'WA/imJQlfTc94C0kGMX2pRQmUZXda4QRQJOvLV1jVL0LdXXXXXXXXXX',
    'enable.auto.offset.store': False,
    'auto.offset.reset': 'latest',
    'group.id': 'consumer', 
    'session.timeout.ms': 6000
}

CONF = {
    'PRIMARY': conf_primary,
    'SECONDARY': conf_secondary
}
TOPIC = {
    'PRIMARY': ['common-topic'],
    'SECONDARY': ['common-topic'],
    'TRAFFICROUTER': ['traffic-router']
}
