# PodTranslate Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [AWS Deployment](#aws-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Monitoring Setup](#monitoring-setup)

## Prerequisites

### Required Software
- Docker 24.0+
- Docker Compose 2.0+
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- PostgreSQL 15+
- RabbitMQ 3.12+
- Redis 7+

### Required API Keys
- OpenAI API key (for GPT-4 and Whisper)
- DeepL API key (optional, for translation)
- AWS credentials (for S3 storage)
- HuggingFace token (for pyannote.audio)
- Platform API credentials (Spotify, Apple, Google)

## Local Development

### 1. Clone Repository
```bash
git clone <repository-url>
cd PODTRANSLATE-
```

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Infrastructure Services
```bash
docker-compose up -d postgres redis rabbitmq clickhouse
```

### 4. Install Dependencies

**Audio Processing Service (Python):**
```bash
cd services/audio-processing
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**API Gateway (Node.js):**
```bash
cd services/api-gateway
npm install
```

**Distribution Service (Node.js):**
```bash
cd services/distribution
npm install
```

### 5. Database Migration
```bash
cd shared/database
python -c "from database import get_database; db = get_database(); db.create_all()"
```

### 6. Start Services

**Terminal 1 - Audio Processing:**
```bash
cd services/audio-processing
python src/main.py
```

**Terminal 2 - API Gateway:**
```bash
cd services/api-gateway
npm run dev
```

**Terminal 3 - Distribution Service:**
```bash
cd services/distribution
npm run dev
```

### 7. Verify Installation
```bash
curl http://localhost:3000/api/v1/health
curl http://localhost:3001/health
```

## Docker Deployment

### 1. Build Images
```bash
docker-compose build
```

### 2. Start All Services
```bash
docker-compose up -d
```

### 3. View Logs
```bash
docker-compose logs -f
```

### 4. Stop Services
```bash
docker-compose down
```

### 5. Access Services
- API Gateway: http://localhost:3000
- Audio Processing: http://localhost:3001
- Distribution: http://localhost:3002
- Analytics: http://localhost:3003
- AI Tools: http://localhost:3004
- Grafana: http://localhost:3005
- RabbitMQ Management: http://localhost:15672

## Kubernetes Deployment

### 1. Prerequisites
- Kubernetes cluster (EKS, GKE, or AKS)
- kubectl configured
- Helm 3+

### 2. Create Namespace
```bash
kubectl create namespace podtranslate
```

### 3. Create Secrets
```bash
kubectl create secret generic podtranslate-secrets \
  --from-env-file=.env \
  -n podtranslate
```

### 4. Deploy Infrastructure
```bash
# PostgreSQL
helm install postgres bitnami/postgresql \
  --namespace podtranslate \
  --set auth.username=podtranslate \
  --set auth.password=<password> \
  --set auth.database=podtranslate

# RabbitMQ
helm install rabbitmq bitnami/rabbitmq \
  --namespace podtranslate

# Redis
helm install redis bitnami/redis \
  --namespace podtranslate
```

### 5. Deploy Services
```bash
kubectl apply -f infrastructure/kubernetes/ -n podtranslate
```

### 6. Verify Deployment
```bash
kubectl get pods -n podtranslate
kubectl get services -n podtranslate
```

### 7. Access Services
```bash
kubectl port-forward svc/api-gateway 3000:3000 -n podtranslate
```

## AWS Deployment

### Architecture
```
Internet → ALB → ECS/Fargate → Services
                     ↓
                 RDS (PostgreSQL)
                     ↓
                 ElastiCache (Redis)
                     ↓
                 Amazon MQ (RabbitMQ)
                     ↓
                 S3 (Storage)
```

### 1. Infrastructure as Code (Terraform)

**Create `infrastructure/terraform/main.tf`:**

```hcl
provider "aws" {
  region = "us-east-1"
}

# VPC
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "podtranslate-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier           = "podtranslate-db"
  engine              = "postgres"
  engine_version      = "15.3"
  instance_class      = "db.t3.medium"
  allocated_storage   = 100

  db_name  = "podtranslate"
  username = "podtranslate"
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  skip_final_snapshot    = false
  final_snapshot_identifier = "podtranslate-final-snapshot"
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "podtranslate-redis"
  engine               = "redis"
  node_type            = "cache.t3.medium"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379

  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]
}

# S3 Buckets
resource "aws_s3_bucket" "audio" {
  bucket = "podtranslate-audio-${var.environment}"
}

resource "aws_s3_bucket" "transcripts" {
  bucket = "podtranslate-transcripts-${var.environment}"
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "podtranslate-cluster"
}

# ALB
resource "aws_lb" "main" {
  name               = "podtranslate-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets
}
```

### 2. Deploy with Terraform
```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### 3. Deploy Services to ECS

