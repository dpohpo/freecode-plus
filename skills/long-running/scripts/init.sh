#!/bin/bash
# init.sh - Project Environment Startup Script
# This script starts all necessary services for the project

set -e

echo "=========================================="
echo "Starting project environment..."
echo "=========================================="

# Kill any existing servers (cleanup from previous sessions)
echo "Cleaning up existing processes..."
pkill -f "node.*server.js" 2>/dev/null || true
pkill -f "node.*app.js" 2>/dev/null || true
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python.*server.py" 2>/dev/null || true

# Wait for cleanup
sleep 1

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Start backend (if exists)
if [ -d "backend" ]; then
    echo "Starting backend..."
    cd backend

    # Install dependencies if needed
    if [ -f "package.json" ] && [ ! -d "node_modules" ]; then
        echo "Installing backend dependencies..."
        npm install
    fi

    # Start backend server
    if [ -f "package.json" ]; then
        npm start &
        BACKEND_PID=$!
        echo "Backend started (PID: $BACKEND_PID)"
    fi

    cd "$SCRIPT_DIR"
fi

# Start frontend (if exists)
if [ -d "frontend" ]; then
    echo "Starting frontend..."
    cd frontend

    # Install dependencies if needed
    if [ -f "package.json" ] && [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi

    # Start frontend server
    if [ -f "package.json" ]; then
        npm start &
        FRONTEND_PID=$!
        echo "Frontend started (PID: $FRONTEND_PID)"
    fi

    cd "$SCRIPT_DIR"
fi

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 3

# Health check
echo "Performing health check..."

check_service() {
    local url=$1
    local name=$2
    local max_attempts=10
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✓ $name is ready at $url"
            return 0
        fi
        echo "  Waiting for $name... (attempt $attempt/$max_attempts)"
        sleep 1
        attempt=$((attempt + 1))
    done

    echo "✗ $name failed to start"
    return 1
}

# Check backend
if [ -d "backend" ]; then
    check_service "http://localhost:3001/health" "Backend" || true
fi

# Check frontend
if [ -d "frontend" ]; then
    check_service "http://localhost:3000" "Frontend" || true
fi

echo "=========================================="
echo "Environment startup complete!"
echo "=========================================="

# Keep script running to maintain background processes
wait
