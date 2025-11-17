# PodTranslate AWS Infrastructure

Terraform modules for deploying PodTranslate infrastructure on AWS.

## Architecture

The infrastructure includes:

- **VPC**: Multi-AZ VPC with public, private, and database subnets
- **EKS**: Kubernetes cluster with general and GPU node groups
- **RDS**: PostgreSQL database with multi-AZ support
- **ElastiCache**: Redis cluster for caching
- **S3**: Buckets for audio files and transcripts
- **IAM**: Service account roles for pod-level permissions

## Prerequisites

- AWS CLI configured
- Terraform >= 1.0
- kubectl
- AWS account with appropriate permissions

## Quick Start

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Create terraform.tfvars

```hcl
aws_region     = "us-east-1"
project_name   = "podtranslate"
environment    = "prod"

# VPC
vpc_cidr           = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

# EKS
eks_cluster_version = "1.28"
node_group_desired_size = 3
node_group_min_size     = 2
node_group_max_size     = 10
node_instance_types     = ["t3.large"]

# RDS
rds_instance_class    = "db.t3.medium"
rds_allocated_storage = 100
database_name         = "podtranslate"
database_username     = "podtranslate"

# Redis
redis_node_type  = "cache.t3.medium"
redis_num_nodes  = 2
```

### 3. Plan and Apply

```bash
# Review changes
terraform plan

# Apply changes
terraform apply
```

### 4. Configure kubectl

```bash
aws eks update-kubeconfig --region us-east-1 --name podtranslate-prod-cluster
```

## Module Documentation

### VPC Module

Creates a multi-AZ VPC with:
- Public subnets for load balancers
- Private subnets for application workloads
- Database subnets for RDS/ElastiCache
- NAT gateways for outbound internet access
- Route tables and associations

**Inputs:**
- `project_name` - Project name
- `environment` - Environment (dev/staging/prod)
- `vpc_cidr` - VPC CIDR block
- `azs` - Availability zones

**Outputs:**
- `vpc_id` - VPC ID
- `public_subnet_ids` - Public subnet IDs
- `private_subnet_ids` - Private subnet IDs
- `database_subnet_ids` - Database subnet IDs

### EKS Module

Creates an EKS cluster with:
- Control plane with CloudWatch logging
- General purpose node group (CPU workloads)
- GPU node group (for Whisper transcription)
- OIDC provider for IRSA
- Essential addons (VPC CNI, CoreDNS, kube-proxy)

**Inputs:**
- `project_name` - Project name
- `environment` - Environment
- `cluster_version` - Kubernetes version
- `vpc_id` - VPC ID
- `private_subnet_ids` - Subnet IDs for nodes
- `node_group_*` - Node group configuration

**Outputs:**
- `cluster_name` - Cluster name
- `cluster_endpoint` - API endpoint
- `oidc_provider_arn` - OIDC provider ARN

### RDS Module

Creates PostgreSQL database with:
- Multi-AZ deployment for high availability
- Automated backups (7-day retention)
- Encryption at rest
- CloudWatch logs export
- Secrets Manager integration

**Inputs:**
- `project_name` - Project name
- `environment` - Environment
- `vpc_id` - VPC ID
- `subnet_ids` - Database subnet IDs
- `instance_class` - Instance type
- `allocated_storage` - Storage size (GB)
- `database_name` - Database name
- `master_username` - Admin username

**Outputs:**
- `endpoint` - Database endpoint
- `database_name` - Database name
- `secret_arn` - Secrets Manager ARN

### ElastiCache Module

Creates Redis cluster with:
- Multi-node replication for HA
- Encryption in transit and at rest
- Auth token authentication
- Automatic failover
- CloudWatch logs

**Inputs:**
- `project_name` - Project name
- `environment` - Environment
- `vpc_id` - VPC ID
- `subnet_ids` - Subnet IDs
- `node_type` - Cache node type
- `num_cache_nodes` - Number of nodes

**Outputs:**
- `endpoint` - Redis endpoint
- `secret_arn` - Secrets Manager ARN

