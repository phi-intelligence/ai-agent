# Orchestrator Service

FastAPI service for orchestrating agent workflows using LangGraph.

## Setup

1. Install dependencies:
   ```bash
   pip install poetry
   poetry install
   ```

2. Create `.env` file:
   ```bash
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/phi_agents
   CORE_API_URL=http://localhost:8000
   OPENAI_API_KEY=your-openai-api-key
   ```

3. Start the server:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

The orchestrator will be available at http://localhost:8001

## API Endpoints

- `POST /agents/{agent_id}/run-task` - Run a task for an agent
- `GET /tasks/{task_id}` - Get task status and results

## Workflows

Currently implemented:
- `DAILY_WAREHOUSE_REPORT` - Daily warehouse analysis workflow

Workflows use LangGraph to orchestrate multiple steps:
1. Load agent config
2. Fetch relevant documents
3. Fetch WMS data (stub for now)
4. LLM analysis
5. Format report
6. Save results


