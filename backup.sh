#!/bin/bash
# Database Backup Script

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/iolta_backup_${DATE}.sql"

mkdir -p $BACKUP_DIR

echo "Creating database backup..."
docker-compose -f docker-compose.prod.yml exec -T database pg_dump -U iolta_user -d iolta_guard_db > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Backup created: $BACKUP_FILE"
    gzip "$BACKUP_FILE"
    echo "✓ Compressed: ${BACKUP_FILE}.gz"
    
    # Keep only last 7 days of backups
    find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
    echo "✓ Old backups cleaned"
else
    echo "✗ Backup failed"
    exit 1
fi
