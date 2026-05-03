terraform {
  required_providers {
    confluent = {
      source  = "confluentinc/confluent"
      version = "2.59.0"
    }
  }
}

provider "confluent" {
  cloud_api_key    = var.confluent_cloud_api_key
  cloud_api_secret = var.confluent_cloud_api_secret
}

# Existing environment
data "confluent_environment" "env" {
  id = var.confluent_cloud_env_id
}

# Existing Dedicated cluster
data "confluent_kafka_cluster" "cluster" {
  id = var.confluent_cloud_kafka_cluster_id

  environment {
    #id = data.confluent_environment.env.id
    id = var.confluent_cloud_env_id
  }
}

# Existing Schema Registry cluster
data "confluent_schema_registry_cluster" "schema-registry" {
  environment {
    id = data.confluent_environment.env.id
  }
}

locals {
  topic_acl_ops = [
    "READ",
    "WRITE",
    "DELETE",
  ]
}

resource "confluent_service_account" "service-account" {
  display_name = "${var.connector_name}"
  description  = "Service account for connector access to kafka topics, consumergroups etc"
}

#--- Need this to create ACLs on DLQ topic ( This is not needed as ACLs are not needed, RBACs should do. Bug: tracked by ??? )
resource "confluent_role_binding" "cloud-cluster-admin-for-acl" {
  depends_on  = [confluent_service_account.service-account]
  principal   = "User:${confluent_service_account.service-account.id}"
  role_name   = "CloudClusterAdmin"
  crn_pattern = "${data.confluent_kafka_cluster.cluster.rbac_crn}"
}

#--- DeveloperWrite ????
resource "confluent_role_binding" "connector-developer-write" {
  depends_on  = [confluent_service_account.service-account]
  principal   = "User:${confluent_service_account.service-account.id}"
  role_name   = "DeveloperWrite"
  crn_pattern = "${data.confluent_kafka_cluster.cluster.rbac_crn}/kafka=${data.confluent_kafka_cluster.cluster.id}/topic=${var.connector_topic}"
}

#--- DeveloperWrite
resource "confluent_role_binding" "connector-developer-read" {
  depends_on  = [confluent_service_account.service-account]
  principal   = "User:${confluent_service_account.service-account.id}"
  role_name   = "DeveloperRead"
  crn_pattern = "${data.confluent_kafka_cluster.cluster.rbac_crn}/kafka=${data.confluent_kafka_cluster.cluster.id}/topic=${var.connector_topic}"
}

#--- DeveloperWrite on DLT topic
resource "confluent_role_binding" "connector-developer-write-dlt" {
  depends_on  = [confluent_service_account.service-account]
  principal   = "User:${confluent_service_account.service-account.id}"
  role_name   = "DeveloperWrite"
  crn_pattern = "${data.confluent_kafka_cluster.cluster.rbac_crn}/kafka=${data.confluent_kafka_cluster.cluster.id}/topic=${var.connector_name}-dlt"
}

#--- Operator to create DLT topics
resource "confluent_role_binding" "connector-cluster-operator" {
  depends_on  = [confluent_service_account.service-account]
  principal   = "User:${confluent_service_account.service-account.id}"
  role_name   = "Operator"
  crn_pattern = data.confluent_kafka_cluster.cluster.rbac_crn
}

#--- DeveloperRead on ConsumerGroup
resource "confluent_role_binding" "connector-consumer-group" {
  depends_on  = [confluent_service_account.service-account]
  principal   = "User:${confluent_service_account.service-account.id}"
  role_name   = "DeveloperRead"
  crn_pattern = "${data.confluent_kafka_cluster.cluster.rbac_crn}/kafka=${data.confluent_kafka_cluster.cluster.id}/group=connect-lcc-*"
}

resource "confluent_role_binding" "connector-resource-owner-dlt" {
  depends_on  = [confluent_service_account.service-account]
  principal   = "User:${confluent_service_account.service-account.id}"
  role_name   = "ResourceOwner"
  crn_pattern = "${data.confluent_kafka_cluster.cluster.rbac_crn}/kafka=${data.confluent_kafka_cluster.cluster.id}/topic=${var.connector_name}-dlt"
}

#  -- Remove when bug is fixed
resource "confluent_role_binding" "connector-developer-write-confluent-bug" {
  depends_on  = [confluent_service_account.service-account]
  principal   = "User:${confluent_service_account.service-account.id}"
  role_name   = "DeveloperWrite"
  crn_pattern = "${data.confluent_kafka_cluster.cluster.rbac_crn}/kafka=${data.confluent_kafka_cluster.cluster.id}/topic=dlq-lcc*"
}

# -- Schema Registry Role Binding
resource "confluent_role_binding" "schema-registry-access" {
  principal   = "User:${confluent_service_account.service-account.id}"
  role_name   = "ResourceOwner"
  crn_pattern = "${data.confluent_schema_registry_cluster.schema-registry.resource_name}/subject=*"
}

