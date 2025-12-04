# Setup and Testing Guide

## ✅ All Implementation Complete

All phases from PLAN.md (1-13) have been implemented. This guide will help you set up and test everything.

---

## Prerequisites

1. **Python 3.11+** installed
2. **Node.js 18+** installed
3. **Docker Desktop** running
4. **Poetry** installed (for Python dependencies)
5. **PostgreSQL** (via Docker)

---

## Step 1: Database Setup

```bash
# Start database
cd infra/docker
docker-compose up -d

# Wait for database to be ready (about 10-15 seconds)
docker-compose ps
```

---

## Step 2: Install Dependencies

### Core API
```bash
cd apps/core-api
poetry install
```

### Orchestrator
```bash
cd apps/orchestrator
poetry install
```

### Local Agent
```bash
cd apps/local-agent
poetry install

# Install Playwright browsers (required for WebTool)
playwright install chromium
```

### Frontend
```bash
cd apps/web
npm install
```

---

## Step 3: Run Database Migrations

### Core API Migrations
```bash
cd apps/core-api
alembic upgrade head
```

### Orchestrator Migrations
```bash
cd apps/orchestrator
alembic upgrade head
```

---

## Step 4: Configure Environment Variables

### Core API (`apps/core-api/.env`)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/phi_agents
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=sk-proj-your-key-here
```

### Orchestrator (`apps/orchestrator/.env`)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/phi_orchestrator
CORE_API_URL=http://localhost:8000
OPENAI_API_KEY=sk-proj-your-key-here

# Optional: Email configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com

# Optional: Slack configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Local Agent (`apps/local-agent/.env`)
```env
ORCHESTRATOR_URL=http://localhost:8001
CORE_API_URL=http://localhost:8000
DB_DSN=postgresql://user:pass@localhost:5432/wms  # Optional: for DBTool
FILE_BASE_PATH=/var/phi  # Optional: for FileTool
```

---

## Step 5: Start Services

### Terminal 1: Database
```bash
cd infra/docker
docker-compose up
```

### Terminal 2: Core API
```bash
cd apps/core-api
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 3: Orchestrator
```bash
cd apps/orchestrator
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

### Terminal 4: Frontend
```bash
cd apps/web
npm run dev -- -p 3001
```

### Terminal 5: Local Agent (when testing)
```bash
cd apps/local-agent
source .venv/bin/activate
phi-agent run --config /path/to/agent-config.yaml
```

---

## Step 6: Test the Platform

### 1. Create Account
- Go to `http://localhost:3001`
- Sign up with email and password
- Login

### 2. Create Organization
- Create a new organization
- Note the organization ID

### 3. Create Agent
- Go to your organization
- Click "Create Agent"
- Select industry and role
- Upload documents (job descriptions, SOPs, etc.)
- Click "Generate Profile"
- Wait for profile generation

### 4. Download Agent Config
- On agent detail page
- Click "Download Config (YAML)"
- Save the config file

### 5. Run a Task
- On agent detail page
- Click "Run Test Task (Daily Warehouse Report)"
- Watch the progress bar update in real-time
- See current step updates
- View final report when complete

### 6. Test Local Agent (Optional)
- Edit the downloaded config file
- Add local database/file paths
- Start local agent:
  ```bash
  cd apps/local-agent
  phi-agent run --config /path/to/config.yaml
  ```
- Run a task that uses local tools
- Verify local agent executes tools

---

## Testing Individual Features

### Test Progress Tracking
1. Run a task
2. Watch progress bar update (0% → 100%)
3. See current step change
4. Check ETA if available

### Test Local Tools
1. Ensure local agent is running
2. Configure DBTool or FileTool in agent config
3. Run a task that uses these tools
4. Verify tools execute locally

### Test Browser Automation
1. Add WebTool to agent config
2. Run a task that uses WebTool
3. Verify browser automation works

### Test Dashboard Generation
1. Run a task that generates a dashboard
2. Look for "Open Dashboard" link in results
3. Click link to view Streamlit dashboard

### Test Notifications
1. Configure email/Slack in agent config
2. Run a task
3. Verify notifications are sent

---

## Troubleshooting

### Database Connection Issues
- Check Docker is running: `docker ps`
- Verify database is up: `docker-compose ps` in `infra/docker`
- Check port 5433 is not in use
- Verify DATABASE_URL in .env files

### Migration Issues
- Make sure you're in the correct directory
- Check database is accessible
- Try: `alembic current` to see current revision

### Local Agent Not Connecting
- Verify orchestrator is running on port 8001
- Check config file has correct `server.base_url`
- Check network connectivity
- Look at orchestrator logs for heartbeat messages

### Tool Execution Fails
- Verify local agent is running
- Check tool configuration in agent config
- Verify database/file paths are correct
- Check local agent logs for errors

### Frontend Not Loading
- Check all services are running
- Verify ports 8000, 8001, 3001 are available
- Check browser console for errors
- Verify CORS settings in backend

---

## Next Steps

1. **Customize Workflows**: Modify `warehouse_report.py` to add your own workflows
2. **Add More Tools**: Create new tools in `apps/local-agent/phi_agent/tools/`
3. **Configure Notifications**: Set up email/Slack for production
4. **Deploy**: Follow deployment guide for production setup
5. **Monitor**: Set up logging and monitoring

---

## Support

For issues or questions:
1. Check logs in each service terminal
2. Review error messages in frontend console
3. Check database for data consistency
4. Verify all environment variables are set

---

**Happy Testing! 🚀**

