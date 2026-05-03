curl --request PUT \
--url "https://api.confluent.cloud/connect/v1/environments/${ENV_ID}/clusters/${CLUSTER_ID}/connectors/xyz/config" \
--header 'Authorization: Basic '$CLOUD_AUTH'' --header 'content-type: application/json'  \
--data '{
    "name": "<UPDATE_ME>",
    "connector.class": "SqlServerCdcSourceV2",
    "database.hostname": "<UPDATE_ME>",
    "database.names": "testdb",
    "database.port": "5434",
    "database.user": "kafka",
    "database.password": "<UPDATE_ME>",
    "kafka.api.key": "<UPDATE_ME>",
    "kafka.api.secret": "<UPDATE_ME>",
    "kafka.auth.mode": "KAFKA_API_KEY",
    "kafka.endpoint": "SASL_SSL://<UPDATE_ME>:9092",
    "output.data.format": "AVRO",
    "output.key.format": "JSON",
    "table.include.list": "dbo.Employee",
    "tasks.max": "1",
    "topic.prefix": "<UPDATE_ME>",
    "tasks.max": "1"
}'
