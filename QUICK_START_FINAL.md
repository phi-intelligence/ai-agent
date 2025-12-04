# Quick Start - Final Checklist

## ✅ Already Completed

1. ✅ All code implementation (Phases 1-13)
2. ✅ Database migrations created and run
3. ✅ Frontend dependencies installed
4. ✅ Migration conflicts resolved

## 🚀 Quick Start (5 minutes)

### 1. Start Database
```bash
cd infra/docker
docker-compose up -d
```

### 2. Install Local Agent Dependencies
```bash
cd apps/local-agent
poetry install
playwright install chromium
```

### 3. Start Services (4 terminals)

**Terminal 1: Core API**
```bash
cd apps/core-api
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2: Orchestrator**
```bash
cd apps/orchestrator
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

**Terminal 3: Frontend**
```bash
cd apps/web
npm run dev -- -p 3001
```

**Terminal 4: Local Agent (optional, for testing)**
```bash
cd apps/local-agent
source .venv/bin/activate
phi-agent run --config /path/to/agent-config.yaml
```

### 4. Access Application
- Frontend: http://localhost:3001
- Core API Docs: http://localhost:8000/docs
- Orchestrator Docs: http://localhost:8001/docs

## ✅ Verification

1. Check all services are running:
   - Core API: `curl http://localhost:8000/health`
   - Orchestrator: `curl http://localhost:8001/health`
   - Frontend: Open http://localhost:3001

2. Test the flow:
   - Sign up / Login
   - Create organization
   - Create agent
   - Upload documents
   - Generate profile
   - Run a task
   - Watch progress bar update

## 🎯 You're Ready!

Everything is set up and ready to use. All features from PLAN.md are implemented and working.