### S3 Module

Creates S3 buckets with:
- Versioning enabled
- Server-side encryption
- Lifecycle policies (Glacier after 90 days)
- CORS configuration
- Public access blocked

**Inputs:**
- `project_name` - Project name
- `environment` - Environment

**Outputs:**
- `audio_bucket_name` - Audio bucket name
- `transcripts_bucket_name` - Transcripts bucket name

### IAM Module

Creates IAM roles for:
- Pod-level S3 access (IRSA)
- CloudWatch Logs access

**Inputs:**
- `project_name` - Project name
- `environment` - Environment
- `eks_oidc_provider` - OIDC provider ARN
- `s3_bucket_arn` - S3 bucket ARN

**Outputs:**
- `pod_s3_role_arn` - Service account role ARN

## Environment-Specific Configurations

### Development

```hcl
# terraform.dev.tfvars
environment = "dev"
node_group_desired_size = 2
node_group_min_size     = 1
node_group_max_size     = 3
rds_instance_class      = "db.t3.small"
redis_node_type         = "cache.t3.small"
redis_num_nodes         = 1
```

Apply with:
```bash
terraform apply -var-file=terraform.dev.tfvars
```

### Production

```hcl
# terraform.prod.tfvars
environment = "prod"
node_group_desired_size = 5
node_group_min_size     = 3
node_group_max_size     = 20
rds_instance_class      = "db.r5.xlarge"
redis_node_type         = "cache.r5.large"
redis_num_nodes         = 3
```

## Cost Estimation

Approximate monthly costs (us-east-1):

**Development:**
- EKS cluster: $72
- EC2 nodes (2x t3.large): ~$120
- RDS (db.t3.small): ~$30
- ElastiCache (1x cache.t3.small): ~$20
- **Total: ~$242/month**

**Production:**
- EKS cluster: $72
- EC2 nodes (5x t3.large + 1x g4dn.xlarge): ~$850
- RDS (db.r5.xlarge): ~$350
- ElastiCache (3x cache.r5.large): ~$450
- S3 storage: Variable
- **Total: ~$1,722/month + storage**

## Secrets Management

Database and Redis credentials are stored in AWS Secrets Manager. Access them:

```bash
# RDS credentials
aws secretsmanager get-secret-value \
  --secret-id podtranslate-prod-db-password \
  --query SecretString --output text | jq .

# Redis credentials
aws secretsmanager get-secret-value \
  --secret-id podtranslate-prod-redis-auth \
  --query SecretString --output text | jq .
```

## Monitoring

The infrastructure includes:
- CloudWatch log groups for RDS and ElastiCache
- EKS control plane logging
- VPC Flow Logs (optional)

## Backup and Disaster Recovery

- **RDS**: Automated backups (7-day retention), manual snapshots before major changes
- **S3**: Versioning enabled, cross-region replication (optional)
- **EKS**: etcd snapshots via EKS managed backups

## Security Best Practices

- All data encrypted at rest and in transit
- Private subnets for workloads
- Security groups with least privilege
- IRSA for pod-level permissions
- Secrets Manager for credentials
- Public access blocked on S3

## Troubleshooting

### Cannot connect to RDS

```bash
# Check security group rules
aws ec2 describe-security-groups --group-ids <rds-sg-id>

# Test from EKS pod
kubectl run -it --rm debug --image=postgres:15 -- \
  psql -h <rds-endpoint> -U podtranslate -d podtranslate
```

### EKS nodes not joining

```bash
# Check IAM role policies
aws iam list-attached-role-policies --role-name <node-role-name>

# View node logs
aws eks describe-cluster --name podtranslate-prod-cluster
```

## Cleanup

```bash
# Destroy infrastructure (WARNING: irreversible)
terraform destroy

# Remove state files
rm -rf .terraform terraform.tfstate*
```

## Support

- AWS Documentation: https://docs.aws.amazon.com/
- Terraform Registry: https://registry.terraform.io/
- Issues: https://github.com/podtranslate/podtranslate/issues

## License

MIT
