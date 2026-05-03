### Register Schema
```
> confluent schema-registry schema create --schema avro_schema.json --subject schema_validation-value --type avro
Successfully registered schema with ID 100001
```
avro_schema.json
```
{
    "name": "schema_validation",
    "namespace": "btest.com",
    "type": "record",
    "fields": [
      { "name": "foo_string", "type": "string" },
      { "name": "foo_int", "type": "int" }
    ]
}
```
### List Schemas & Subjects
```
> confluent schema-registry subject list
                     Subject
--------------------------------------------------
  confluent.io.examples.serialization.avro.Order
  confluent.io.examples.serialization.avro.User
  firehose-multi-schema-value
  firehose-single-schema-value
  orgid_001-value
  orgid_002-value

> confluent schema-registry schema list
  Schema ID |                    Subject                     | Version
------------+------------------------------------------------+----------
     100001 | confluent.io.examples.serialization.avro.User  |       1
     100001 | firehose-multi-schema-value                    |       2
     100001 | firehose-single-schema-value                   |       1
     100002 | orgid_001-value                                |       1
     100002 | orgid_002-value                                |       1
     100003 | confluent.io.examples.serialization.avro.Order |       1
```

### Delete Schema
:warning: SoftDelete first and Hard Delete to leave no references behind.
```
> confluent schema-registry schema delete --subject firehose-multi-schema-value --version 2
Are you sure you want to delete schema "firehose-multi-schema-value (version 2)"?
To confirm, type "firehose-multi-schema-value". To cancel, press Ctrl-C: firehose-multi-schema-value
Successfully soft deleted version "2" for subject "firehose-multi-schema-value".
  Version
-----------
        2
> confluent schema-registry schema delete --subject firehose-multi-schema-value --version 2 --permanent
Are you sure you want to permanently delete schema "firehose-multi-schema-value (version 2)"?
To confirm, type "firehose-multi-schema-value". To cancel, press Ctrl-C: firehose-multi-schema-value
Successfully hard deleted version "2" for subject "firehose-multi-schema-value".
  Version
-----------
        2
```
### Broker side schema validation
```
> kafka-avro-console-producer --bootstrap-server pkc-ryzn9.westus3.azure.confluent.cloud:9092 \
--producer.config java.config --topic schema_validation --property value.schema.id=100001 \
--property basic.auth.credentials.source="USER_INFO" \
--property schema.registry.url="https://psrc-lq2dm.us-east-2.aws.confluent.cloud" \
--property schema.registry.basic.auth.user.info="XXXXXX:XXXXXX"

{"foo_string":"string", "foo_int":1}
{"foo_string":"string", "foo_int":"foo_string"}

org.apache.kafka.common.errors.SerializationException: Error deserializing json {"foo_string":"string", "foo_int":"foo_string"} to Avro of schema {"type":"record","name":"schema_validation","namespace":"block.com","fields":[{"name":"foo_string","type":"string"},{"name":"foo_int","type":"int"}]}
	at io.confluent.kafka.formatter.AvroMessageReader.readFrom(AvroMessageReader.java:134)
	at io.confluent.kafka.formatter.SchemaMessageReader.readMessage(SchemaMessageReader.java:325)
	at kafka.tools.ConsoleProducer$.main(ConsoleProducer.scala:51)
	at kafka.tools.ConsoleProducer.main(ConsoleProducer.scala)
Caused by: org.apache.avro.AvroTypeException: Expected int. Got VALUE_STRING
```

### Schema Evolution - Compatibility
#### backward compatibility test

Register
```
> confluent schema-registry  schema create --type AVRO --api-key XXXXX --api-secret XXXXXX --schema avro_backward.avsc --subject avro-value

Successfully registered schema with ID 100006
```
 
Register ( not backward compatibile ) 
```
> confluent schema-registry  schema create --type AVRO --api-key XXXXX --api-secret XXXXXX --schema avro_backward_bad.avsc --subject avro-value

Error: {"error_code":409,"message":"Schema being registered is incompatible with an earlier schema for subject \"avro-value\", details: [{errorType:'READER_FIELD_MISSING_DEFAULT_VALUE', description:'The field 'custid' at path '/fields/1' in the new schema has no default value and is missing in the old schema', additionalInfo:'custid'}, {oldSchemaVersion: 1}, {oldSchema: '{\"type\":\"record\",\"name\":\"compact_test\",\"namespace\":\"io.confluent.examples\",\"fields\":[{\"name\":\"seq\",\"type\":\"int\"}]}'}, {compatibility: 'BACKWARD'}]; error code: 409"}

```
 
