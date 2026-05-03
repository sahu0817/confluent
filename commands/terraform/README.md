### Show the provider schema
```
 terraform providers schema -json | jq
```
### Show the state
```
[ubuntu@awst2x ~/terraform/flink/statement/create]# terraform state show confluent_flink_statement.create-dim-roles-2
# confluent_flink_statement.create-dim-roles-2:
resource "confluent_flink_statement" "create-dim-roles-2" {
    id                       = "env-y65pxp/lfcp-wpomgw/ddl-dim-roles-2"
    latest_offsets           = {}
    latest_offsets_timestamp = "0001-01-01T00:00:00Z"
    properties               = {
        "sql.current-catalog"  = "srinivas"
        "sql.current-database" = "test"
    }
    statement                = <<-EOT
        CREATE TABLE IF NOT EXISTS dim_roles_2 (
            role_sid STRING,
            id STRING,
            name STRING,
            description STRING,
            create_date TIMESTAMP(3),
            create_by STRING,
            view_only BOOLEAN,
            role_visible BOOLEAN,
            tenant_id STRING,
            roles_tenant_id STRING,
            __ts_ms BIGINT,
            dl_landed_at TIMESTAMP(3),
            PRIMARY KEY(id) NOT ENFORCED -- VERIFY KEY
        ) WITH (
          'changelog.mode' = 'upsert',
          'value.format' = 'avro-registry',
          'value.fields-include' = 'all'
        );
    EOT
    statement_name           = "ddl-dim-roles-2"
    stopped                  = false
}
```
