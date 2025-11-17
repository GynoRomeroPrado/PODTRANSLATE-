output "pod_s3_role_arn" {
  description = "IAM role ARN for pod S3 access"
  value       = aws_iam_role.pod_s3_access.arn
}
