## librdkafka debug 
Context and verbosity [in braces] of each context .
```
generic = anything generic enough not to fit the other contexts [noise=sparse]
broker = broker handling (protocol requests, queues) [medium]
topic = topic and partition state changes and events [medium]
queue = internal request and message queue events [low]
msg = message tranmission and parsing [high]
protocol = Kafka protocol requests and responses [medium/high]
cgrp = consumer group state machine [medium]
security = SSL and SASL handshakes - on connect only [low]
fetch = Consumer's fetcher state machine and fetch decisions [high]
feature = Broker feature discovery - on connect only [medium]
interceptor = interceptor handling and callbacks [low]
plugin = dynamic plugin loading [sparse]
metadata = Topic and broker metadata updates [medium]
admin
eos
mock
assignor
conf
all = enable all of the above contexts [very high]
```

Typical non-secure Producer debug settings for information on handling the broker connection, topic metadata, and message transmission.
```
debug=broker,topic,msg
```
Typical non-secure Consumer debug settings for information on consumer group state, topic metadata, and message fetching.
```
debug=cgrp,topic,fetch
```

## Debug log interpretation

No batching
```
"May 1, 2024 @ 13:59:56.745","MSGSET [amplify-batch#producer-3] [thrd:sasl_ssl://e-0720-use1-az2-gje8v9.us-east-1.aws.glb.confluent.c]: sasl_ssl://e-0720-use1-az2-gje8v9.us-east-1.aws.glb.confluent.cloud:9092/15: amplify.capture-cu-ba.1 [15]: MessageSet with 1 message(s) (MsgId 0, BaseSeq -1) delivered","affirm.chrono.publisher.kafka.v1.librdkafka",DEBUG,"-","us-east-1",live
```
With batching
```
%7|1715185916.090|MSGSET|TestProducer#producer-1| [thrd:sasl_ssl://b2-pkc-6583q.eastus2.azure.confluent.cloud:9092/2]: sasl_ssl://b2-pkc-6583q.eastus2.azure.confluent.cloud:9092/2: linked-topic [1]: MessageSet with 19 message(s) (MsgId 0, BaseSeq -1) delivered
```
