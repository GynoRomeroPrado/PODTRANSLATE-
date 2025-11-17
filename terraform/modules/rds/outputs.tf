output "endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.main.endpoint
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "secret_arn" {
  description = "Secrets Manager secret ARN"
  value       = aws_secretsmanager_secret.db_password.arn
}
