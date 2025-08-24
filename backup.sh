#!/bin/bash

# Database backup script for Water Level Dashboard

BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_FILE="data/real_time_data.db"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo "❌ Database file not found: $DB_FILE"
    exit 1
fi

# Create backup
BACKUP_FILE="$BACKUP_DIR/water_data_backup_$TIMESTAMP.db"
cp "$DB_FILE" "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Database backed up successfully to: $BACKUP_FILE"
    
    # Show backup info
    echo "📊 Backup information:"
    echo "  Size: $(du -h "$BACKUP_FILE" | cut -f1)"
    echo "  Records: $(sqlite3 "$BACKUP_FILE" "SELECT COUNT(*) FROM water_data;" 2>/dev/null || echo "Unable to count")"
    
    # Clean up old backups (keep last 10)
    echo "🧹 Cleaning up old backups..."
    ls -t "$BACKUP_DIR"/water_data_backup_*.db | tail -n +11 | xargs rm -f 2>/dev/null
    
    echo "📁 Current backups:"
    ls -la "$BACKUP_DIR"/water_data_backup_*.db 2>/dev/null | wc -l | xargs echo "  Total backups:"
else
    echo "❌ Backup failed!"
    exit 1
fi
