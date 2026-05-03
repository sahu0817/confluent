## Flink Rest API
#### List Regions
```
curl --request GET \
--url 'https://api.confluent.cloud/fcpm/v2/regions?cloud=AWS' \
--header 'Authorization: Basic '$CLOUD_AUTH64'' --header 'content-type: application/json'
```
<details>
  <summary>Output</summary>
  
  ```js
{
  "api_version": "fcpm/v2",
  "data": [
    {
      "api_version": "fcpm/v2",
      "cloud": "AWS",
      "display_name": "Mumbai (ap-south-1)",
      "http_endpoint": "https://flink.ap-south-1.aws.confluent.cloud",
      "id": "aws.ap-south-1",
      "kind": "Region",
      "metadata": {
        "self": ""
      },
      "region_name": "ap-south-1"
    },
    {
      "api_version": "fcpm/v2",
      "cloud": "AWS",
      "display_name": "Singapore (ap-southeast-1)",
      "http_endpoint": "https://flink.ap-southeast-1.aws.confluent.cloud",
      "id": "aws.ap-southeast-1",
      "kind": "Region",
      "metadata": {
        "self": ""
      },
      "region_name": "ap-southeast-1"
    },
    {
      "api_version": "fcpm/v2",
      "cloud": "AWS",
      "display_name": "Sydney (ap-southeast-2)",
      "http_endpoint": "https://flink.ap-southeast-2.aws.confluent.cloud",
      "id": "aws.ap-southeast-2",
      "kind": "Region",
      "metadata": {
        "self": ""
      },
      "region_name": "ap-southeast-2"
    },
    {
      "api_version": "fcpm/v2",
      "cloud": "AWS",
      "display_name": "Frankfurt (eu-central-1)",
      "http_endpoint": "https://flink.eu-central-1.aws.confluent.cloud",
      "id": "aws.eu-central-1",
      "kind": "Region",
      "metadata": {
        "self": ""
      },
      "region_name": "eu-central-1"
    },
    {
      "api_version": "fcpm/v2",
      "cloud": "AWS",
      "display_name": "Ireland (eu-west-1)",
      "http_endpoint": "https://flink.eu-west-1.aws.confluent.cloud",
      "id": "aws.eu-west-1",
      "kind": "Region",
      "metadata": {
        "self": ""
      },
      "region_name": "eu-west-1"
    },
    {
      "api_version": "fcpm/v2",
      "cloud": "AWS",
      "display_name": "London (eu-west-2)",
      "http_endpoint": "https://flink.eu-west-2.aws.confluent.cloud",
      "id": "aws.eu-west-2",
      "kind": "Region",
      "metadata": {
        "self": ""
      },
      "region_name": "eu-west-2"
    },
    {
      "api_version": "fcpm/v2",
      "cloud": "AWS",
      "display_name": "N. Virginia (us-east-1)",
      "http_endpoint": "https://flink.us-east-1.aws.confluent.cloud",
      "id": "aws.us-east-1",
      "kind": "Region",
      "metadata": {
        "self": ""
      },
      "region_name": "us-east-1"
    },
    {
      "api_version": "fcpm/v2",
      "cloud": "AWS",
      "display_name": "Ohio (us-east-2)",
      "http_endpoint": "https://flink.us-east-2.aws.confluent.cloud",
      "id": "aws.us-east-2",
      "kind": "Region",
      "metadata": {
        "self": ""
      },
      "region_name": "us-east-2"
    },
    {
      "api_version": "fcpm/v2",
      "cloud": "AWS",
      "display_name": "Oregon (us-west-2)",
      "http_endpoint": "https://flink.us-west-2.aws.confluent.cloud",
      "id": "aws.us-west-2",
      "kind": "Region",
      "metadata": {
        "self": ""
      },
      "region_name": "us-west-2"
    }
  ],
  "kind": "RegionList",
  "metadata": {
    "first": "",
    "next": "",
    "total_size": 9
  }
}
  ```
</details>

#### List Statements in your env
> api-key creation
>> confluent api-key create  --resource flink --cloud aws --region us-east-1 --service-account sa-g9w081

> RBAC of svc_account
>> FlinkAdmin 
```
curl --request GET --url 'https://flink.us-east-1.aws.confluent.cloud/sql/v1beta1/organizations/4c8541f7-cc3f-44af-a366-ad4de432fe24/environments/env-r0vjz9/statements'
--header 'Authorization: Basic '$FLINK_AUTH64'' --header 'content-type: application/json' | jq
```
<details>
  <summary>Output</summary>
  
