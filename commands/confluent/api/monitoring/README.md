## Confluent Cloud Monitoring REST API

## Contents
- [ClusterLink Lag monitor](#ClusterLink-Lag-monitor)
- [Active-Connections-Count-by-User](#Active-Connections-Count-by-User)
- [Request Count by user](#Request-Count-by-user)
- [Calculate monthly costs by team](#Calculate-monthly-costs-by-team)
- [FFF ZoneAlignment monitor](#FFF-ZoneAlignment-monitor)
  
#### ClusterLink Lag monitor
```
curl --request POST \
--url 'https://api.telemetry.confluent.cloud/v2/metrics/cloud/query' \
--header 'Authorization: Basic '$CLOUD_AUTH64'' \
--header 'content-type: application/json' \
--data @clusterlink_lag.json

{
  "data": []
}
```

#### Active Connections Count by User
```
> curl --request POST \
--url 'https://api.telemetry.confluent.cloud/v2/metrics/cloud/query' \
--header 'Authorization: Basic '$CLOUD_AUTH64'' \
--header 'content-type: application/json' \
--data "@connection_attempts_user.json"
```
<details>
  <summary>Output</summary>
  
```js
{
  "data": [
    {
      "timestamp": "2024-05-08T00:00:00Z",
      "value": 29.316666666666666,
      "metric.principal_id": "sa-r0ddv1"
    },
    {
      "timestamp": "2024-05-08T00:00:00Z",
      "value": 4.316666666666666,
      "metric.principal_id": "u-1jqq8v"
    },
    {
      "timestamp": "2024-05-08T00:00:00Z",
      "value": 0,
      "metric.principal_id": "u-3wp1k0"
    },
    {
      "timestamp": "2024-05-08T00:00:00Z",
      "value": 0,
      "metric.principal_id": "u-4nrxr6"
    }
  ]
}

```
</details>

#### Request Count by user
```
> curl --request POST \
--url 'https://api.telemetry.confluent.cloud/v2/metrics/cloud/query' \
--header 'Authorization: Basic '$CLOUD_AUTH64'' \
--header 'content-type: application/json' \
--data "@request_count_user.json"
```
<details>
  <summary>Output</summary>
  
```js
{
  "data": [
    {
      "metric.principal_id": "u-1jqq8v",
      "points": [
        {
          "timestamp": "2024-06-21T02:00:00Z",
          "value": 5046
        },
        {
          "timestamp": "2024-06-21T03:00:00Z",
          "value": 15933
        },
        {
          "timestamp": "2024-06-21T04:00:00Z",
          "value": 15936
        },
        {
          "timestamp": "2024-06-21T05:00:00Z",
          "value": 15933
        },
        {
          "timestamp": "2024-06-21T06:00:00Z",
          "value": 15933
        },
        {
          "timestamp": "2024-06-21T07:00:00Z",
          "value": 15929
        },
        {
          "timestamp": "2024-06-21T08:00:00Z",
          "value": 15931
        },
        {
          "timestamp": "2024-06-21T09:00:00Z",
          "value": 15931
        },
        {
          "timestamp": "2024-06-21T10:00:00Z",
          "value": 15938
        },
        {
          "timestamp": "2024-06-21T11:00:00Z",
          "value": 15934
        },
        {
          "timestamp": "2024-06-21T12:00:00Z",
          "value": 15933
        },
        {
          "timestamp": "2024-06-21T13:00:00Z",
          "value": 15939
        },
        {
          "timestamp": "2024-06-21T14:00:00Z",
          "value": 15933
        },
        {
          "timestamp": "2024-06-21T15:00:00Z",
          "value": 15926
        },
        {
          "timestamp": "2024-06-21T16:00:00Z",
          "value": 15928
        },
        {
          "timestamp": "2024-06-21T17:00:00Z",
          "value": 15938
        },
        {
          "timestamp": "2024-06-21T18:00:00Z",
          "value": 10894
        }
      ]
    }
  ]
}

```
</details>

#### Calculate monthly costs by team
To track usage by team, you assign each unique team/application its own service account. Then you use the Metrics API and filter results using the principal_id label to separate usage by service account. You track and sum this usage on a monthly basis, and use it to create a derived showback of costs for each service account.
```
> curl --location --request POST   --url 'https://api.telemetry.confluent.cloud/v2/metrics/cloud/query' --header 'Authorization: Basic '${CLOUD_AUTH64}'' --header 'Content-Type: application/json' --data-raw '{
"aggregations": [
  {
      "metric": "io.confluent.kafka.server/request_bytes"
  }
],
"filter": {
  "field": "resource.kafka.id",
  "op": "EQ",
  "value": "lkc-3w6270"
},
"granularity": "P1D",
"group_by": [
  "metric.principal_id"
],
"intervals": [
    "2024-04-29T00:00:00-00:00/P1D"
],
"limit": 1000
}'
```
<details>
  <summary>Output</summary>
 
```js 
{
  "data": [
    {
      "timestamp": "2024-04-29T00:00:00Z",
      "value": 28769158,
      "metric.principal_id": "u-1jqq8v"
    },
    {
      "timestamp": "2024-04-29T00:00:00Z",
      "value": 752,
      "metric.principal_id": "u-j580mp"
    }
  ]
}
```
</details> 

#### FFF ZoneAlignment monitor
To determine how clients connected to your cluster are utilizing bandwidth - Fetch From Follower.
```
> curl --location --request POST   --url 'https://api.telemetry.confluent.cloud/v2/metrics/cloud/query' --header 'Authorization: Basic '${CLOUD_AUTH64}'' --header 'Content-Type: application/json' --data-raw '{
   "aggregations": [
      {
         "metric": "io.confluent.kafka.server/response_bytes"
      }
   ],
   "filter": {
      "op": "AND",
      "filters": [
         {
         "field": "resource.kafka.id",
         "op": "EQ",
         "value": "lkc-1w9gn5"
         },
         {
         "field": "metric.type",
         "op": "EQ",
         "value": "Fetch"
         }
      ]
   },
   "group_by": [
      "metric.zone_alignment",
      "metric.principal_id"
   ],
   "granularity": "PT30M",
   "intervals": [
   "2024-09-13T18:30:00Z/PT1H"
   ],
   "limit": 1000
}
'
```
When cluster is not FFF enabled
<details>
  <summary>Output</summary>
 
```js
{
  "data": [
    {
      "timestamp": "2024-09-13T19:30:00Z",
      "value": 0,
      "metric.principal_id": "u-1jqq8v"
    },
    {
      "timestamp": "2024-09-13T20:00:00Z",
      "value": 0,
      "metric.principal_id": "u-1jqq8v"
    }
  ]
}
```
</details>
When cluster is FFF enabled
<details>
  <summary>Output</summary>
 
```js
{
   "timestamp": "2024-09-13T19:30:00Z",
   "value": 76,
   "metric.principal_id": "u-1jqq8v",
   "metric.zone_alignment": "CROSS_ZONE"
}
{
   "timestamp": "2024-09-13T19:30:00Z",
   "value": 11535077,
   "metric.principal_id": "u-2qzav",
   "metric.zone_alignment": "SAME_ZONE"
}
{
   "timestamp": "2024-09-13T19:30:00Z",
   "value": 7340578,
   "metric.principal_id": "u-1jqq8v",
   "metric.zone_alignment": "UNKNOWN"
}
```
</details>
