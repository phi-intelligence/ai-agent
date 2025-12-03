#!/bin/bash

# Start development environment

echo "Starting Phi Agents development environment..."

# Start database
echo "Starting PostgreSQL database..."
cd ../../infra/docker
docker-compose up -d

# Wait for database to be ready
echo "Waiting for database..."
sleep 5

# Start backend
echo "Starting Core API..."
cd ../../apps/core-api
# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q poetry
poetry install
echo "Starting FastAPI server..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting Next.js app..."
cd ../web
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================="
echo "Development environment started!"
echo "========================================="
echo "Database: http://localhost:5432"
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo "========================================="

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; docker-compose down; exit" INT
wait


