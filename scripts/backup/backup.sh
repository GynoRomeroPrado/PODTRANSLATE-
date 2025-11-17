#!/bin/bash
set -e

#
# PodTranslate Backup Script
# Backs up PostgreSQL database, S3 data, and configurations
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/podtranslate}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=${RETENTION_DAYS:-30}

# Load environment variables
if [ -f "$SCRIPT_DIR/.env" ]; then
  source "$SCRIPT_DIR/.env"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
  echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

# Create backup directory
create_backup_dir() {
  local backup_path="$BACKUP_DIR/$TIMESTAMP"
  mkdir -p "$backup_path"
  echo "$backup_path"
}

# Backup PostgreSQL database
backup_postgres() {
  local backup_path=$1
  log "Backing up PostgreSQL database..."

  # Export from Kubernetes pod
  if [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
    kubectl exec -n podtranslate deployment/postgresql -- \
      pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc | \
      gzip > "$backup_path/postgres_${TIMESTAMP}.dump.gz"
  else
    # Local docker or direct connection
    pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -Fc | \
      gzip > "$backup_path/postgres_${TIMESTAMP}.dump.gz"
  fi

  log "✓ PostgreSQL backup completed: $(du -h "$backup_path/postgres_${TIMESTAMP}.dump.gz" | cut -f1)"
}

# Backup ClickHouse analytics database
backup_clickhouse() {
  local backup_path=$1
  log "Backing up ClickHouse database..."

  if [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
    kubectl exec -n podtranslate deployment/clickhouse -- \
      clickhouse-client --query="BACKUP DATABASE analytics TO Disk('backups', '${TIMESTAMP}/analytics')" || true
  else
    clickhouse-client --host "$CLICKHOUSE_HOST" \
      --query="BACKUP DATABASE analytics TO Disk('backups', '${TIMESTAMP}/analytics')" || true
  fi

  log "✓ ClickHouse backup completed"
}

# Backup S3 data
backup_s3() {
  local backup_path=$1
  log "Backing up S3 data..."

  # Create manifest of S3 objects
  aws s3 ls "s3://$S3_AUDIO_BUCKET" --recursive > "$backup_path/s3_audio_manifest.txt"
  aws s3 ls "s3://$S3_TRANSCRIPTS_BUCKET" --recursive > "$backup_path/s3_transcripts_manifest.txt"

  # Optional: Sync S3 data to local backup
  if [ "$BACKUP_S3_DATA" = "true" ]; then
    mkdir -p "$backup_path/s3_data"
    aws s3 sync "s3://$S3_AUDIO_BUCKET" "$backup_path/s3_data/audio" --quiet
    aws s3 sync "s3://$S3_TRANSCRIPTS_BUCKET" "$backup_path/s3_data/transcripts" --quiet
    log "✓ S3 data synced to local backup"
  fi

  log "✓ S3 manifests created"
}

# Backup Kubernetes resources
backup_kubernetes() {
  local backup_path=$1
  log "Backing up Kubernetes resources..."

  mkdir -p "$backup_path/k8s"

  # Export all resources
  for resource in deployment statefulset service configmap secret pvc; do
    kubectl get "$resource" -n podtranslate -o yaml > "$backup_path/k8s/${resource}s.yaml" 2>/dev/null || true
  done

  # Export Helm values
  if command -v helm &> /dev/null; then
    helm get values podtranslate -n podtranslate -o yaml > "$backup_path/k8s/helm-values.yaml" 2>/dev/null || true
  fi

  log "✓ Kubernetes resources backed up"
}

# Backup configurations
backup_configs() {
  local backup_path=$1
  log "Backing up configurations..."

  mkdir -p "$backup_path/configs"

  # Copy environment files (excluding secrets)
  cp -r "$SCRIPT_DIR/../../.env.example" "$backup_path/configs/" 2>/dev/null || true
  cp -r "$SCRIPT_DIR/../../docker-compose.yml" "$backup_path/configs/" 2>/dev/null || true

  log "✓ Configurations backed up"
}

# Create backup metadata
create_metadata() {
  local backup_path=$1
  log "Creating backup metadata..."

  cat > "$backup_path/metadata.json" <<EOF
{
  "timestamp": "$TIMESTAMP",
  "date": "$(date -Iseconds)",
  "hostname": "$(hostname)",
  "deployment_type": "$DEPLOYMENT_TYPE",
  "postgres_version": "$(psql --version | head -1)",
  "components": [
    "postgres",
    "clickhouse",
    "s3",
    "configs"
  ]
}
EOF

  log "✓ Metadata created"
}

# Compress backup
compress_backup() {
  local backup_path=$1
  log "Compressing backup..."

  tar -czf "${backup_path}.tar.gz" -C "$(dirname "$backup_path")" "$(basename "$backup_path")"
  rm -rf "$backup_path"

  local size=$(du -h "${backup_path}.tar.gz" | cut -f1)
  log "✓ Backup compressed: $size"
}

# Upload to S3
upload_to_s3() {
  local backup_file=$1
  log "Uploading backup to S3..."

  aws s3 cp "$backup_file" "s3://$S3_BACKUP_BUCKET/backups/$(basename "$backup_file")"

  log "✓ Backup uploaded to S3"
}

# Clean old backups
cleanup_old_backups() {
  log "Cleaning up old backups (retention: ${RETENTION_DAYS} days)..."

  # Local cleanup
  find "$BACKUP_DIR" -name "*.tar.gz" -mtime +${RETENTION_DAYS} -delete

  # S3 cleanup
  if [ -n "$S3_BACKUP_BUCKET" ]; then
    aws s3 ls "s3://$S3_BACKUP_BUCKET/backups/" | \
      awk '{print $4}' | \
      while read -r file; do
        file_date=$(echo "$file" | grep -oP '\d{8}' | head -1)
        if [ -n "$file_date" ]; then
          days_old=$(( ($(date +%s) - $(date -d "$file_date" +%s)) / 86400 ))
          if [ $days_old -gt $RETENTION_DAYS ]; then
            aws s3 rm "s3://$S3_BACKUP_BUCKET/backups/$file"
            log "Deleted old backup: $file"
          fi
        fi
      done
  fi

  log "✓ Old backups cleaned up"
}

# Main backup function
main() {
  log "Starting PodTranslate backup..."
  log "Backup directory: $BACKUP_DIR"

  # Create backup directory
  local backup_path=$(create_backup_dir)
  log "Created backup directory: $backup_path"

  # Perform backups
  backup_postgres "$backup_path"
  backup_clickhouse "$backup_path" || warn "ClickHouse backup failed (non-fatal)"
  backup_s3 "$backup_path"

  if [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
    backup_kubernetes "$backup_path"
  fi

  backup_configs "$backup_path"
  create_metadata "$backup_path"

  # Compress and upload
  compress_backup "$backup_path"

  if [ -n "$S3_BACKUP_BUCKET" ]; then
    upload_to_s3 "${backup_path}.tar.gz"
  fi

  # Cleanup
  cleanup_old_backups

  log "✅ Backup completed successfully!"
  log "Backup file: ${backup_path}.tar.gz"
}

# Run main function
main "$@"
