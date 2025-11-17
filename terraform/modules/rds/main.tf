locals {
  name = "${var.project_name}-${var.environment}"
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${local.name}-db-subnet"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "${local.name}-db-subnet"
  }
}

# Security Group
resource "aws_security_group" "rds" {
  name        = "${local.name}-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = var.vpc_id

  ingress {
    description = "PostgreSQL from VPC"
    from_port   = 5432
    to_port     = 5432
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
    Name = "${local.name}-rds-sg"
  }
}

# Random password
resource "random_password" "master" {
  length  = 32
  special = true
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier     = "${local.name}-db"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.instance_class

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.allocated_storage * 2
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.database_name
  username = var.master_username
  password = random_password.master.result

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  multi_az               = var.multi_az
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  deletion_protection             = true
  skip_final_snapshot            = false
  final_snapshot_identifier      = "${local.name}-db-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  tags = {
    Name = "${local.name}-db"
  }
}

# Store password in Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name = "${local.name}-db-password"
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = var.master_username
    password = random_password.master.result
    endpoint = aws_db_instance.main.endpoint
    database = var.database_name
  })
}
