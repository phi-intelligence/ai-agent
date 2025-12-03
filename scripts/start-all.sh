#!/bin/bash

set -e

echo "========================================="
echo "Starting Phi Agents Platform"
echo "========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Start database
echo ""
echo "📦 Starting PostgreSQL database..."
cd "$(dirname "$0")/../infra/docker"
docker-compose up -d

# Wait for database
echo "⏳ Waiting for database to be ready..."
sleep 5

# Check database connection
until docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; do
    echo "   Waiting for database..."
    sleep 2
done
echo "✅ Database is ready"

# Run migrations for core-api
echo ""
echo "🔄 Running database migrations (core-api)..."
cd "$(dirname "$0")/../apps/core-api"
if [ ! -d ".venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q poetry
poetry install
alembic upgrade head
echo "✅ Core API migrations complete"

# Run migrations for orchestrator
echo ""
echo "🔄 Running database migrations (orchestrator)..."
cd "$(dirname "$0")/../apps/orchestrator"
if [ ! -d ".venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q poetry
poetry install
alembic upgrade head
echo "✅ Orchestrator migrations complete"

# Seed initial data
echo ""
echo "🌱 Seeding initial data..."
cd "$(dirname "$0")/../apps/core-api"
source .venv/bin/activate
python scripts/seed_data.py || echo "⚠️  Seed data script may have already run"
echo "✅ Data seeding complete"

# Check for .env files
echo ""
echo "📝 Checking environment configuration..."
if [ ! -f "$(dirname "$0")/../apps/core-api/.env" ]; then
    echo "⚠️  Warning: apps/core-api/.env not found. Creating template..."
    cat > "$(dirname "$0")/../apps/core-api/.env" << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/phi_agents
SECRET_KEY=your-secret-key-change-in-production
OPENAI_API_KEY=your-openai-api-key-here
EOF
    echo "   Please update apps/core-api/.env with your OpenAI API key"
fi

if [ ! -f "$(dirname "$0")/../apps/orchestrator/.env" ]; then
    echo "⚠️  Warning: apps/orchestrator/.env not found. Creating template..."
    cat > "$(dirname "$0")/../apps/orchestrator/.env" << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/phi_agents
CORE_API_URL=http://localhost:8000
OPENAI_API_KEY=your-openai-api-key-here
EOF
    echo "   Please update apps/orchestrator/.env with your OpenAI API key"
fi

if [ ! -f "$(dirname "$0")/../apps/web/.env.local" ]; then
    echo "⚠️  Warning: apps/web/.env.local not found. Creating template..."
    cat > "$(dirname "$0")/../apps/web/.env.local" << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ORCHESTRATOR_URL=http://localhost:8001
EOF
fi

# Start services
echo ""
echo "🚀 Starting services..."
echo ""

# Start Core API
echo "   Starting Core API (port 8000)..."
cd "$(dirname "$0")/../apps/core-api"
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000 > /tmp/phi-core-api.log 2>&1 &
CORE_API_PID=$!
echo "   Core API PID: $CORE_API_PID"

# Wait a bit for core API to start
sleep 3

# Start Orchestrator
echo "   Starting Orchestrator (port 8001)..."
cd "$(dirname "$0")/../apps/orchestrator"
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001 > /tmp/phi-orchestrator.log 2>&1 &
ORCHESTRATOR_PID=$!
echo "   Orchestrator PID: $ORCHESTRATOR_PID"

# Wait a bit for orchestrator to start
sleep 3

# Start Web Frontend
echo "   Starting Web Frontend (port 3000)..."
cd "$(dirname "$0")/../apps/web"
if [ ! -d "node_modules" ]; then
    echo "   Installing npm dependencies..."
    npm install
fi
npm run dev > /tmp/phi-web.log 2>&1 &
WEB_PID=$!
echo "   Web Frontend PID: $WEB_PID"

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
check_service() {
    local name=$1
    local url=$2
    local pid=$3
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✅ $name is running"
        return 0
    else
        echo "❌ $name is not responding (PID: $pid)"
        return 1
    fi
}

check_service "Core API" "http://localhost:8000/docs" "$CORE_API_PID"
check_service "Orchestrator" "http://localhost:8001/docs" "$ORCHESTRATOR_PID"
check_service "Web Frontend" "http://localhost:3000" "$WEB_PID"

echo ""
echo "========================================="
echo "✅ All services started!"
echo "========================================="
echo ""
echo "📍 Services:"
echo "   Database:     postgresql://postgres:postgres@localhost:5432/phi_agents"
echo "   Core API:     http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Orchestrator: http://localhost:8001"
echo "   Orchestrator Docs: http://localhost:8001/docs"
echo "   Web Frontend: http://localhost:3000"
echo ""
echo "📋 Logs:"
echo "   Core API:     tail -f /tmp/phi-core-api.log"
echo "   Orchestrator: tail -f /tmp/phi-orchestrator.log"
echo "   Web:          tail -f /tmp/phi-web.log"
echo ""
echo "🛑 To stop all services:"
echo "   ./scripts/stop-all.sh"
echo "   or kill $CORE_API_PID $ORCHESTRATOR_PID $WEB_PID"
echo ""
echo "💡 Make sure to set OPENAI_API_KEY in:"
echo "   - apps/core-api/.env"
echo "   - apps/orchestrator/.env"
echo "========================================="

# Save PIDs to file for stop script
echo "$CORE_API_PID $ORCHESTRATOR_PID $WEB_PID" > /tmp/phi-agents-pids.txt

# Keep script running
wait


