#!/bin/bash
# Database Restore Script

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_file.sql>"
    echo "Example: ./restore.sh backups/iolta_backup_20251126_120000.sql.gz"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "WARNING: This will replace the current database!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Decompress if gzipped
if [[ $BACKUP_FILE == *.gz ]]; then
    echo "Decompressing backup..."
    gunzip -c "$BACKUP_FILE" > /tmp/restore_temp.sql
    RESTORE_FILE="/tmp/restore_temp.sql"
else
    RESTORE_FILE="$BACKUP_FILE"
fi

echo "Stopping backend..."
docker-compose -f docker-compose.prod.yml stop backend

echo "Dropping and recreating database..."
docker-compose -f docker-compose.prod.yml exec -T database psql -U iolta_user -c "DROP DATABASE IF EXISTS iolta_guard_db;"
docker-compose -f docker-compose.prod.yml exec -T database psql -U iolta_user -c "CREATE DATABASE iolta_guard_db;"

echo "Restoring database..."
docker-compose -f docker-compose.prod.yml exec -T database psql -U iolta_user -d iolta_guard_db < "$RESTORE_FILE"

# Cleanup temp file
if [ -f "/tmp/restore_temp.sql" ]; then
    rm /tmp/restore_temp.sql
fi

echo "Starting backend..."
docker-compose -f docker-compose.prod.yml start backend

echo "✓ Database restored successfully"
