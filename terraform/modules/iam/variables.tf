variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "eks_cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "eks_oidc_provider" {
  description = "EKS OIDC provider ARN"
  type        = string
}

variable "s3_bucket_arn" {
  description = "S3 bucket ARN"
  type        = string
}