```js
{
  "api_version": "sql/v1beta1",
  "data": [
    {
      "api_version": "sql/v1beta1",
      "environment_id": "env-r0vjz9",
      "kind": "Statement",
      "metadata": {
        "created_at": "2024-05-22T16:33:29.075221Z",
        "resource_version": "51",
        "self": "https://flink.us-east-1.aws.confluent.cloud/sql/v1beta1/organizations/4c8541f7-cc3f-44af-a366-ad4de432fe24/environments/env-r0vjz9/statements/workspace-2024-05-22-162403-02fd9115-ed40-487e-a8a9-d165d6a9fabb",
        "uid": "b5a806f5-b818-4408-b6c0-7f6fd7da6eb2",
        "updated_at": "2024-05-22T16:34:18.395358Z"
      },
      "name": "workspace-2024-05-22-162403-02fd9115-ed40-487e-a8a9-d165d6a9fabb",
      "organization_id": "4c8541f7-cc3f-44af-a366-ad4de432fe24",
      "spec": {
        "compute_pool_id": "lfcp-1d5rwj",
        "principal": "u-1jqq8v",
        "properties": {
          "sql.current-catalog": "handson-flink",
          "sql.current-database": "handson-flink",
          "sql.local-time-zone": "GMT-05:00"
        },
        "statement": "SELECT COUNT(DISTINCT id) AS num_customers FROM shoe_customers;",
        "stopped": true
      },
      . . .
{
      "api_version": "sql/v1beta1",
      "environment_id": "env-r0vjz9",
      "kind": "Statement",
      "metadata": {
        "created_at": "2024-05-22T21:53:59.675622Z",
        "resource_version": "8",
        "self": "https://flink.us-east-1.aws.confluent.cloud/sql/v1beta1/organizations/4c8541f7-cc3f-44af-a366-ad4de432fe24/environments/env-r0vjz9/statements/workspace-2024-05-22-162403-38d10dd4-19fe-4fad-9b20-1dbd61a38e94",
        "uid": "81411fa5-839b-493c-b41e-385d727e9399",
        "updated_at": "2024-05-22T21:54:02.642524Z"
      },
      "name": "workspace-2024-05-22-162403-38d10dd4-19fe-4fad-9b20-1dbd61a38e94",
      "organization_id": "4c8541f7-cc3f-44af-a366-ad4de432fe24",
      "spec": {
        "compute_pool_id": "lfcp-1d5rwj",
        "principal": "u-1jqq8v",
        "properties": {
          "sql.current-catalog": "handson-flink",
          "sql.current-database": "handson-flink",
          "sql.local-time-zone": "GMT-05:00"
        },
        "statement": "CREATE TABLE shoe_order_customer_product( order_id INT, first_name STRING, last_name STRING, email STRING, brand STRING, `model` STRING, sale_price INT, rating DOUBLE )WITH ( 'changelog.mode' = 'retract' );",
        "stopped": false
      },
      "status": {
        "detail": "Table 'shoe_order_customer_product' created",
        "phase": "COMPLETED",
        "result_schema": {}
      }
    }
  ],
  "kind": "StatementList",
  "metadata": {
    "next": "https://flink.us-east-1.aws.confluent.cloud/sql/v1beta1/organizations/4c8541f7-cc3f-44af-a366-ad4de432fe24/environments/env-r0vjz9/statements?page_size=10&page_token=d3JhcHBlcg-eyJ2Ijoic3RvcmFnZW1ldGEvdjIiLCJjb250aW51ZVRva2VuIjoiU3RhdGVtZW50LnNxbCMwIzRjODU0MWY3LWNjM2YtNDRhZi1hMzY2LWFkNGRlNDMyZmUyNCNlbnYtcjB2ano5LHdvcmtzcGFjZS0yMDI0LTA1LTIyLTE2MjQwMy0zOGQxMGRkNC0xOWZlLTRmYWQtOWIyMC0xZGJkNjFhMzhlOTQiLCJ2YWxpZGF0aW9uVG9rZW4iOiIyMDhmNGZiMzUyNjgyY2Q3Zjc2ZTRlZTk5YmUxMjBlNGEzNWQ0ZjRhZTlhYTg1OGE5ZTVkNTQ2NzU5YjA0MmM0In0",
    "self": "https://flink.us-east-1.aws.confluent.cloud/sql/v1beta1/organizations/4c8541f7-cc3f-44af-a366-ad4de432fe24/environments/env-r0vjz9/statements?page_size=10"
  }
}
  ```
</details>

#### Update Statement 
```
curl --request PUT \
--url 'https://flink.us-east-2.aws.confluent.cloud/sql/v1beta1/organizations/4c8541f7-cc3f-44af-a366-ad4de432fe24/environments/env-z3y7v3/statements/flink-test' \
--header 'Authorization: Basic '$FLINK_AUTH64'' \
--header 'content-type: application/json' \
--data '@statement_update.json'
```
