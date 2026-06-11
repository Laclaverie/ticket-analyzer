#!/bin/bash

# Ticket Analyzer - Reset Database and Storage
# Deletes ALL accidental data directories to start fresh at the repo root.

set -e

# Find the repository root (directory where this script's parent 'scripts' resides)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Repository root detected at: $REPO_ROOT"

# List of known accidental or old data locations
DATA_LOCATIONS=(
    "$REPO_ROOT/data"
    "$REPO_ROOT/apps/api-service/data"
    "$REPO_ROOT/apps/worker-service/data"
    "$REPO_ROOT/scripts/data"
    "$REPO_ROOT/apps/api-service/ticket_analyzer.db"
    "$REPO_ROOT/apps/worker-service/ticket_analyzer.db"
    "$REPO_ROOT/apps/api-service/images"
    "$REPO_ROOT/apps/worker-service/images"
)

echo "Cleaning up data directories and accidental files..."

for LOC in "${DATA_LOCATIONS[@]}"; do
    if [ -e "$LOC" ]; then
        echo "Removing: $LOC"
        rm -rf "$LOC"
    fi
done

# Initialize fresh directory at root
mkdir -p "$REPO_ROOT/data/images"
echo "Created fresh shared data directory at $REPO_ROOT/data"
echo "Done."
