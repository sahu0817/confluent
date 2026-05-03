### RoleBindings API
#### List RoleBindings at ORG level

```
> curl -X GET -H “accept: application/json” -H “Authorization: Basic $CLOUD_AUTH” -H “Content-Type: application/json” “https://confluent.cloud/api/iam/v2/role-bindings?crn_pattern=crn://confluent.cloud/organization=$ORG/*”
```
<details>
  <summary>Output</summary>
  
```js
{
  "api_version": "iam/v2",
  "kind": "RoleBindingList",
  "data": [
    {
      "api_version": "iam/v2",
      "kind": "RoleBinding",
      "id": "rb-1b9ry",
      "principal": "User:pool-R6ma",
      "role_name": "CloudClusterAdmin",
      "crn_pattern": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-1968p5/cloud-cluster=lkc-1wop5z",
      "metadata": {
        "self": "https://confluent.cloud/api/iam/v2/role-bindings/rb-1b9ry",
        "created_at": "2023-12-12T17:12:56.632057Z"
      }
    },
    {
      "api_version": "iam/v2",
      "kind": "RoleBinding",
      "id": "rb-1LK2wb",
      "principal": "User:sa-n36236",
      "role_name": "CloudClusterAdmin",
      "crn_pattern": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-1968p5/cloud-cluster=lkc-k6y86g",
      "metadata": {
        "self": "https://confluent.cloud/api/iam/v2/role-bindings/rb-1LK2wb",
        "created_at": "2024-06-06T15:33:33.453141Z"
      }
    },
. . .
    {
      "api_version": "iam/v2",
      "kind": "RoleBinding",
      "id": "u-ymjk3o3077-m",
      "principal": "User:u-ymjk3o",
      "role_name": "FlinkDeveloper",
      "crn_pattern": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-381qyj",
      "metadata": {
        "self": "https://confluent.cloud/api/iam/v2/role-bindings/u-ymjk3o3077-m",
        "created_at": "2024-03-14T23:48:47.422591Z"
      }
    }
  ],
  "metadata": {}
}
```
<details>
