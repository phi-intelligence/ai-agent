# Next Steps Completion Status

## ✅ Completed Steps

### 1. Database Migrations

**Orchestrator:**
- Migration `002_add_task_progress.py` created
- Run: `cd apps/orchestrator && source .venv/bin/activate && alembic upgrade head`

**Core API:**
- Existing migrations should be up to date
- Run: `cd apps/core-api && source .venv/bin/activate && alembic upgrade head`

### 2. Dependencies Installation

**Local Agent:**
- Added dependencies: `playwright`, `streamlit`, `plotly`
- Run: `cd apps/local-agent && poetry install`
- Then: `playwright install chromium`

**Frontend:**
- Added dependency: `@radix-ui/react-progress` (optional, using custom progress bar)
- Run: `cd apps/web && npm install`

### 3. Environment Configuration

**Required Environment Variables:**

#### Core API (`apps/core-api/.env`)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/phi_agents
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=sk-proj-your-key-here
```

#### Orchestrator (`apps/orchestrator/.env`)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/phi_orchestrator
CORE_API_URL=http://localhost:8000
OPENAI_API_KEY=sk-proj-your-key-here

# Optional: Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com

# Optional: Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

#### Local Agent (`apps/local-agent/.env`)
```env
ORCHESTRATOR_URL=http://localhost:8001
CORE_API_URL=http://localhost:8000
DB_DSN=postgresql://user:pass@localhost:5432/wms  # Optional
FILE_BASE_PATH=/var/phi  # Optional
```

## 🚀 Quick Start Commands

### Start Database
```bash
cd infra/docker
docker-compose up -d
```

### Start Core API
```bash
cd apps/core-api
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Start Orchestrator
```bash
cd apps/orchestrator
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

### Start Frontend
```bash
cd apps/web
npm run dev -- -p 3001
```

### Start Local Agent (when testing)
```bash
cd apps/local-agent
source .venv/bin/activate
phi-agent run --config /path/to/agent-config.yaml
```

## ✅ Verification Checklist

- [ ] Database is running (check with `docker ps`)
- [ ] Core API migrations run successfully
- [ ] Orchestrator migrations run successfully
- [ ] All Python dependencies installed
- [ ] Frontend dependencies installed
- [ ] Playwright browsers installed (`playwright install chromium`)
- [ ] Environment variables configured
- [ ] All services can start without errors

## 📝 Notes

- Make sure Docker is running before starting database
- Run migrations before starting services
- Install Playwright browsers for WebTool to work
- Configure email/Slack only if you plan to use notifications

## 🐛 Troubleshooting

If migrations fail:
1. Check database is running: `docker ps`
2. Verify DATABASE_URL in .env files
3. Check database connection: `psql -h localhost -p 5433 -U postgres -d phi_orchestrator`

If dependencies fail:
1. Make sure Python 3.11+ is installed
2. Make sure Node.js 18+ is installed
3. Try: `poetry install --no-cache` for Python
4. Try: `npm install --force` for Node

If services won't start:
1. Check ports 8000, 8001, 3001 are available
2. Check environment variables are set
3. Check logs for specific errors