# -- api-key needed for ACL, topic creation
resource "confluent_api_key" "kafka" {
  display_name = "${var.connector_name}"
  description  = "Kafka API Key that is owned by service account"
  owner {
    id          = confluent_service_account.service-account.id
    api_version = confluent_service_account.service-account.api_version
    kind        = confluent_service_account.service-account.kind
  }

  managed_resource {
    id          = data.confluent_kafka_cluster.cluster.id
    api_version = data.confluent_kafka_cluster.cluster.api_version
    kind        = data.confluent_kafka_cluster.cluster.kind

    environment {
      id = var.confluent_cloud_env_id
    }
  }

  #lifecycle {
  #  prevent_destroy = true
  #}
}
# -- Create ACLs for DLQ topic ( This wouldnt be necessary once the bug is fixed: https://confluentinc.atlassian.net/browse/CC-39052 )
resource "confluent_kafka_acl" "dlq" {
  depends_on = [
    confluent_role_binding.cloud-cluster-admin-for-acl,
    confluent_role_binding.connector-developer-write,
    confluent_role_binding.connector-developer-read,
    confluent_role_binding.connector-developer-write-dlt,
    confluent_role_binding.connector-cluster-operator,
    confluent_role_binding.connector-consumer-group,
    confluent_role_binding.connector-resource-owner-dlt,
    confluent_role_binding.connector-developer-write-confluent-bug
  ]
  for_each = toset(local.topic_acl_ops)
  kafka_cluster {
    id = data.confluent_kafka_cluster.cluster.id
  }
  resource_type = "TOPIC"
  resource_name = "dlq-lcc"
  pattern_type  = "PREFIXED"
  principal     = "User:${confluent_service_account.service-account.id}"
  host          = "*"
  operation    = each.value
  permission    = "ALLOW"
  rest_endpoint = data.confluent_kafka_cluster.cluster.rest_endpoint
  credentials {
    key    = confluent_api_key.kafka.id
    secret = confluent_api_key.kafka.secret
  }

}

# -- API key for schema registry access
resource "confluent_api_key" "schema-registry" {
  display_name = "${var.environment_short}-${var.connector_name}-schema-registry-key"
  description  = "Schema Registry key for managed connector (owned by Service Account)"

  owner {
    id          = confluent_service_account.service-account.id
    api_version = confluent_service_account.service-account.api_version
    kind        = confluent_service_account.service-account.kind
  }

  managed_resource {
    id          = data.confluent_schema_registry_cluster.schema-registry.id
    api_version = data.confluent_schema_registry_cluster.schema-registry.api_version
    kind        = data.confluent_schema_registry_cluster.schema-registry.kind
    environment {
      id = data.confluent_environment.env.id
    }
  }
}

# -- Create connector topic
resource "confluent_kafka_topic" "connector_topic" {
  kafka_cluster {
    id = data.confluent_kafka_cluster.cluster.id
  }
  topic_name         = var.connector_topic
  rest_endpoint      = data.confluent_kafka_cluster.cluster.rest_endpoint
  credentials {
    key    = confluent_api_key.kafka.id
    secret = confluent_api_key.kafka.secret
  }

  #lifecycle {
  #  prevent_destroy = true
  #}
}

# -- Schema for connector topic
resource "confluent_schema" "connector_topic" {
  depends_on = [confluent_api_key.schema-registry, confluent_role_binding.schema-registry-access ]

  schema_registry_cluster {
    id = data.confluent_schema_registry_cluster.schema-registry.id
  }
  rest_endpoint = data.confluent_schema_registry_cluster.schema-registry.rest_endpoint
  subject_name = var.subject_name
  format = "AVRO"
  schema = file("./schema.avsc")
  credentials {
    key    = confluent_api_key.schema-registry.id
    secret = confluent_api_key.schema-registry.secret
  }

  #lifecycle {
  #  prevent_destroy = true
  #}
}
# -- Deploy Connector
resource "confluent_connector" "sink" {
  depends_on = [ confluent_kafka_acl.dlq, confluent_kafka_topic.connector_topic, confluent_schema.connector_topic ]
  environment {
    #id = data.confluent_environment.env.id
    id = var.confluent_cloud_env_id
  }
  kafka_cluster {
    id = data.confluent_kafka_cluster.cluster.id
  }

  config_sensitive = {
    "kafka.auth.mode"          = "SERVICE_ACCOUNT"
    "kafka.service.account.id" = confluent_service_account.service-account.id
    "connection.password"      = var.db_password
    "value.converter.schema.registry.basic.auth.user.info" = "${confluent_api_key.schema-registry.id}:${confluent_api_key.schema-registry.secret}"
  }

  config_nonsensitive =  {
    "connector.class"                               = "MicrosoftSqlServerSink",
    "name"                                          = var.connector_name,
    "tasks.max"                                     = var.tasks_max,
    "topics"                                        = var.connector_topic,
    "table.name.format"                             = "kafka_$${topic}"
    "connection.host"                               = "18.220.31.188"
    "connection.port"                               = "5434"
    "connection.user"                               = var.db_user
    "db.name"                                       = var.db_name
    "behavior.on.error"                             = "ignore",
    "report.errors.as"                              = "error_string",
    "reporter.result.topic.name"                    = "${var.connector_name}-success"
    "reporter.error.topic.name"                     = "${var.connector_name}-error",
    "value.converter.schemas.enable"                = "false",
    "input.data.format"                             = var.input_data_format,
    "insert.mode"                                   = "UPSERT"        # or "INSERT"
    "auto.create"                                   = "true"
    "auto.evolve"                                   = "true"
    "pk.mode"                                       = "record_value"
    "pk.fields"                                     = "order_id"

    "value.converter"                               = "io.confluent.connect.avro.AvroConverter"
    "value.converter.schema.registry.url"           = data.confluent_schema_registry_cluster.schema-registry.rest_endpoint
    "value.converter.schema.registry.basic.auth.credentials.source" = "USER_INFO"
  }

#  offsets {
#    partition = {
#      "kafka_partition" = "0"
#      "kafka_topic"     = confluent_kafka_topic.connector_topic.topic_name
#    }
#    offset = {
#      "kafka_offset" = "0"
#    }
#  }
#
#  offsets {
#    partition = {
#      "kafka_partition" = "1"
#      "kafka_topic"     = confluent_kafka_topic.connector_topic.topic_name
#    }
#    offset = {
#      "kafka_offset" = "0"
#    }
#  }
}
