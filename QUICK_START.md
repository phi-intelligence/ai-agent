# Quick Start Guide

## Prerequisites

1. **Docker Desktop** - Must be running
2. **Python 3.11+** - For backend services
3. **Node.js 18+** - For frontend
4. **OpenAI API Key** - For LLM features

## Option 1: Automated Start (Recommended)

```bash
# Make sure Docker Desktop is running first!
./scripts/start-all.sh
```

This script will:
- Start PostgreSQL database
- Run all migrations
- Seed initial data
- Start Core API (port 8000)
- Start Orchestrator (port 8001)
- Start Web Frontend (port 3000)

## Option 2: Manual Start

### Step 1: Start Database

```bash
cd infra/docker
docker-compose up -d
```

Wait for database to be ready (about 5 seconds).

### Step 2: Set Up Environment Variables

Create `.env` files:

**apps/core-api/.env**:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/phi_agents
SECRET_KEY=your-secret-key-change-in-production
OPENAI_API_KEY=your-openai-api-key-here
```

**apps/orchestrator/.env**:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/phi_agents
CORE_API_URL=http://localhost:8000
OPENAI_API_KEY=your-openai-api-key-here
```

**apps/web/.env.local**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ORCHESTRATOR_URL=http://localhost:8001
```

### Step 3: Run Migrations

**Core API**:
```bash
cd apps/core-api
python3 -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
alembic upgrade head
```

**Orchestrator**:
```bash
cd apps/orchestrator
python3 -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
alembic upgrade head
```

### Step 4: Seed Initial Data

```bash
cd apps/core-api
source .venv/bin/activate
python scripts/seed_data.py
```

### Step 5: Start Services

**Terminal 1 - Core API**:
```bash
cd apps/core-api
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Orchestrator**:
```bash
cd apps/orchestrator
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

**Terminal 3 - Web Frontend**:
```bash
cd apps/web
npm install
npm run dev
```

## Access the Application

- **Web Frontend**: http://localhost:3000
- **Core API Docs**: http://localhost:8000/docs
- **Orchestrator Docs**: http://localhost:8001/docs
- **Database**: postgresql://postgres:postgres@localhost:5432/phi_agents

## Testing the Application

1. **Sign Up**: Go to http://localhost:3000/signup
2. **Create Organization**: After login, create an organization
3. **Create Agent**: Navigate to your org and create an agent
4. **Upload Documents**: Upload documents to your agent
5. **Generate Profile**: Generate agent profile using LLM
6. **Run Task**: Test task execution

## Troubleshooting

### Docker not running
```bash
# Start Docker Desktop, then:
docker info  # Should work
```

### Port already in use
```bash
# Check what's using the port:
lsof -i :8000
lsof -i :8001
lsof -i :3000

# Kill the process or change ports in .env files
```

### Database connection errors
```bash
# Check if database is running:
docker ps

# Check database logs:
docker-compose -f infra/docker/docker-compose.yml logs db
```

### Migration errors
```bash
# Reset database (WARNING: deletes all data):
docker-compose -f infra/docker/docker-compose.yml down -v
docker-compose -f infra/docker/docker-compose.yml up -d
# Then run migrations again
```

### OpenAI API errors
- Make sure `OPENAI_API_KEY` is set in both `.env` files
- Verify your API key is valid
- Check API usage limits

## Stop All Services

```bash
./scripts/stop-all.sh
```

Or manually:
```bash
# Stop Docker
cd infra/docker
docker-compose down

# Stop Python services (Ctrl+C in each terminal)
# Stop Next.js (Ctrl+C)
```

