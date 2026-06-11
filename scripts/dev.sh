#!/bin/bash

# Ticket Analyzer - Development Environment Setup
# Sets up the shared environment for all services.

# Find the repository root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Use absolute paths for the shared data directory
export DATA_ROOT="$REPO_ROOT/data"
export DATABASE_URL="sqlite:///$DATA_ROOT/ticket_analyzer.db"
export STORAGE_PATH="$DATA_ROOT/images"

mkdir -p "$STORAGE_PATH"

echo "--------------------------------------------------------"
echo "Ticket Analyzer Environment Ready"
echo "--------------------------------------------------------"
echo "REPO_ROOT:    $REPO_ROOT"
echo "DATABASE_URL: $DATABASE_URL"
echo "STORAGE_PATH: $STORAGE_PATH"
echo "--------------------------------------------------------"
echo ""
echo "To run the services in separate terminals, copy these commands:"
echo ""
echo "Terminal 1 (API):"
echo "export DATABASE_URL=\"$DATABASE_URL\" && export STORAGE_PATH=\"$STORAGE_PATH\" && cd $REPO_ROOT/apps/api-service && uv run uvicorn api_service.main:app --reload"
echo ""
echo "Terminal 2 (Worker):"
echo "export DATABASE_URL=\"$DATABASE_URL\" && export STORAGE_PATH=\"$STORAGE_PATH\" && cd $REPO_ROOT/apps/worker-service && uv run python -m worker_service.main"
echo ""
echo "Terminal 3 (Web):"
echo "cd $REPO_ROOT/apps/web-client && npm run dev"
echo ""
echo "Tip: Run './scripts/reset_db.sh' if you want to start with a fresh shared database."
