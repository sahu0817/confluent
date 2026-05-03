variable "confluent_cloud_api_key" {
  description = "Confluent Cloud API Key (also referred as Cloud API ID)"
  type        = string
}

variable "confluent_cloud_api_secret" {
  description = "Confluent Cloud API Secret"
  type        = string
  sensitive   = true
}

variable "confluent_cloud_env_id" {
  description = "Confluent Cloud Environment ID"
  type        = string
  default     = "env-y65pxp"
}

variable "confluent_cloud_kafka_cluster_id" {
  description = "Confluent Cloud Kafka Cluster ID"
  type        = string
  default     = "lkc-86p6xm"
}

variable "tasks_max" {
  description = "Maximum number of tasks for the connector"
  type        = string
  default     = "1"
}

variable "connector_name" {
  description = "Name of the connector"
  type        = string
  default     = "srinivas_mssql_sink_test"
}

variable "db_name" {
  description = "Name of the database"
  type        = string
  default     = "testdb"
}

variable "db_user" {
  description = "dtabase user"
  type        = string
  default     = "******"
}


variable "db_password" {
  description = "database password"
  type        = string
  default     = "*******"
  sensitive   = true
}


variable "connector_topic" {
  description = "Topic to be consumed by the connector"
  type        = string
  default     = "srinivas_mssql_sink_test"
}

variable "subject_name" {
  description = "Schema for the connector topic"
  type        = string
  default     = "srinivas_mssql_sink_test-value"
}

variable "environment_short" {
  description = "Comfluent Cloud Environment Name Abbreviation"
  type        = string
  default     = "srinivas"
}

variable "input_data_format" {
  description = "Input data format"
  type        = string
  default     = "AVRO"
}
