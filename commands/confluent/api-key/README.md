## confluent api-key management

### Create Keys
#### Create a api-key for cloud resource
```
> confluent api-key create --resource cloud --service-account sa-wy876j
 
+---------+------------------------------------------------------------------+
| API Key | GYT5T7EQEXXXXXXX                                                 |
| Secret  | LZ9BVu0L0aVdf2ZTy0u/W0FmSBzEZzlabd6uyfsHk16Ll316armjgMXXXXXXXXXX |
+---------+------------------------------------------------------------------+
```
#### Create a api-key for kafka cluster resource in the cloud
```
> confluent api-key create --resource lkc-1w9gn5 --service-account sa-wy876j
 
+---------+------------------------------------------------------------------+
| API Key | WNYAZYTXXXXXXX                                                   |
| Secret  | aXuVu0L0aVdf2ZTy0u/W0FmSBzEZzlabd6uyfsHk16Ll316armjgMXXXXXXXXXX |
+---------+------------------------------------------------------------------+
```
#### Create a api-key for flink resource
```
> confluent api-key create  --resource flink --cloud aws --region us-east-2
 
+------------+------------------------------------------------------------------+
| API Key    | GLDYNOO4QXXXXXXX                                                 |
| API Secret | UgTNvB6VX03+qKT7Eaq7Os6lJEyF+/roKfnJm7t/NTe6v/SrlhXXXXXXXXXXXXXX |
+------------+------------------------------------------------------------------+
```

### Manage Keys
#### List api-keys
```
> confluent api-key list
         Key         |          Description           | Owner Resource ID |             Owner Email             |  Resource Type  | Resource ID |       Created         
---------------------+--------------------------------+-------------------+-------------------------------------+-----------------+-------------+-----------------------
    HEJQCJNVASQXXXXX |                                | u-1jqq8v          | blabla@confluent.io                 | kafka           | lkc-1w9gn5  | 2023-12-01T02:25:14Z  
```
#### Store api-key
```
> confluent api-key store TYH4MQRMJBWWIYS3
Secret: ****************************************************************

Stored secret for API key "TYH4MQRMJBWWIYS3".
```
#### Use api-key
> Need to store first to use a api-key in a session with confluent cloud
```
> confluent api-key use TYH4MQRMJBWWIYS3
Using API Key "TYH4MQRMJBWWIYS3".
```

