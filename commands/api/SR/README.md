## Contents
- [List Subjects](#List-Subjects)
- [Fetch latest version of schema](#Fetch-latest-version-of-schema)
- [Provision schema](#Provision-schema)
- [Provision schema in specific context](#Provision-schema-in-specific-context)
- [Get schema compatibility mode](#Get-schema-compatibility-mode)
- [Get compatibility for specific schema](#Get-compatibility-for-specific-schema)
- [Change compatibility level](#Change-compatibility-level)
- [Delete Schema](#Delete-Schema)
- [List contexts](#List-contexts)
- [List context subjects](#List-context-subjects)
- [Delete Context](#Delete-Context)
- [Delete Schema in specific context](#Delete-Schema-in-specific-context)
- [Update Context Mode](#Update-Context-Mode)
- [Get Context Mode](#Get-Context-Mode)

### Schema Registry APIs
#### List Subjects
```
curl --request GET \
--url 'https://psrc-4r3n1.us-central1.gcp.confluent.cloud/subjects' \
--header 'Authorization: Basic '$SR_AUTH64'' | jq '.'
```

#### Fetch latest version of schema
```
curl --request GET \
--url 'https://psrc-4r3n1.us-central1.gcp.confluent.cloud/${subject}/versions/latest' \
--header 'Authorization: Basic '$SR_AUTH64'' | jq '.'
```
#### Provision schema
```
curl -s --request POST \
--url 'https://psrc-4r3n1.us-central1.gcp.confluent.cloud/subjects/${schema_name}/versions' \
--header 'Authorization: Basic '$SR_AUTH64'' \
--header 'Content-Type: application/vnd.schemaregistry.v1+json' \
--data "@avro_schema.json" | jq '.'
```
#### Provision schema in specific context
```
schema_name="srini_test-value"
context=".dev"
#
curl -s --request POST \
--url "https://psrc-1ymy5nj.us-east-1.aws.confluent.cloud/contexts/${context}/subjects/${schema_name}/versions" \
--header 'Authorization: Basic '$SR_AUTH64'' \
--header 'Content-Type: application/vnd.schemaregistry.v1+json' \
--data "@avro_schema.json" | jq '.'
```
```
{
  "id": 100003
}
```
⚠️If you provision a schema in a context that is in IMPORT mode you get this error
```
{
  "error_code": 42205,
  "message": "Subject :.lrhk1SFkTiGqVHZGvWQXgA-schema-registry:srini_test-value in context :.lrhk1SFkTiGqVHZGvWQXgA-schema-registry: is not in read-write mode; error code: 42205"
}
```
#### Get schema compatibility mode
```
curl --request GET \
--url 'https://psrc-ry0y7.centralus.azure.confluent.cloud/config' \
--header 'Authorization: Basic '$SR_AUTH64''

{
  "compatibilityLevel": "BACKWARD"
}
```

#### Get compatibility for specific schema
When no explicit compatibility is set for the schema ( default global compatibilithy )
```
curl --request GET \
--url 'https://psrc-ry0y7.centralus.azure.confluent.cloud/config/firsttopic-value' \
--header 'Authorization: Basic '$SR_AUTH64''
{
  "error_code": 40408,
  "message": "Subject 'firsttopic-value' does not have subject-level compatibility configured"
}
```
##### Change compatibility level
Change to 'FORWARD'
```
curl --request GET \
--url 'https://psrc-ry0y7.centralus.azure.confluent.cloud/config/firsttopic-value' \
--header 'Authorization: Basic '$SR_AUTH64''
{
  "compatibilityLevel": "FORWARD"
}
```

#### Delete Schema
> [!WARNING] 
> You will run into this error if you do a hard delete ( ?permanent=true ) before you Soft delete first 
```
{
  "error_code": 40405,
  "message": "Subject 'srini-csfle-demo-value' was not deleted first before being permanently deleted; error code: 40405"
}
```
```
curl -s --request DELETE \
--url 'https://psrc-4r3n1.us-central1.gcp.confluent.cloud/subjects/'${schema_name}'?permanent=true' \
--header 'Authorization: Basic '$SR_AUTH'' \
--header 'Content-Type: application/vnd.schemaregistry.v1+json' | jq '.'
```
<details>
  <summary>Output</summary>
  
  ```js 
[
  1,
  2
]
```
</details>

#### List contexts
```
curl --request GET --url 'https://psrc-1ymy5nj.us-east-1.aws.confluent.cloud/contexts' --header 'Authorization: Basic '$SR_AUTH64'' | jq '.'
```
<details>
  <summary>Output</summary>
  
  ```js 
[
  ".",
  ".2s-ZvivKThqEOl4dqvxGEA-schema-registry",
  ".clone",
  ".dev",
  ".lrhk1SFkTiGqVHZGvWQXgA-schema-registry",
  ".stg"
]
```
</details>

#### List context subjects
```
context=".clone"
curl --request GET \
--url "https://psrc-1ymy5nj.us-east-1.aws.confluent.cloud/subjects?subjectPrefix=:${context}" \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic '$SR_AUTH64'' | jq '.'
```
ℹ️ when using $variables in --url enclose in DOUBLE QUOTES

<details>
  <summary>Output</summary>
  
  ```js 
[
  ":.clone:clone_sample_data_users-value"
]
```
</details>

#### Delete context
```
context=".clone"

curl --request DELETE \
--url "https://psrc-1ymy5nj.us-east-1.aws.confluent.cloud/contexts/${context}" \
--header 'Authorization: Basic '$SR_AUTH64''
```
<details>
  <summary>Output</summary>
  
  ```js 
{"error_code":42211,"message":"The specified context ':.clone:' is not empty."}
```
</details>

:warning: Schema context cannot be delete when there are subjects in the context. Delete all the subjects first.


#### Delete Schema in specific context
Do a SOFT delete
```
export subject=':.clone:clone_sample_data_users-value'
curl -s --request DELETE \
--url 'https://psrc-1ymy5nj.us-east-1.aws.confluent.cloud/subjects/'${subject}'' \
--header 'Authorization: Basic '$SR_AUTH'' \
--header 'Content-Type: application/vnd.schemaregistry.v1+json' | jq '.'
```
<details>
  <summary>Output</summary>
  
  ```js 
[1]
```
</details>

Do a HARD delete
```
curl -s --request DELETE \
--url 'https://psrc-1ymy5nj.us-east-1.aws.confluent.cloud/subjects/'${subject}'?permanent=true' \
--header 'Authorization: Basic '$SR_AUTH'' \
--header 'Content-Type: application/vnd.schemaregistry.v1+json' | jq '.'
```
<details>
  <summary>Output</summary>
  
  ```js 
[1]
```
</details>

#### Update Context mode
READWRITE mode
```
subject=":.2s-ZvivKThqEOl4dqvxGEA-schema-registry"

curl --request PUT \
--url 'https://psrc-1ymy5nj.us-east-1.aws.confluent.cloud/mode/${subject}' \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic '$SR_AUTH64'' \
--data '{"mode": "READWRITE"}' | jq '.'
```
<details>
  <summary>Output</summary>
  
  ```js 
{
  "mode": "READWRITE"
}
```
</details>

IMPORT mode

```
subject=":.2s-ZvivKThqEOl4dqvxGEA-schema-registry"

curl --request PUT \
--url 'https://psrc-1ymy5nj.us-east-1.aws.confluent.cloud/mode/${subject}' \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic '$SR_AUTH64'' \
--data '{"mode": "IMPORT"}' | jq '.'
```
<details>
  <summary>Output</summary>
  
  ```js 
{
  "mode": "IMPORT"
}
```
</details>

#### Get Context mode
```
subject=":.2s-ZvivKThqEOl4dqvxGEA-schema-registry"

curl --request GET \
--url 'https://psrc-1ymy5nj.us-east-1.aws.confluent.cloud/mode/${subject}' \
--header 'Authorization: Basic '$SR_AUTH64'' | jq '.'
```
<details>
  <summary>Output</summary>
  
  ```js 
{
  "mode": "IMPORT"
}
```
</details>


