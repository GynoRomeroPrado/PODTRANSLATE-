variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs"
  type        = list(string)
}

variable "node_type" {
  description = "Cache node type"
  type        = string
}

variable "num_cache_nodes" {
  description = "Number of cache nodes"
  type        = number
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access Redis"
  type        = list(string)
}
