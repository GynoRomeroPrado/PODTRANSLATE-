locals {
  name = "${var.project_name}-${var.environment}"
}

# Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  name       = "${local.name}-redis-subnet"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "${local.name}-redis-subnet"
  }
}

# Security Group
resource "aws_security_group" "redis" {
  name        = "${local.name}-redis-sg"
  description = "Security group for Redis"
  vpc_id      = var.vpc_id

  ingress {
    description = "Redis from VPC"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name}-redis-sg"
  }
}

# Random auth token
resource "random_password" "auth_token" {
  length  = 32
  special = false
}

# Replication Group
resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${local.name}-redis"
  replication_group_description = "Redis cluster for ${local.name}"

  engine               = "redis"
  engine_version       = "7.0"
  node_type            = var.node_type
  num_cache_clusters   = var.num_cache_nodes
  port                 = 6379

  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]

  automatic_failover_enabled = var.num_cache_nodes > 1
  multi_az_enabled          = var.num_cache_nodes > 1

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                = random_password.auth_token.result

  snapshot_retention_limit = 5
  snapshot_window         = "03:00-05:00"
  maintenance_window      = "mon:05:00-mon:07:00"

  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_slow_log.name
    destination_type = "cloudwatch-logs"
    log_format       = "json"
    log_type         = "slow-log"
  }

  tags = {
    Name = "${local.name}-redis"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "redis_slow_log" {
  name              = "/aws/elasticache/${local.name}-redis/slow-log"
  retention_in_days = 7

  tags = {
    Name = "${local.name}-redis-logs"
  }
}

# Store auth token in Secrets Manager
resource "aws_secretsmanager_secret" "redis_auth" {
  name = "${local.name}-redis-auth"
}

resource "aws_secretsmanager_secret_version" "redis_auth" {
  secret_id     = aws_secretsmanager_secret.redis_auth.id
  secret_string = jsonencode({
    auth_token = random_password.auth_token.result
    endpoint   = aws_elasticache_replication_group.main.primary_endpoint_address
    port       = 6379
  })
}
