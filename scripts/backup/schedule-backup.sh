#!/bin/bash
#
# Schedule automated backups with cron
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Cron schedule (daily at 2 AM)
CRON_SCHEDULE="${CRON_SCHEDULE:-0 2 * * *}"

# Create cron job
CRON_JOB="$CRON_SCHEDULE $SCRIPT_DIR/backup.sh >> /var/log/podtranslate-backup.log 2>&1"

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Backup scheduled: $CRON_SCHEDULE"
echo "Logs: /var/log/podtranslate-backup.log"
echo ""
echo "To view scheduled backups:"
echo "  crontab -l"
echo ""
echo "To remove scheduled backups:"
echo "  crontab -r"
