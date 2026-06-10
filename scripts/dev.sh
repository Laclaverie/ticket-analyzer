#!/bin/bash

# Ticket Analyzer - Unified Development Launcher
# Starts API, Worker, and Web Client in development mode.

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Ticket Analyzer development environment...${NC}"

# Create data directory in root if it doesn't exist
mkdir -p data

# Kill existing processes on relevant ports
echo "Checking for existing processes..."
PORT_8000_PID=$(lsof -t -i :8000)
if [ ! -z "$PORT_8000_PID" ]; then
    echo "Killing process on port 8000: $PORT_8000_PID"
    kill $PORT_8000_PID
fi

PORT_5173_PID=$(lsof -t -i :5173)
if [ ! -z "$PORT_5173_PID" ]; then
    echo "Killing process on port 5173: $PORT_5173_PID"
    kill $PORT_5173_PID
fi

# Set shared environment variables
export DATABASE_URL="sqlite:///$(pwd)/data/ticket_analyzer.db"
export STORAGE_PATH="$(pwd)/data/images"

# 1. API Service
echo -e "${GREEN}Launching API Service (port 8000)...${NC}"
(cd apps/api-service && uv run uvicorn api_service.main:app --host 0.0.0.0 --port 8000) > api.log 2>&1 &
API_PID=$!

# 2. Worker Service
echo -e "${GREEN}Launching Worker Service...${NC}"
(cd apps/worker-service && uv run python -m worker_service.main) > worker.log 2>&1 &
WORKER_PID=$!

# 3. Web Client
echo -e "${GREEN}Launching Web Client (port 5173)...${NC}"
(cd apps/web-client && npm run dev -- --host 0.0.0.0) > web.log 2>&1 &
WEB_PID=$!

echo -e "${BLUE}All services launched!${NC}"
echo -e "API:    http://localhost:8000"
echo -e "Web:    http://localhost:5173"
echo -e "Logs:   api.log, worker.log, web.log"
echo -e "Data:   $(pwd)/data"
echo ""
echo "Press Ctrl+C to stop all services."

# Handle shutdown
trap "kill $API_PID $WORKER_PID $WEB_PID; echo -e '\n${BLUE}Services stopped.${NC}'; exit" INT

# Keep script running
wait
