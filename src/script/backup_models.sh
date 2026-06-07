#!/bin/bash

# Define backup directory
BACKUP_DIR="/d/Turing/python_begineer/Projects/Metalytics/backup/trained_models"
SOURCE_DIR="/d/Turing/python_begineer/Projects/Metalytics/trained_models/"  # Directory where .zip models are stored
TIMESTAMP=$(date +"%Y%m%d_%H%M")

# Copy zipped models to backup directory with timestamp
mkdir -p "$BACKUP_DIR"
for model in $SOURCE_DIR/*.zip; do
    cp "$model" "$BACKUP_DIR/$(basename $model .zip)_$TIMESTAMP.zip"
done

echo "Model backups completed at $TIMESTAMP"