**Build and push Docker images:**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -t podtranslate/api-gateway services/api-gateway
docker tag podtranslate/api-gateway:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/podtranslate/api-gateway:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/podtranslate/api-gateway:latest
```

**Create ECS task definition and service:**
```bash
aws ecs create-service \
  --cluster podtranslate-cluster \
  --service-name api-gateway \
  --task-definition podtranslate-api-gateway \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

## Environment Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
CLICKHOUSE_URL=http://clickhouse:8123

# Message Queue
RABBITMQ_URL=amqp://user:pass@host:5672
REDIS_URL=redis://host:6379

# Storage
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
S3_BUCKET_AUDIO=podtranslate-audio
S3_BUCKET_TRANSCRIPTS=podtranslate-transcripts

# AI Services
OPENAI_API_KEY=sk-xxx
DEEPL_API_KEY=xxx
PYANNOTE_AUTH_TOKEN=xxx

# Platform APIs
SPOTIFY_CLIENT_ID=xxx
SPOTIFY_CLIENT_SECRET=xxx
APPLE_KEY_ID=xxx
GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json

# Application
NODE_ENV=production
JWT_SECRET=xxx
```

### Configuration Management

**AWS Systems Manager Parameter Store:**
```bash
aws ssm put-parameter \
  --name /podtranslate/production/openai-api-key \
  --value "sk-xxx" \
  --type SecureString
```

**Kubernetes Secrets:**
```bash
kubectl create secret generic api-keys \
  --from-literal=openai-api-key=sk-xxx \
  --from-literal=deepl-api-key=xxx \
  -n podtranslate
```

## Monitoring Setup

### 1. Prometheus
```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --create-namespace
```

### 2. Grafana
```bash
# Install Grafana
helm install grafana grafana/grafana \
  --namespace monitoring \
  --set adminPassword=admin
```

### 3. Import Dashboards
- PodTranslate System Overview
- Audio Processing Metrics
- API Gateway Performance
- Database Monitoring

### 4. Alerting Rules

**Create `alerting-rules.yml`:**
```yaml
groups:
  - name: podtranslate
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: TranscriptionJobFailed
        expr: transcription_jobs_failed_total > 10
        for: 10m
        annotations:
          summary: "Multiple transcription jobs failing"
```

## Backup and Recovery

### Database Backups
```bash
# Automated daily backups
0 2 * * * pg_dump -h localhost -U podtranslate podtranslate | gzip > /backups/podtranslate_$(date +\%Y\%m\%d).sql.gz
```

### S3 Versioning
```bash
aws s3api put-bucket-versioning \
  --bucket podtranslate-audio \
  --versioning-configuration Status=Enabled
```

## Scaling

### Horizontal Pod Autoscaler (Kubernetes)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Auto Scaling (AWS)
```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/podtranslate-cluster/api-gateway \
  --min-capacity 2 \
  --max-capacity 10
```

## Troubleshooting

### Common Issues

**1. Transcription Service Not Starting**
- Check CUDA availability for GPU
- Verify Whisper model download
- Check disk space for model cache

**2. Database Connection Failed**
- Verify DATABASE_URL format
- Check network connectivity
- Verify credentials

**3. High Memory Usage**
- Adjust Whisper model size
- Increase container memory limits
- Enable memory swapping

### Logs
```bash
# Docker Compose
docker-compose logs -f api-gateway

# Kubernetes
kubectl logs -f deployment/api-gateway -n podtranslate

# ECS
aws logs tail /ecs/api-gateway --follow
```

## Security Checklist

- [ ] Enable SSL/TLS for all services
- [ ] Rotate API keys regularly
- [ ] Use IAM roles instead of access keys
- [ ] Enable database encryption
- [ ] Set up VPC security groups
- [ ] Enable CloudTrail logging
- [ ] Configure WAF rules
- [ ] Set up DDoS protection
- [ ] Regular security audits
- [ ] Vulnerability scanning

## Performance Tuning

### Database Optimization
```sql
-- Add indexes for common queries
CREATE INDEX idx_episodes_podcast ON episodes(podcast_id);
CREATE INDEX idx_jobs_status ON transcription_jobs(status);
```

### Redis Caching
```javascript
// Cache frequently accessed data
const cacheKey = `podcast:${podcastId}`;
const cached = await redis.get(cacheKey);
if (cached) return JSON.parse(cached);

const podcast = await db.getPodcast(podcastId);
await redis.set(cacheKey, JSON.stringify(podcast), 'EX', 3600);
```

### Connection Pooling
```python
# PostgreSQL connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

## Support

For deployment issues:
- Check documentation: https://docs.podtranslate.com
- GitHub Issues: https://github.com/podtranslate/podtranslate/issues
- Email: devops@podtranslate.com
