# Phi Agents

A platform where companies create virtual employees (agents) tailored to their industry & role, upload job descriptions / SOPs, and download a local agent that runs on their infrastructure with system-level access.

## Architecture

- **Web App** (Next.js) - Agent Factory UI
- **Core API** (FastAPI) - Auth, users, organizations, agents, documents
- **Orchestrator** (FastAPI + LangGraph) - Task execution and workflows
- **Local Agent** (Python CLI) - On-premise agent runtime

## Development

See `PLAN.md` for the complete implementation roadmap.

### Quick Start

1. Start infrastructure:
   ```bash
   docker-compose up -d
   ```

2. Run migrations:
   ```bash
   cd apps/core-api
   alembic upgrade head
   ```

3. Start services:
   ```bash
   # Backend
   cd apps/core-api
   uvicorn main:app --reload

   # Frontend
   cd apps/web
   npm run dev
   ```


