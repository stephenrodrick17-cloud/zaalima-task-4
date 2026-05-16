#!/bin/bash

# Start script for Infrastructure Damage Detection System
# This script builds the frontend and starts the FastAPI backend

echo "=========================================="
echo "RoadGuard AI - Infrastructure Damage Detection"
echo "=========================================="
echo ""

# Set environment variables
export PORT=8000

# Install backend dependencies
echo "[1/4] Installing backend dependencies..."
pip install --no-cache-dir -r requirements.txt

# Install frontend dependencies and build
echo "[2/4] Installing frontend dependencies..."
cd frontend
npm install
echo "[3/4] Building frontend..."
npm run build
cd ..

# Start the backend server
echo "[4/4] Starting backend server..."
echo ""
echo "Server starting on http://localhost:$PORT"
echo "API Documentation: http://localhost:$PORT/docs"
echo "=========================================="

uvicorn backend.main:app --host 0.0.0.0 --port $PORT --reload
