terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }

  backend "s3" {
    bucket         = "podtranslate-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "podtranslate-terraform-lock"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "PodTranslate"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    }
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
  azs          = var.availability_zones
}

# EKS Cluster Module
module "eks" {
  source = "./modules/eks"

  project_name            = var.project_name
  environment             = var.environment
  cluster_version         = var.eks_cluster_version
  vpc_id                  = module.vpc.vpc_id
  private_subnet_ids      = module.vpc.private_subnet_ids
  node_group_desired_size = var.node_group_desired_size
  node_group_min_size     = var.node_group_min_size
  node_group_max_size     = var.node_group_max_size
  node_instance_types     = var.node_instance_types
}

# RDS PostgreSQL Module
module "rds" {
  source = "./modules/rds"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.database_subnet_ids
  instance_class     = var.rds_instance_class
  allocated_storage  = var.rds_allocated_storage
  database_name      = var.database_name
  master_username    = var.database_username
  allowed_cidr_blocks = module.vpc.private_subnet_cidrs
}

# ElastiCache Redis Module
module.elasticache" {
  source = "./modules/elasticache"

  project_name        = var.project_name
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.private_subnet_ids
  node_type           = var.redis_node_type
  num_cache_nodes     = var.redis_num_nodes
  allowed_cidr_blocks = module.vpc.private_subnet_cidrs
}

# S3 Buckets Module
module "s3" {
  source = "./modules/s3"

  project_name = var.project_name
  environment  = var.environment
}

# IAM Module
module "iam" {
  source = "./modules/iam"

  project_name      = var.project_name
  environment       = var.environment
  eks_cluster_name  = module.eks.cluster_name
  eks_oidc_provider = module.eks.oidc_provider_arn
  s3_bucket_arn     = module.s3.audio_bucket_arn
}
