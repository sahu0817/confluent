### Produce APIs
#### produce to topic
```
curl --request POST \
--url 'https://pkc-ymrq7.us-east-2.aws.confluent.cloud/kafka/v3/clusters/lkc-w7vx0w/topics/rest-topic-test/records' \
--header 'content-type: application/json' \
-u WEQYIUAR5LUS7NQL:RXZZ1sq0mOSTA/3aptZyDJBb2JcLzmic3sIn/fUmTtk7MwRQMzeTuhTg4lSRXR+T \
--data "@produce_record.json"
```

<details>
  <summary>Output</summary>

  ```js
  {
    "error_code": 200,
    "cluster_id": "lkc-w7vx0w",
    "topic_name": "test2",
    "partition_id": 0,
    "offset": 7,
    "timestamp": "2022-12-03T22:14:42Z",
    "key": {
      "type": "BINARY",
      "size": 6
    },
    "value": {
      "type": "JSON",
      "size": 13
    }
  }
  ```
</details>

#### Produce to topic with inline data
```
curl --request POST \
--url https://pkc-00000.region.provider.confluent.cloud/kafka/v3/clusters/cluster-1/topics/topic-1/records \
--header 'Authorization: Basic REPLACE_BASIC_AUTH' \
--data '{"partition_id":0,"headers":[{"name":"string","value":"string"}],"key":{"type":"string","data":null},"value":{"type":"string","data":null},"timestamp":"2019-08-24T14:15:22Z"}'
```
