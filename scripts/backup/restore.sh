#!/bin/bash
set -e

#
# PodTranslate Restore Script
# Restores PostgreSQL database, S3 data, and configurations from backup
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/podtranslate}"

# Load environment variables
if [ -f "$SCRIPT_DIR/.env" ]; then
  source "$SCRIPT_DIR/.env"
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
  echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1" >&2
  exit 1
}

warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

# List available backups
list_backups() {
  log "Available backups:"
  echo ""

  if [ -n "$S3_BACKUP_BUCKET" ]; then
    aws s3 ls "s3://$S3_BACKUP_BUCKET/backups/" | grep "\.tar\.gz$" | awk '{print "  " $4}'
  else
    ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | xargs -n1 basename || echo "  No backups found"
  fi

  echo ""
}

# Download backup from S3
download_from_s3() {
  local backup_name=$1
  local local_path="$BACKUP_DIR/$backup_name"

  log "Downloading backup from S3..."
  aws s3 cp "s3://$S3_BACKUP_BUCKET/backups/$backup_name" "$local_path"

  echo "$local_path"
}

# Extract backup
extract_backup() {
  local backup_file=$1
  local extract_dir="${backup_file%.tar.gz}"

  log "Extracting backup..."
  tar -xzf "$backup_file" -C "$BACKUP_DIR"

  echo "$extract_dir"
}

# Restore PostgreSQL database
restore_postgres() {
  local backup_path=$1
  local postgres_dump=$(find "$backup_path" -name "postgres_*.dump.gz" | head -1)

  if [ -z "$postgres_dump" ]; then
    error "PostgreSQL dump not found in backup"
  fi

  log "Restoring PostgreSQL database..."

  # Confirmation prompt
  read -p "⚠️  This will replace the current database. Continue? (yes/no): " confirm
  if [ "$confirm" != "yes" ]; then
    error "Restore cancelled by user"
  fi

  # Drop and recreate database
  if [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
    kubectl exec -n podtranslate deployment/postgresql -- \
      psql -U "$DB_USER" -c "DROP DATABASE IF EXISTS ${DB_NAME}_old;"
    kubectl exec -n podtranslate deployment/postgresql -- \
      psql -U "$DB_USER" -c "ALTER DATABASE $DB_NAME RENAME TO ${DB_NAME}_old;"
    kubectl exec -n podtranslate deployment/postgresql -- \
      psql -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;"

    # Restore
    gunzip < "$postgres_dump" | \
      kubectl exec -i -n podtranslate deployment/postgresql -- \
      pg_restore -U "$DB_USER" -d "$DB_NAME" -v
  else
    psql -h "$DB_HOST" -U "$DB_USER" -c "DROP DATABASE IF EXISTS ${DB_NAME}_old;"
    psql -h "$DB_HOST" -U "$DB_USER" -c "ALTER DATABASE $DB_NAME RENAME TO ${DB_NAME}_old;"
    psql -h "$DB_HOST" -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;"

    gunzip < "$postgres_dump" | pg_restore -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -v
  fi

  log "✓ PostgreSQL database restored"
}

# Restore S3 data
restore_s3() {
  local backup_path=$1

  if [ ! -d "$backup_path/s3_data" ]; then
    warn "S3 data not found in backup (manifest-only backup)"
    return
  fi

  log "Restoring S3 data..."

  read -p "⚠️  This will upload files to S3. Continue? (yes/no): " confirm
  if [ "$confirm" != "yes" ]; then
    log "S3 restore skipped"
    return
  fi

  aws s3 sync "$backup_path/s3_data/audio" "s3://$S3_AUDIO_BUCKET" --quiet
  aws s3 sync "$backup_path/s3_data/transcripts" "s3://$S3_TRANSCRIPTS_BUCKET" --quiet

  log "✓ S3 data restored"
}

# Restore Kubernetes resources
restore_kubernetes() {
  local backup_path=$1

  if [ ! -d "$backup_path/k8s" ]; then
    warn "Kubernetes resources not found in backup"
    return
  fi

  log "Restoring Kubernetes resources..."

  read -p "⚠️  This will modify Kubernetes resources. Continue? (yes/no): " confirm
  if [ "$confirm" != "yes" ]; then
    log "Kubernetes restore skipped"
    return
  fi

  # Apply resources (excluding secrets for safety)
  for file in "$backup_path/k8s"/*.yaml; do
    if [ "$(basename "$file")" != "secrets.yaml" ]; then
      kubectl apply -f "$file" -n podtranslate || warn "Failed to apply $(basename "$file")"
    fi
  done

  log "✓ Kubernetes resources restored (secrets excluded)"
}

# Verify restore
verify_restore() {
  log "Verifying restore..."

  # Check database connectivity
  if [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
    kubectl exec -n podtranslate deployment/postgresql -- \
      psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT COUNT(*) FROM users;" > /dev/null
  else
    psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT COUNT(*) FROM users;" > /dev/null
  fi

  log "✓ Database connectivity verified"
}

# Main restore function
main() {
  local backup_name=$1

  if [ -z "$backup_name" ]; then
    list_backups
    echo "Usage: $0 <backup_name>"
    echo "Example: $0 20240115_120000.tar.gz"
    exit 1
  fi

  log "Starting PodTranslate restore..."
  log "Backup: $backup_name"

  # Download from S3 if needed
  local backup_file
  if [ -n "$S3_BACKUP_BUCKET" ] && [ ! -f "$BACKUP_DIR/$backup_name" ]; then
    backup_file=$(download_from_s3 "$backup_name")
  else
    backup_file="$BACKUP_DIR/$backup_name"
  fi

  if [ ! -f "$backup_file" ]; then
    error "Backup file not found: $backup_file"
  fi

  # Extract backup
  local backup_path=$(extract_backup "$backup_file")
  log "Backup extracted to: $backup_path"

  # Show metadata
  if [ -f "$backup_path/metadata.json" ]; then
    log "Backup metadata:"
    cat "$backup_path/metadata.json"
    echo ""
  fi

  # Restore components
  restore_postgres "$backup_path"
  restore_s3 "$backup_path" || warn "S3 restore failed (non-fatal)"

  if [ "$DEPLOYMENT_TYPE" = "kubernetes" ]; then
    restore_kubernetes "$backup_path" || warn "Kubernetes restore failed (non-fatal)"
  fi

  # Verify
  verify_restore

  # Cleanup
  rm -rf "$backup_path"

  log "✅ Restore completed successfully!"
  log ""
  log "Next steps:"
  log "1. Verify application functionality"
  log "2. Check data integrity"
  log "3. Remove old database: DROP DATABASE ${DB_NAME}_old;"
}

# Run main function
main "$@"
