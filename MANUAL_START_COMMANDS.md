# Manual Startup Commands

Follow these commands in separate terminal windows to start each service manually and see the output.

## Prerequisites

1. **Start Docker Desktop** (if not already running)
   ```bash
   # Check if Docker is running
   docker ps
   
   # If not running, start Docker Desktop manually from Applications
   ```

2. **Start the Database**
   ```bash
   cd /Users/marysonmarceline/Downloads/ai-agent/infra/docker
   docker-compose up
   ```
   Keep this terminal open. You'll see database logs here.

## Terminal 1: Database (PostgreSQL)

```bash
cd /Users/marysonmarceline/Downloads/ai-agent/infra/docker
docker-compose up
```

Wait until you see: `database system is ready to accept connections`

## Terminal 2: Core API

```bash
cd /Users/marysonmarceline/Downloads/ai-agent/apps/core-api
source .venv/bin/activate
export OPENAI_API_KEY="your-openai-api-key-here"
uvicorn app.main:app --reload --port 8000
```

You should see:
- `INFO:     Uvicorn running on http://127.0.0.1:8000`
- `INFO:     Application startup complete.`
- API will be available at: http://localhost:8000/docs

## Terminal 3: Orchestrator

```bash
cd /Users/marysonmarceline/Downloads/ai-agent/apps/orchestrator
source .venv/bin/activate
export OPENAI_API_KEY="your-openai-api-key-here"
uvicorn app.main:app --reload --port 8001
```

You should see:
- `INFO:     Uvicorn running on http://127.0.0.1:8001`
- `INFO:     Application startup complete.`
- API will be available at: http://localhost:8001/docs

## Terminal 4: Web Frontend

```bash
cd /Users/marysonmarceline/Downloads/ai-agent/apps/web
PORT=3001 npm run dev
```

You should see:
- `✓ Ready in X.Xs`
- `○ Compiling / ...`
- Frontend will be available at: http://localhost:3001

## Verification

Once all services are running, verify they're working:

```bash
# Check Core API
curl http://localhost:8000/health

# Check Orchestrator
curl http://localhost:8001/health

# Check Web Frontend (should return HTML)
curl http://localhost:3001
```

## Stopping Services

To stop services, press `Ctrl+C` in each terminal window.

To stop the database:
```bash
cd /Users/marysonmarceline/Downloads/ai-agent/infra/docker
docker-compose down
```

## Troubleshooting

### If Core API or Orchestrator fail to start:
- Make sure the database is running first
- Check that virtual environments are activated: `which python` should show `.venv/bin/python`
- Verify API keys are set: `echo $OPENAI_API_KEY`

### If you see port already in use errors:
```bash
# Find what's using the port
lsof -i :8000
lsof -i :8001
lsof -i :3001

# Kill the process
kill -9 <PID>
```

### If database connection fails:
- Make sure Docker is running: `docker ps`
- Check database is up: `docker-compose ps` (in infra/docker directory)
- Verify DATABASE_URL in .env files points to port 5433