Register ( backward compatible )
```
> confluent schema-registry  schema create --type AVRO --api-key XXXXX --api-secret XXXXXX --schema avro_backward_good.avsc --subject avro-value

Successfully registered schema with ID 100007
```

#### forward compatibility test
 
Register
```
confluent schema-registry  schema create --type AVRO --api-key XXXXX --api-secret XXXXX --schema ./avro_forward.avsc --subject avro-forward-value
Successfully registered schema with ID 100008
```
> change compatibility mode to FORWARD after registering the above schema
 
Register ( not forward compatible )
```
> confluent schema-registry  schema create --type AVRO --api-key XXXXX --api-secret XXXXX --schema ./avro_forward_bad.avsc --subject avro-forward-value --output yaml
Error: {"error_code":409,"message":"Schema being registered is incompatible with an earlier schema for subject \"avro-forward-value\", details: [{errorType:'READER_FIELD_MISSING_DEFAULT_VALUE', description:'The field 'seq' at path '/fields/0' in the old schema has no default value and is missing in the new schema', additionalInfo:'seq'}, {oldSchemaVersion: 1}, {oldSchema: '{\"type\":\"record\",\"name\":\"forward_test\",\"namespace\":\"io.confluent.examples\",\"fields\":[{\"name\":\"seq\",\"type\":\"int\"},{\"name\":\"cust\",\"type\":\"int\",\"default\":123}]}'}, {compatibility: 'FORWARD'}]; error code: 409"}
```
 
Register ( forward compatible ) 
```
> confluent schema-registry  schema create --type AVRO --api-key XXXXX --api-secret XXXXX  --schema ./avro_forward_good.avsc --subject avro-forward-value --output yaml
id: 100009

```
#### full compatibility test
 
Register
```
> confluent schema-registry  schema create --type AVRO --api-key XXXXX--api-secret XXXXX --schema ./avro_full.avsc --subject avro-full-value
Successfully registered schema with ID 100010
```
> change compatibility mode to FULL after registering the above schema
 
Register ( not full compatible )
```
> confluent schema-registry  schema create --type AVRO --api-key XXXXX --api-secret XXXXX --schema ./avro_full_bad.avsc --subject avro-full-value
Error: {"error_code":409,"message":"Schema being registered is incompatible with an earlier schema for subject \"avro-full-value\", details: [{errorType:'READER_FIELD_MISSING_DEFAULT_VALUE', description:'The field 'xyz' at path '/fields/2' in the new schema has no default value and is missing in the old schema', additionalInfo:'xyz'}, {oldSchemaVersion: 1}, {oldSchema: '{\"type\":\"record\",\"name\":\"backward_test\",\"namespace\":\"io.confluent.examples\",\"fields\":[{\"name\":\"seq\",\"type\":\"int\"},{\"name\":\"cust\",\"type\":\"int\",\"default\":123},{\"name\":\"emp\",\"type\":\"int\"}]}'}, {compatibility: 'FULL'}]; error code: 409"}

```
 
Register ( full compatible ) 
```
> confluent schema-registry  schema create --type AVRO --api-key A2CMSE2YBLPHRT2U --api-secret QR7Z7kMgYxe+VQStsV2knhZmCoqtxX0+tYNnF7BUhSjA+nhLX7ovBbjBLKZf934v --schema ./avro_full_good.avsc --subject avro-full-value
Successfully registered schema with ID 100011

```
#### backward compatibility test ( int to string )
Register
```
> confluent schema-registry schema create --schema avro_schema.json --subject schema_validation-value  --type avro
Successfully registered schema with ID "100024".
```
> Change a attribute type from INT to STRING

> :warning: This change is NOT allowed with any COMPATIBILITY types
 
