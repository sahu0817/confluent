## Contents
- [RBAC Vs ACL](#RBAC-Vs-ACL)
- [RBAC](#RBAC)
- [Kafka ACL](#Kafka-ACL)
- [Schema Registry ACL](#Schema-Registry-ACL)
  
### RBAC Vs ACL
#### Order of precedence 
Ref: https://docs.confluent.io/cloud/current/security/access-control/rbac/use-acls-with-rbac.html

In Confluent Cloud, ACLs and RBAC role bindings work together based on the following order of precedence:

- ACL DENY rules are applied first. If an ACL DENY is applied, then access is denied regardless of any ACL ALLOW rules and RBAC role bindings.
- ACL ALLOW and RBAC roles are applied. All RBAC roles are ALLOW.

When there are no ACL DENY rules that apply:
- If you only have an RBAC permission for a given resource, but not the ACL, then you have permissions for that resource.
- If you have only an ACL permission, you have permissions on the resource.
- If you have both an RBAC and ACL permission, then you have permissions on the resource.

### RBAC
RBAC lets you control access to an organization, environment, cluster, or granular Kafka resources (topics, consumer groups, and transactional IDs), Schema Registry resources, and ksqlDB resources based on predefined roles and access permissions.

#### Query principals with a certain role ( Confluent Platform ONLY )
```
> confluent iam rbac rb list  --kafka-cluster-id lw_j8rxUS22zKtvw7o2uQg --role SystemAdmin
      Principal
----------------------
  User:alice
  User:controlcenter
```
#### Query principals with OrganizationAdmin role
```
> confluent iam rbac role-binding  list --role OrganizationAdmin
    Principal    |       Name        |                   Email                     
-----------------+-------------------+---------------------------------------------                     
  User:u-1jqq8v  |                   | srsahu+svcs-central@confluent.io            
  User:u-38vnz0  |                   | jblake+svcs-central@confluent.io            
```
#### Query principals with a EnvironmentAdmin role
```
confluent iam rbac role-binding  list --role EnvironmentAdmin --environment env-381qyj
    Principal    |     Name      | Email  
-----------------+---------------+--------
  User:sa-8mz8z0 | sa_test |
```
#### Assign a FlinkDeveloper Role to a UserAccount 
```
> confluent iam rbac role-binding create --principal User:u-1jqq8v --role FlinkDeveloper --environment env-z3y7v3
+-----------+----------------------------------+
| ID        | rb-RGj20K                        |
| Principal | User:u-1jqq8v                    |
| Email     | srsahu+svcs-central@confluent.io |
| Role      | FlinkDeveloper                   |
+-----------+----------------------------------+
```
#### Assign a FlinkDeveloper Role to a UserAccount in specific computepool in a region.
```
confluent iam rbac role-binding create --principal User:u-1jqq8v --role FlinkDeveloper  --environment env-z3y7v3 --flink-region aws.us-east-2 --resource ComputePool:lfcp-mz311w
+-----------------+----------------+
| Principal       | User:u-1jqq8v  |
| Email           |                |
| Role            | FlinkDeveloper |
| Environment     |                |
| Cloud Cluster   |                |
| Cluster Type    |                |
| Logical Cluster |                |
| Resource Type   | ComputePool    |
| Name            | lfcp-mz311w    |
| Pattern Type    | LITERAL        |
+-----------------+----------------+
```
#### List all role bindings in a specific scope and its nested scopes
```
> confluent iam rbac role-binding list --principal User:u-1jqq8v  --inclusive
     ID     |   Principal   |              Email               |       Role        | Environment | Cloud Cluster | Cluster Type | Logical Cluster | Resource Type |    Name     | Pattern Type  
------------+---------------+----------------------------------+-------------------+-------------+---------------+--------------+-----------------+---------------+-------------+---------------
  rb-2RED5  | User:u-1jqq8v | srsahu+svcs-central@confluent.io | OrganizationAdmin |             |               |              |                 |               |             |               
  rb-AB2rD1 | User:u-1jqq8v | srsahu+svcs-central@confluent.io | FlinkDeveloper    | env-z3y7v3  |               |              |                 | Compute-Pool  | lfcp-mz311w | LITERAL       
  rb-MY9OeM | User:u-1jqq8v | srsahu+svcs-central@confluent.io | FlinkAdmin        | env-z3y7v3  |               |              |                 |               |             |               
  rb-Nw7mM  | User:u-1jqq8v | srsahu+svcs-central@confluent.io | FlinkDeveloper    | env-381qyj  |               |              |                 | Compute-Pool  | lfcp-19p8gv | LITERAL       
  rb-RGj20K | User:u-1jqq8v | srsahu+svcs-central@confluent.io | FlinkDeveloper    | env-z3y7v3  |               |              |                 |               |             |          
```

```
> confluent iam rbac role-binding list --principal Group:group-qkV9 --inclusive
```
#### Delete a Role
```
> confluent iam rbac role-binding  delete --principal User:u-25gwqy --role OrganizationAdmin
Are you sure you want to delete this role binding? (y/n): y
+-----------+--------------------+
| ID        | rb-43V5o           |
| Principal | User:u-25gwqy      |
| Email     | alan.xu@blabla.com |
| Role      | OrganizationAdmin  |
+-----------+--------------------+
```
```
> confluent iam rbac role-binding  delete --principal User:u-nk8jyz --role Operator --environment env-j30nww --cloud-cluster lkc-8w8ydq
Are you sure you want to delete this role binding? (y/n): y
+-----------+----------------------+
| ID        | rb-oBRAP             |
| Principal | User:u-nk8jyz        |
| Email     | yelena.wu@bla.com |
| Role      | Operator             |
+-----------+----------------------+
```
### Kafka ACL
#### CP
```
kafka-acls --bootstrap-server ec2-18-237-32-100.us-west-2.compute.amazonaws.com:9092 \
 --add \
 --allow-principal User:user1 --allow-principal User:user2 \
 --operation read --operation write \
 --topic acl-test
```

#### CC
```
kafka-acls --bootstrap-server pkc-ymrq7.us-east-2.aws.confluent.cloud:9092 --command-config java.config --add --allow-principal User:u-1jqq8v --operation DESCRIBE --operation READ --operation WRITE --topic _confluent-command
Adding ACLs for resource `ResourcePattern(resourceType=TOPIC, name=_confluent-command, patternType=LITERAL)`:
        (principal=User:u-1jqq8v, host=*, operation=READ, permissionType=ALLOW)
        (principal=User:u-1jqq8v, host=*, operation=WRITE, permissionType=ALLOW)
        (principal=User:u-1jqq8v, host=*, operation=DESCRIBE, permissionType=ALLOW)

Current ACLs for resource `ResourcePattern(resourceType=TOPIC, name=_confluent-command, patternType=LITERAL)`:
        (principal=User:898344, host=*, operation=READ, permissionType=ALLOW)
        (principal=User:898344, host=*, operation=DESCRIBE, permissionType=ALLOW)
        (principal=User:898344, host=*, operation=WRITE, permissionType=ALLOW)
```
List ACLs for a User
```
> confluent kafka acl list --principal User:sa-g9w081
    Principal    | Permission | Operation | Resource Type | Resource Name | Pattern Type  
-----------------+------------+-----------+---------------+---------------+---------------
  User:sa-g9w081 | ALLOW      | CREATE    | TOPIC         | data-preview  | PREFIXED      
  User:sa-g9w081 | ALLOW      | DESCRIBE  | CLUSTER       | kafka-cluster | LITERAL       
  User:sa-g9w081 | ALLOW      | WRITE     | TOPIC         | data-preview  | PREFIXED      
  User:sa-g9w081 | ALLOW      | WRITE     | TOPIC         | datagen-topic | LITERAL 
```
Deny Access to a topic for a user
```
> kafka-avro-console-producer --bootstrap-server pkc-ryzn9.westus3.azure.confluent.cloud:9092 --topic abs_avro --producer.config java.config  --property key.serializer=org.apache.kafka.common.serialization.StringSerializer --property parse.key=true --property key.separator=, --property value.schema.file=./cnum.avsc --property schema.registry.url=https://psrc-lq2dm.us-east-2.aws.confluent.cloud  --property basic.auth.credentials.source="USER_INFO" --property schema.registry.basic.auth.user.info="XXXXXXXXX"
one,{"cnum": 1, "cname": "srini"}

> confluent kafka acl create --principal User:sa-r0ddv1 --deny --operations write --topic abs_avro
    Principal    | Permission | Operation | Resource Type | Resource Name | Pattern Type  
-----------------+------------+-----------+---------------+---------------+---------------
  User:sa-r0ddv1 | DENY       | WRITE     | TOPIC         | abs_avro      | LITERAL

> kafka-avro-console-producer --bootstrap-server pkc-ryzn9.westus3.azure.confluent.cloud:9092 --topic abs_avro --producer.config java.config  --property key.serializer=org.apache.kafka.common.serialization.StringSerializer --property parse.key=true --property key.separator=, --property value.schema.file=./cnum.avsc --property schema.registry.url=https://psrc-lq2dm.us-east-2.aws.confluent.cloud  --property basic.auth.credentials.source="USER_INFO" --property schema.registry.basic.auth.user.info="XXXXXXXXX"
two,{"cnum": 2, "cname": "srini"}
[2024-04-26 19:54:49,680] ERROR Error when sending message to topic abs_avro with key: 3 bytes, value: 12 bytes with error: (org.apache.kafka.clients.producer.internals.ErrorLoggingCallback:52)
org.apache.kafka.common.errors.TopicAuthorizationException: Not authorized to access topics: [abs_avro]  
```

Delete ACL that was created to deny access
```
> confluent kafka acl delete --principal User:sa-r0ddv1 --deny --operations write --topic abs_avro
Are you sure you want to delete the ACL corresponding to these parameters? (y/n): y
Deleted 1 ACL.

> kafka-avro-console-producer --bootstrap-server pkc-ryzn9.westus3.azure.confluent.cloud:9092 --topic abs_avro --producer.config java.config  --property key.serializer=org.apache.kafka.common.serialization.StringSerializer --property parse.key=true --property key.separator=, --property value.schema.file=./cnum.avsc --property schema.registry.url=https://psrc-lq2dm.us-east-2.aws.confluent.cloud  --property basic.auth.credentials.source="USER_INFO" --property schema.registry.basic.auth.user.info="XXXXXXXXX"
two,{"cnum": 2, "cname": "srini"}
```

### Schema Registry ACL
#### CP Local
List Schema Registry ACLs
```
> sr-acl-cli --config sr_local.properties --list

[2024-07-11 16:11:38,051] WARN Creating the schema topic _schemas_acl using a replication factor of 1, which is less than the desired one of 3. If this is a production environment, it's crucial to add more brokers and increase the replication factor of the topic. (io.confluent.kafka.schemaregistry.security.authorizer.schemaregistryacl.SchemaRegistryAclAuthorizerUtils:161)
Current ACL's for Subject Operations are
{}
Current ACL's for Global Operations are
{}
[2024-07-11 16:11:38,908] ERROR [Consumer clientId=schema-registry-acl-reader, groupId=sr-acl-cli] Unable to find FetchSessionHandler for node 0. Ignoring fetch response. (org.apache.kafka.clients.consumer.internals.AbstractFetch:128)
```

#### CFK GKE
Add
```
> sr-acl-cli --config sr_cfk.properties --add -o SUBJECT_READ -o SUBJECT_WRITE -s bob-value -p Bob
[2024-07-12 01:00:34,504] ERROR [Consumer clientId=schema-registry-acl-reader, groupId=sr-acl-cli] Unable to find FetchSessionHandler for node 0. Ignoring fetch response. (org.apache.kafka.clients.consumer.internals.AbstractFetch:128)
```
List
```
> sr-acl-cli --config sr_cfk.properties --list
Current ACL's for Subject Operations are
{Bob={bob-value=[SUBJECT_READ, SUBJECT_WRITE]}}
Current ACL's for Global Operations are
{}
[2024-07-12 01:00:54,579] ERROR [Consumer clientId=schema-registry-acl-reader, groupId=sr-acl-cli] Unable to find FetchSessionHandler for node 0. Ignoring fetch response. (org.apache.kafka.clients.consumer.internals.AbstractFetch:128)
```
