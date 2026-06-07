#!/bin/bash

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Configuration
BACKUP_DIR="/d/Turing/python_begineer/Projects/Metalytics/backup/db/"  # Where database backups will be stored
TIMESTAMP=$(date +"%Y%m%d%H%M")
DB_BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Backup the PostgreSQL database
echo "Starting database backup..."
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -F c $DB_NAME > $DB_BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "Database backup successful: $DB_BACKUP_FILE"
else
    echo "Database backup failed"
    exit 1
fi

# Keep only the last 20 database backups
echo "Cleaning up old database backups..."
cd $BACKUP_DIR
ls -1tr | head -n -20 | xargs -d '\n' rm -f --

echo "Database backup process completed successfully."
