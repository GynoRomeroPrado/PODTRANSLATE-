# PodTranslate Backup & Restore

Automated backup and restore scripts for PodTranslate infrastructure.

## Features

- **PostgreSQL**: Full database dumps with compression
- **ClickHouse**: Analytics database backups
- **S3**: Manifest files (optional: full data sync)
- **Kubernetes**: Resource definitions and Helm values
- **Configurations**: Environment and Docker Compose files
- **S3 Upload**: Automatic upload to backup bucket
- **Retention**: Automatic cleanup of old backups
- **Metadata**: JSON metadata for each backup

## Prerequisites

- `postgresql-client` (psql, pg_dump, pg_restore)
- `aws-cli` configured with credentials
- `kubectl` configured (for Kubernetes deployments)
- `tar`, `gzip`

## Configuration

Copy and configure environment file:

```bash
cp .env.example .env
# Edit .env with your configuration
```

### Key Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `DEPLOYMENT_TYPE` | `kubernetes` or `docker` | `kubernetes` |
| `BACKUP_DIR` | Local backup directory | `/var/backups/podtranslate` |
| `RETENTION_DAYS` | Days to keep backups | `30` |
| `BACKUP_S3_DATA` | Backup S3 files locally | `false` |
| `S3_BACKUP_BUCKET` | S3 bucket for backups | Required |

## Usage

### Manual Backup

```bash
./backup.sh
```

Output:
```
[2024-01-15 02:00:00] Starting PodTranslate backup...
[2024-01-15 02:00:01] Backing up PostgreSQL database...
[2024-01-15 02:00:45] ✓ PostgreSQL backup completed: 250M
[2024-01-15 02:01:00] Backing up S3 data...
[2024-01-15 02:01:10] ✓ S3 manifests created
[2024-01-15 02:01:15] Compressing backup...
[2024-01-15 02:02:00] ✓ Backup compressed: 180M
[2024-01-15 02:02:30] ✓ Backup uploaded to S3
[2024-01-15 02:02:31] ✅ Backup completed successfully!
```

### Scheduled Backups

Set up daily backups at 2 AM:

```bash
./schedule-backup.sh
```

Custom schedule:

```bash
# Every 6 hours
CRON_SCHEDULE="0 */6 * * *" ./schedule-backup.sh

# Weekly on Sunday at midnight
CRON_SCHEDULE="0 0 * * 0" ./schedule-backup.sh
```

View logs:

```bash
tail -f /var/log/podtranslate-backup.log
```

### List Backups

```bash
./restore.sh
```

Output:
```
Available backups:

  20240115_020000.tar.gz
  20240114_020000.tar.gz
  20240113_020000.tar.gz
```

### Restore from Backup

```bash
./restore.sh 20240115_020000.tar.gz
```

Interactive prompts:
- Database restore confirmation
- S3 data restore confirmation
- Kubernetes resources confirmation

## Backup Contents

Each backup includes:

```
20240115_020000/
├── postgres_20240115_020000.dump.gz   # PostgreSQL dump
├── s3_audio_manifest.txt               # S3 audio files list
├── s3_transcripts_manifest.txt         # S3 transcripts list
├── s3_data/                            # (Optional) S3 files
│   ├── audio/
│   └── transcripts/
├── k8s/                                # Kubernetes resources
│   ├── deployments.yaml
│   ├── services.yaml
│   ├── configmaps.yaml
│   └── helm-values.yaml
├── configs/                            # Configuration files
│   ├── .env.example
│   └── docker-compose.yml
└── metadata.json                       # Backup metadata
```

## Automation

### Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: podtranslate-backup
  namespace: podtranslate
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: podtranslate/backup:latest
            env:
            - name: DEPLOYMENT_TYPE
              value: "kubernetes"
            - name: S3_BACKUP_BUCKET
              value: "podtranslate-prod-backups"
            envFrom:
            - secretRef:
                name: backup-secrets
            volumeMounts:
            - name: backup-storage
              mountPath: /var/backups/podtranslate
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

Deploy:

```bash
kubectl apply -f k8s-cronjob.yaml
```

### GitHub Actions

```yaml
name: Backup

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:     # Manual trigger

jobs:
  backup:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Configure kubectl
        run: |
          aws eks update-kubeconfig --name podtranslate-prod-cluster

      - name: Run backup
        run: |
          cd scripts/backup
          ./backup.sh
        env:
          DEPLOYMENT_TYPE: kubernetes
          S3_BACKUP_BUCKET: podtranslate-prod-backups
```

## Disaster Recovery

### Complete Restore Procedure

1. **Prepare environment**:
   ```bash
   # Deploy infrastructure
   terraform apply
   helm install podtranslate ./helm/podtranslate
   ```

2. **Stop services**:
   ```bash
   kubectl scale deployment --all --replicas=0 -n podtranslate
   ```

3. **Restore database**:
   ```bash
   ./restore.sh 20240115_020000.tar.gz
   ```

4. **Restore S3 data** (if needed):
   - Manifests are in backup
   - Full data restore requires `BACKUP_S3_DATA=true` in original backup

5. **Start services**:
   ```bash
   kubectl scale deployment --all --replicas=1 -n podtranslate
   ```

6. **Verify**:
   ```bash
   kubectl get pods -n podtranslate
   curl https://podtranslate.example.com/api/v1/health
   ```

## Monitoring

### Backup Status

Check last backup:

```bash
aws s3 ls s3://podtranslate-prod-backups/backups/ | tail -1
```

Verify backup size:

```bash
aws s3 ls s3://podtranslate-prod-backups/backups/20240115_020000.tar.gz --human-readable
```

### Alerts

Set up CloudWatch alarms:

```bash
# Alert if no backup in 25 hours
aws cloudwatch put-metric-alarm \
  --alarm-name podtranslate-backup-missing \
  --alarm-description "No backup in 25 hours" \
  --metric-name BackupAge \
  --namespace PodTranslate \
  --statistic Maximum \
  --period 3600 \
  --threshold 25 \
  --comparison-operator GreaterThanThreshold
```

## Best Practices

1. **Test Restores**: Regularly test restore procedure
2. **Monitor Backups**: Set up alerts for failed backups
3. **Encrypt**: Use encrypted S3 buckets
4. **Retention**: Balance cost vs. compliance requirements
5. **Off-site**: Store backups in different AWS region
6. **Automation**: Use CronJobs or GitHub Actions
7. **Documentation**: Keep runbook updated

## Troubleshooting

### Backup fails with "permission denied"

```bash
# Check AWS credentials
aws sts get-caller-identity

# Check S3 bucket access
aws s3 ls s3://podtranslate-prod-backups/
```

### Restore fails with database connection error

```bash
# Verify database is running
kubectl get pods -n podtranslate | grep postgresql

# Check connectivity
kubectl exec -it deployment/postgresql -n podtranslate -- psql -U podtranslate -c "SELECT 1"
```

### Backup is too large

- Set `BACKUP_S3_DATA=false` to only backup manifests
- Use S3 lifecycle policies for actual data
- Implement incremental backups

## Security

- Never commit `.env` file
- Use IAM roles instead of access keys
- Encrypt backups at rest
- Use private S3 buckets
- Rotate database credentials regularly

## License

MIT
