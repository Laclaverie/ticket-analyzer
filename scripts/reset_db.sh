#!/bin/bash

# Ticket Analyzer - Reset Database and Storage
# Deletes the data directory to start fresh.

set -e

DATA_DIR="$(pwd)/data"

echo "Resetting development data at $DATA_DIR..."

if [ -d "$DATA_DIR" ]; then
    rm -rf "$DATA_DIR"
    echo "Deleted existing data directory."
fi

mkdir -p "$DATA_DIR/images"
echo "Created fresh data directory structure."
echo "Done."
