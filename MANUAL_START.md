# Manual Startup Commands

Follow these commands step-by-step to start the Phi Agents platform manually.

## Prerequisites Check

```bash
# Check if Docker is running
docker info

# If Docker is not running, start Docker Desktop first!
```

## Step 1: Start Database

```bash
cd /Users/marysonmarceline/Downloads/ai-agent/infra/docker
docker-compose up -d

# Wait for database to be ready (about 5 seconds)
sleep 5

# Verify database is running
docker-compose ps
```

## Step 2: Set Up Environment Variables

**Core API (.env):**
```bash
cd /Users/marysonmarceline/Downloads/ai-agent/apps/core-api

# Create .env file if it doesn't exist
cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/phi_agents
SECRET_KEY=dev-secret-key-change-in-production
OPENAI_API_KEY=your-openai-api-key-here
EOF

# Edit with your OpenAI API key:
# nano .env
# or
# open .env
```

**Orchestrator (.env):**
```bash
cd /Users/marysonmarceline/Downloads/ai-agent/apps/orchestrator

# Create .env file if it doesn't exist
cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/phi_agents
CORE_API_URL=http://localhost:8000
OPENAI_API_KEY=your-openai-api-key-here
EOF

# Edit with your OpenAI API key:
# nano .env
# or
# open .env
```

**Web Frontend (.env.local):**
```bash
cd /Users/marysonmarceline/Downloads/ai-agent/apps/web

# Create .env.local file if it doesn't exist
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ORCHESTRATOR_URL=http://localhost:8001
EOF
```

## Step 3: Set Up Core API

```bash
cd /Users/marysonmarceline/Downloads/ai-agent/apps/core-api

# Create virtual environment (if not exists)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install poetry
poetry install

# Run migrations
alembic upgrade head

# Seed initial data (industries, roles, tools)
python scripts/seed_data.py
```

## Step 4: Set Up Orchestrator

```bash
cd /Users/marysonmarceline/Downloads/ai-agent/apps/orchestrator

# Create virtual environment (if not exists)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install poetry
poetry install

# Run migrations
alembic upgrade head
```

## Step 5: Set Up Web Frontend

```bash
cd /Users/marysonmarceline/Downloads/ai-agent/apps/web

# Install dependencies (first time only)
npm install
```

## Step 6: Start Services

Open **3 separate terminal windows/tabs**:

### Terminal 1: Core API
```bash
cd /Users/marysonmarceline/Downloads/ai-agent/apps/core-api
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Orchestrator
```bash
cd /Users/marysonmarceline/Downloads/ai-agent/apps/orchestrator
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

### Terminal 3: Web Frontend
```bash
cd /Users/marysonmarceline/Downloads/ai-agent/apps/web
PORT=3001 npm run dev
```

## Step 7: Verify Services

Wait a few seconds, then check:

```bash
# Check Core API
curl http://localhost:8000/docs

# Check Orchestrator
curl http://localhost:8001/docs

# Check Web Frontend
curl http://localhost:3001
```

## Access URLs

- **Web Frontend**: http://localhost:3001
- **Core API Docs**: http://localhost:8000/docs
- **Orchestrator Docs**: http://localhost:8001/docs

## Quick Start (All in One)

If you want to run everything in one go (after initial setup):

```bash
# Terminal 1
cd /Users/marysonmarceline/Downloads/ai-agent/infra/docker && docker-compose up -d && sleep 5 && cd ../../apps/core-api && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Terminal 2
cd /Users/marysonmarceline/Downloads/ai-agent/apps/orchestrator && source .venv/bin/activate && uvicorn app.main:app --reload --port 8001

# Terminal 3
cd /Users/marysonmarceline/Downloads/ai-agent/apps/web && PORT=3001 npm run dev
```

## Troubleshooting

### Database Connection Error
```bash
# Check if database is running
docker ps | grep postgres

# Check database logs
cd /Users/marysonmarceline/Downloads/ai-agent/infra/docker
docker-compose logs db
```

### Port Already in Use
```bash
# Find what's using the port
lsof -i :8000
lsof -i :8001
lsof -i :3001

# Kill the process
kill -9 <PID>
```

### Migration Errors
```bash
# Reset database (WARNING: deletes all data)
cd /Users/marysonmarceline/Downloads/ai-agent/infra/docker
docker-compose down -v
docker-compose up -d
# Then run migrations again
```

### Module Not Found Errors
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
poetry install
```

## Stop Services

Press `Ctrl+C` in each terminal window, then:

```bash
# Stop database
cd /Users/marysonmarceline/Downloads/ai-agent/infra/docker
docker-compose down
```


