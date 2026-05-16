#!/bin/bash

# Start Backend and Frontend Services for Development
# This script starts both services in the background

set -e

BACKEND_PORT=8000
FRONTEND_PORT=3000
BACKEND_PATH="."
FRONTEND_PATH="./frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Infrastructure Damage Detection - Service Startup        ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $(python3 --version)${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 16+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node $(node --version)${NC}"

echo ""
echo -e "${CYAN}📋 Configuration:${NC}"
echo -e "   Backend:  http://localhost:$BACKEND_PORT"
echo -e "   Frontend: http://localhost:$FRONTEND_PORT"
echo -e "   API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Services stopped${NC}"
}

trap cleanup EXIT

# Start Backend
echo -e "${YELLOW}🚀 Starting Backend (Port $BACKEND_PORT)...${NC}"
cd "$BACKEND_PATH"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source ".venv/bin/activate"
elif [ -f "venv/bin/activate" ]; then
    source "venv/bin/activate"
fi

python3 -m uvicorn backend.main:app \
    --reload \
    --host 0.0.0.0 \
    --port $BACKEND_PORT \
    > backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Wait a moment for backend to start
sleep 2

# Start Frontend
echo -e "${YELLOW}🚀 Starting Frontend (Port $FRONTEND_PORT)...${NC}"
cd "$FRONTEND_PATH"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}   Installing dependencies...${NC}"
    npm install
fi

npm start > frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

# Check health
echo ""
echo -e "${YELLOW}⏳ Checking service health...${NC}"
sleep 3

for i in {1..10}; do
    if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
        break
    fi
    echo -e "${YELLOW}   Attempt $i/10...${NC}"
    sleep 1
done

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✅ All Services Running Successfully!            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"

echo ""
echo -e "${CYAN}📱 Access points:${NC}"
echo -e "   🌐 Frontend:     http://localhost:$FRONTEND_PORT"
echo -e "   🔌 Backend API:  http://localhost:$BACKEND_PORT/api"
echo -e "   📚 API Docs:     http://localhost:$BACKEND_PORT/docs"
echo -e "   💚 Health:       http://localhost:$BACKEND_PORT/health"

echo ""
echo -e "${CYAN}📝 View logs:${NC}"
echo -e "   Backend:  tail -f backend.log"
echo -e "   Frontend: tail -f frontend.log"

echo ""
echo -e "${YELLOW}Press Ctrl+C to stop services${NC}"

# Keep script running
wait