Register in default BACKWARD compatibility
```
> confluent schema-registry schema create --schema avro_schema_typechange.json --subject schema_validation-value  --type avro
Error: Schema being registered is incompatible with an earlier schema for subject "schema_validation-value", details: [
{errorType:'TYPE_MISMATCH', description:'The type (path '/fields/1/type') of a field in the new schema does not match with the old schema', additionalInfo:'reader type: STRING not compatible with writer type: INT'},
{oldSchemaVersion: 1},
{oldSchema: '{"type":"record","name":"schema_validation","namespace":"btest.com","fields":[{"name":"foo_string","type":"string"},{"name":"foo_int","type":"int"}]}'},
{validateFields: 'true', compatibility: 'BACKWARD'}]
```
Register in default FORWARD compatibility
```
> confluent schema-registry schema create --schema avro_schema_typechange.json --subject schema_validation-value  --type avro
Error: Schema being registered is incompatible with an earlier schema for subject "schema_validation-value", details: [
{errorType:'TYPE_MISMATCH', description:'The type (path '/fields/1/type') of a field in the old schema does not match with the new schema', additionalInfo:'reader type: INT not compatible with writer type: STRING'},
{oldSchemaVersion: 1},
{oldSchema: '{"type":"record","name":"schema_validation","namespace":"btest.com","fields":[{"name":"foo_string","type":"string"},{"name":"foo_int","type":"int"}]}'},
{validateFields: 'true', compatibility: 'FORWARD'}];
error code: 409
```
Register in default FULL compatibility
```
> confluent schema-registry schema create --schema avro_schema_typechange.json --subject schema_validation-value  --type avro
Error: Schema being registered is incompatible with an earlier schema for subject "schema_validation-value", details: [
{errorType:'TYPE_MISMATCH', description:'The type (path '/fields/1/type') of a field in the old schema does not match with the new schema', additionalInfo:'reader type: INT not compatible with writer type: STRING'},
{errorType:'TYPE_MISMATCH', description:'The type (path '/fields/1/type') of a field in the new schema does not match with the old schema', additionalInfo:'reader type: STRING not compatible with writer type: INT'},
{oldSchemaVersion: 1},
{oldSchema: '{"type":"record","name":"schema_validation","namespace":"btest.com","fields":[{"name":"foo_string","type":"string"},{"name":"foo_int","type":"int"}]}'},
{validateFields: 'true', compatibility: 'FULL'}]; error code: 409
```
### Dynamic type
If a attribute has the potential to be integer or string based on an upstream event you can define the attribute as below
```
{
      "name": "foo_dynamic",
      "type": [ "null", "string", "int" ],
      "default": null
}
```
Register
```
> confluent schema-registry schema create --schema avro_schema_dynamic.json --subject schema_dynamic-value  --type avro
Successfully registered schema with ID "100026".
```
Produce
```
> kafka-avro-console-producer --bootstrap-server pkc-921jm.us-east-2.aws.confluent.cloud:9092 --producer.config java.config --topic schema_dynamic --property value.schema.id=100026 --property basic.auth.credentials.source="USER_INFO" --property schema.registry.url="https://psrc-mw0d1.us-east-2.aws.confluent.cloud" --property schema.registry.basic.auth.user.info="XXXX:XXXX"
{"foo_string":"teststr1", "foo_dynamic": {"string":"teststr2"}}
{"foo_string":"teststr1", "foo_dynamic": null}
```
Register
> Update foo_string2 to allow INT along with STRING & NULL

```
confluent schema-registry schema create --schema avro_schema_dynamic2.json --subject schema_dynamic-value  --type avro
Successfully registered schema with ID "100027".
```
Produce
```
> kafka-avro-console-producer --bootstrap-server pkc-921jm.us-east-2.aws.confluent.cloud:9092 --producer.config java.config --topic schema_dynamic --property value.schema.id=100027 --property basic.auth.credentials.source="USER_INFO" --property schema.registry.url="https://psrc-mw0d1.us-east-2.aws.confluent.cloud" --property schema.registry.basic.auth.user.info="XXXX:XXXX"
{"foo_string":"teststr1", "foo_dynamic": {"int": 2}}
{"foo_string":"teststr1", "foo_dynamic": {"string": "bla"}}
{"foo_string":"teststr1", "foo_dynamic": null}
```
