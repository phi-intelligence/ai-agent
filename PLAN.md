I’ll break it into:
Product & goals
Architecture overview
Tech stack (final)
Monorepo layout
Database schema (SQL-style)
APIs & services
Frontend (pages & components)
Orchestrator (LangGraph) design
Local agent design
Infra & environments
Phased execution roadmap with concrete tasks
You can literally say to Cursor: “Implement Phase 1 from PLAN.md”.
1. Product Definition & Goals
Product name: Phi Agents
Vision:
A platform where companies create virtual employees (agents) tailored to their industry & role, upload job descriptions / SOPs, and download a local agent that runs on their infrastructure with system-level access. The cloud does orchestration, memory, and reasoning. Local agents handle CCTV, databases, files, email, etc.
Key goals:
Multi-tenant, SaaS, highly scalable
Agent factory UI for configuring agents
Cloud brain for workflows + LLM reasoning
Local runtime for on-prem access
Later: run most LLM workloads on your own GPUs
2. High-Level Architecture
Components:
Web App (Agent Factory UI) – Next.js
Signup / login
Org & agent management
Upload docs (JDs, SOPs, policies)
Generate agent profile/config
Trigger manual tasks & view results
Core API (FastAPI)
Auth, users, organizations
Agents, industries, roles, tools
Documents & embeddings (pgvector)
Agent config export
Task metadata
Orchestrator (FastAPI + LangGraph)
Task execution
Agent workflows
Talk to LLMs via LLM Router (later)
Communicate with local agents (tool tasks)
Local Agent Runtime (Python)
Installed on customer machines
Loads downloaded config
Registers with cloud
Executes tools locally (DB, file, later CCTV)
Sends results back to orchestrator
Database (PostgreSQL + pgvector)
Multi-tenant relational data
Vector search over documents & memories
LLM Providers
Start: OpenAI for everything
Later: self-hosted Llama/Qwen + router
3. Tech Stack (Final Choice)
Frontend:
Next.js (App Router), TypeScript
Tailwind CSS + shadcn/ui
React Query (TanStack Query)
Backend / Services:
Python 3.11+
FastAPI
LangGraph
SQLAlchemy or Tortoise ORM (your choice; assume SQLAlchemy here)
DB & Vector:
PostgreSQL
pgvector extension
Local Agent:
Python CLI / service
Uses requests/httpx, sqlalchemy, pydantic
Infra (dev):
Docker & docker-compose
4. Monorepo Structure


phi-agents/
  apps/
    web/               # Next.js frontend
    core-api/          # FastAPI - core data & config
    orchestrator/      # FastAPI + LangGraph
    local-agent/       # Python CLI/service for customers
  packages/
    shared-types/      # DTOs, pydantic schemas, TS types
    shared-utils/      # logging, config helpers etc.
  infra/
    docker/            # Dockerfiles, compose
    db/                # migrations, seed scripts
  scripts/
    dev/               # helper scripts
  PLAN.md              # this document
  README.md


5. Database Schema (SQL-style)
You can use this as a starting migration.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  owner_user_id UUID REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE organization_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL, -- OWNER, ADMIN, MEMBER
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE industries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  key TEXT UNIQUE NOT NULL,   -- e.g. "logistics"
  name TEXT NOT NULL,
  description TEXT
);

CREATE TABLE role_templates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  industry_id UUID REFERENCES industries(id),
  key TEXT NOT NULL,          -- e.g. "warehouse_analyst"
  name TEXT NOT NULL,
  default_capabilities JSONB,
  default_tools JSONB,
  description TEXT
);

CREATE TABLE tools (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  key TEXT UNIQUE NOT NULL,   -- "db", "file", "cctv", "email", "browser"
  name TEXT NOT NULL,
  config_schema JSONB,        -- JSON schema for config UI
  description TEXT
);

CREATE TABLE agents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  industry_id UUID REFERENCES industries(id),
  role_template_id UUID REFERENCES role_templates(id),
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, DISABLED
  system_prompt TEXT,
  config JSONB,                          -- full agent definition
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE agent_tools (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  tool_id UUID REFERENCES tools(id),
  config JSONB          -- endpoint, db name, etc
);

CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  source_type TEXT NOT NULL, -- JD, SOP, POLICY, MANUAL, OTHER
  storage_path TEXT NOT NULL, -- local path or S3 key
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE document_chunks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
  chunk_text TEXT NOT NULL,
  embedding VECTOR(1536),     -- depends on embedding model size
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE local_agents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ENROLLED', -- ENROLLED, ACTIVE, OFFLINE
  last_heartbeat_at TIMESTAMP WITH TIME ZONE,
  metadata JSONB
);

CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  type TEXT NOT NULL, -- e.g. DAILY_WAREHOUSE_REPORT
  status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, RUNNING, SUCCESS, FAILED
  input JSONB,
  output JSONB,
  error TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE task_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
  event_type TEXT NOT NULL,
  payload JSONB
);
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  owner_user_id UUID REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE organization_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL, -- OWNER, ADMIN, MEMBER
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE industries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  key TEXT UNIQUE NOT NULL,   -- e.g. "logistics"
  name TEXT NOT NULL,
  description TEXT
);

CREATE TABLE role_templates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  industry_id UUID REFERENCES industries(id),
  key TEXT NOT NULL,          -- e.g. "warehouse_analyst"
  name TEXT NOT NULL,
  default_capabilities JSONB,
  default_tools JSONB,
  description TEXT
);

CREATE TABLE tools (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  key TEXT UNIQUE NOT NULL,   -- "db", "file", "cctv", "email", "browser"
  name TEXT NOT NULL,
  config_schema JSONB,        -- JSON schema for config UI
  description TEXT
);

CREATE TABLE agents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  industry_id UUID REFERENCES industries(id),
  role_template_id UUID REFERENCES role_templates(id),
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, DISABLED
  system_prompt TEXT,
  config JSONB,                          -- full agent definition
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE agent_tools (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  tool_id UUID REFERENCES tools(id),
  config JSONB          -- endpoint, db name, etc
);

CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  source_type TEXT NOT NULL, -- JD, SOP, POLICY, MANUAL, OTHER
  storage_path TEXT NOT NULL, -- local path or S3 key
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE document_chunks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
  chunk_text TEXT NOT NULL,
  embedding VECTOR(1536),     -- depends on embedding model size
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE local_agents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ENROLLED', -- ENROLLED, ACTIVE, OFFLINE
  last_heartbeat_at TIMESTAMP WITH TIME ZONE,
  metadata JSONB
);

CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  type TEXT NOT NULL, -- e.g. DAILY_WAREHOUSE_REPORT
  status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, RUNNING, SUCCESS, FAILED
  input JSONB,
  output JSONB,
  error TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE task_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
  event_type TEXT NOT NULL,
  payload JSONB
);
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  owner_user_id UUID REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE organization_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL, -- OWNER, ADMIN, MEMBER
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE industries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  key TEXT UNIQUE NOT NULL,   -- e.g. "logistics"
  name TEXT NOT NULL,
  description TEXT
);

CREATE TABLE role_templates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  industry_id UUID REFERENCES industries(id),
  key TEXT NOT NULL,          -- e.g. "warehouse_analyst"
  name TEXT NOT NULL,
  default_capabilities JSONB,
  default_tools JSONB,
  description TEXT
);

CREATE TABLE tools (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  key TEXT UNIQUE NOT NULL,   -- "db", "file", "cctv", "email", "browser"
  name TEXT NOT NULL,
  config_schema JSONB,        -- JSON schema for config UI
  description TEXT
);

CREATE TABLE agents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  industry_id UUID REFERENCES industries(id),
  role_template_id UUID REFERENCES role_templates(id),
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, DISABLED
  system_prompt TEXT,
  config JSONB,                          -- full agent definition
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE agent_tools (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  tool_id UUID REFERENCES tools(id),
  config JSONB          -- endpoint, db name, etc
);

CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  source_type TEXT NOT NULL, -- JD, SOP, POLICY, MANUAL, OTHER
  storage_path TEXT NOT NULL, -- local path or S3 key
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE document_chunks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
  chunk_text TEXT NOT NULL,
  embedding VECTOR(1536),     -- depends on embedding model size
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE local_agents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ENROLLED', -- ENROLLED, ACTIVE, OFFLINE
  last_heartbeat_at TIMESTAMP WITH TIME ZONE,
  metadata JSONB
);

CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  type TEXT NOT NULL, -- e.g. DAILY_WAREHOUSE_REPORT
  status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, RUNNING, SUCCESS, FAILED
  input JSONB,
  output JSONB,
  error TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE task_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
  event_type TEXT NOT NULL,
  payload JSONB
);
6. Services & API Design
6.1 Core API (apps/core-api)
Responsibilities:
Auth
Users, orgs, memberships
Industries, role templates, tools
Agents & tools configuration
Documents upload & embedding
Agent config export
Task metadata & listing
Endpoints (v1):
Auth:
POST /auth/signup – { email, password, name } → user + token
POST /auth/login – { email, password } → token
GET /me – returns user + memberships
Organizations:
POST /orgs – create org; owner = current user
GET /orgs – list orgs for current user
GET /orgs/{org_id}
Industries & role templates:
GET /industries
GET /role-templates?industry_key=logistics
Agents:
POST /orgs/{org_id}/agents
body: { industry_id, role_template_id, name, tool_ids[] }
GET /orgs/{org_id}/agents
GET /agents/{agent_id}
PATCH /agents/{agent_id} – update name, status, config fields
Tools:
GET /tools – list tool types + schema
Documents:
POST /agents/{agent_id}/documents
multipart: file, source_type
pipeline: store file → extract text → chunk → embed → save chunks
GET /agents/{agent_id}/documents
POST /agents/{agent_id}/search-docs
{ query: string, top_k: int }
Agent profile & config:
POST /agents/{agent_id}/generate-profile
Uses LLM:
Input: industry, role template, sample doc chunks
Output: system prompt, capabilities, config JSON
Save into agents.system_prompt + agents.config
GET /agents/{agent_id}/config
Returns YAML/JSON for local agent:

agent_id: "<uuid>"
org_id: "<uuid>"
name: "Warehouse Analyst"
industry: "logistics"
role: "warehouse_analyst"
llm:
  model: "gpt-4.1"  # initially
  temperature: 0.2
tools:
  - key: "db"
    required_settings:
      - "DB_DSN"
  - key: "file"
memory:
  org_namespace: "org_<id>"
  agent_namespace: "agent_<id>"
workflows:
  - type: "DAILY_WAREHOUSE_REPORT"
    schedule: "0 17 * * *"


Tasks listing:
GET /agents/{agent_id}/tasks
GET /tasks/{task_id}
6.2 Orchestrator (apps/orchestrator)
Responsibilities:
Execute agent tasks using LangGraph
Communicate with local agents for tools
Store task events & outputs
Endpoints:
Task control:
POST /agents/{agent_id}/run-task
body: { type, input }
Creates task, kicks off LangGraph workflow
Returns task_id
GET /tasks/{task_id} – status, output, events
Local agent integration:
POST /local-agents/heartbeat
body: { local_agent_id (optional), agent_id, org_id, name, capabilities, status }
Registers or updates a local agent record
POST /tool-callbacks
body: { task_id, step_id, tool_name, result, error? }
Tool-task protocol (cloud → local):
Orchestrator should push tool tasks via:
Simpler version: local agent polls GET /local-agents/{id}/pending-tasks
Response: list of tasks like:


{
  "tasks": [
    {
      "task_tool_id": "uuid",
      "task_id": "task-uuid",
      "tool": "db",
      "payload": {
        "query": "SELECT * FROM picks WHERE date = CURRENT_DATE"
      }
    }
  ]
}



Local agent responds back with POST /tool-callbacks.
7. Frontend (apps/web) – Pages & Flows
Use Next.js (App Router).
Main routes:
/login – login form
/signup – signup
/dashboard – list orgs, quick stats
/orgs/[orgId] – org overview, agents listing shortcut
/orgs/[orgId]/agents – list agents + create button
/orgs/[orgId]/agents/new – agent creation form
/agents/[agentId] – agent detail view:
General info
Tools
Documents list + upload
“Generate Profile” button
Show system prompt
“Download Config” button
“Run Test Task” button
Task history & statuses
Components:
<AuthLayout>, <DashboardLayout>
<AgentList>, <AgentForm>, <DocumentUpload>, <TaskList>
<ConfigViewer> – show YAML inline
Use React Query for all API calls.
8. Orchestrator / LangGraph Design
Basic graph for DAILY_WAREHOUSE_REPORT
Nodes:
StartNode
Input: { agent_id, org_id, task_type, params }
LoadAgentConfigNode
Fetch agent config from core-api
Output: config, system_prompt, allowed tools
FetchDataNode
Create DB tool task for local agent:
Example payload: SQL template + date range.
Wait for callback.
Output: structured WMS data (JSON).
FetchDocsNode
Call core-api search-docs:
Query: “warehouse daily performance SOP”
Output: top N doc chunks.
LLMAnalysisNode
Call LLM (via OpenAI or router) with:
System prompt
WMS data
SOP chunks
Ask it:
Summarise throughput, bottlenecks, anomalies, suggestions.
ReportFormatterNode
Format result into markdown & a short executive summary.
Output: { full_report_md, summary_text }
SaveTaskResultNode
Store output in tasks.output
Log final task_events.
All nodes run inside LangGraph and share task_id for tracing.
9. Local Agent Design (apps/local-agent)
Layout

local-agent/
  phi_agent/
    __init__.py
    main.py           # CLI entry: parse args
    config.py         # read YAML, validate with pydantic
    client.py         # HTTP client to core-api + orchestrator
    registry.py       # register/heartbeat local agent
    worker.py         # polling loop for tasks
    tools/
      base.py
      db.py
      file.py
      # later: cctv.py, email.py, browser.py
  pyproject.toml


Behaviour
Start:
phi-agent run --config ./phi-agent-config.yaml
Load config.
Register local agent:
POST /local-agents/heartbeat.
Polling loop:
Every X seconds:
GET /local-agents/{id}/pending-tasks
For each task:
Choose appropriate tool:
DBTool → execute SQL on local DB
FileTool → read CSV/Excel
Return result with POST /tool-callbacks.
Tool examples:
DBTool:
Use DSN or host/user/password from a separate local .env or interactive config.
Connect via SQLAlchemy, run query, return JSON rows.
FileTool:
Based on config, read from directory where exports live.
Parse CSV / Excel, return structured data.
Later: CCTVTool (placeholder now).
10. Infra & Environments
Dev Environment
docker-compose.yml:
db – Postgres with pgvector
core-api – bound to localhost:8000
orchestrator – localhost:8001
web – localhost:3000
.env files:
DB connection strings
OpenAI key
Run local agent outside Docker to simulate a customer environment.
Prod (later on AWS, not required immediately)
ECS for core-api, orchestrator, web
RDS for PostgreSQL
S3 for document storage
CloudFront for frontend
Secrets Manager for secrets
SQS for async tasks (later)
11. Phase-Based Execution Plan (Cursor-Ready)
This is your end-to-end roadmap. Tackle in order.



PHASE 1 – Monorepo & Auth Skeleton 
Backend (core-api):
 Set up Python project with FastAPI.
 Connect to Postgres (Docker).
 Create models/migrations for:
users
organizations
organization_members
 Implement JWT-based auth:
POST /auth/signup
POST /auth/login
GET /me
 Implement org endpoints:
POST /orgs
GET /orgs
GET /orgs/{id}
Frontend (web):
 Initialize Next.js + TS + Tailwind + shadcn/ui.
 Add API client hooks (React Query).
 Implement:
/signup + form → call /auth/signup
/login + form → call /auth/login
 Set up authenticated layout with basic top nav.
 /dashboard – list organizations.\


PHASE 2 – Industries, Roles, Agents, Tools 
Backend:
 Add tables:
industries
role_templates
tools
agents
agent_tools
 Seed examples:
Industry: logistics (“Logistics & Warehousing”)
Role templates: warehouse_analyst, ops_manager, safety_officer
Tools: db, file, cctv (stub), email
 Add endpoints:
GET /industries
GET /role-templates?industry_key=
GET /tools
POST /orgs/{org_id}/agents
GET /orgs/{org_id}/agents
GET /agents/{agent_id}
Frontend:
 /orgs/[orgId]/agents:
Fetch and display agent list.
“Create Agent” button.
 /orgs/[orgId]/agents/new:
Dropdown: industry → loads role templates.
Dropdown: role template.
Agent name.
Multi-select: tools (from GET /tools).
Submit → POST /orgs/{org_id}/agents.


PHASE 3 – Documents & Memory 
Backend:
 Add documents, document_chunks tables.
 Implement:
POST /agents/{agent_id}/documents:
Accept upload
Save file (local storage/ folder)
Extract text (use pdfplumber/pypdf for PDF, python-docx for DOCX).
Chunk text into ~500–1000 character segments.
Embed each chunk via OpenAI embeddings.
Insert into document_chunks with pgvector.
GET /agents/{agent_id}/documents.
POST /agents/{agent_id}/search-docs:
Input: { query, top_k }
Embed query
Vector search in document_chunks (cosine similarity)
Return top chunks.
Frontend:
 On /agents/[agentId]:
“Documents” section:
Upload component → POST doc.
List docs with name, type, created_at.
Optional: search box:
Calls search-docs and displays snippet.


PHASE 4 – Agent Profile & Config Export 
Backend:
 Fields:
agents.system_prompt (TEXT)
agents.config (JSONB)
 Implement POST /agents/{agent_id}/generate-profile:
Load:
Industry + role template details.
5–10 sample doc chunks (JDs, SOPs).
Call LLM with prompt like:
“You are building a virtual employee. Given this industry, role, and context, produce: system prompt, list of capabilities, example workflows, and safety constraints.”
Save response as:
system_prompt (string)
config (JSON: capabilities, workflows, tool usage rules)
 Implement GET /agents/{agent_id}/config:
Combine:
Agent meta
Tools
Workflows
Memory namespaces
Return YAML/JSON.
Frontend:
 On /agents/[agentId]:
Button “Generate Profile”.
Display generated system_prompt and config (read-only).
Button “Download Config” → calls /agents/{id}/config and downloads .yaml.
\


PHASE 5 – Orchestrator & Task Execution 
Backend (orchestrator):
 Setup FastAPI app.
 Connect to same Postgres.
 Add tasks and task_events usage.
 Implement POST /agents/{agent_id}/run-task:
Body: { type, input? }
Create a row in tasks.
Invoke LangGraph to run workflow.
 Implement GET /tasks/{task_id}.
LangGraph:
 Define a basic graph for DAILY_WAREHOUSE_REPORT task:
Node 1: Load agent config.
Node 2: Fetch relevant docs (via core-api search-docs).
Node 3: Stub-fetch WMS data (simulate).
Node 4: LLM analysis.
Node 5: Format report.
Node 6: Save output to tasks.output.
Frontend:
 On /agents/[agentId]:
Button: “Run Test Task (Daily Warehouse Report)”.
Call orchestrator endpoint.
Show task status & final report.
At this point you have a cloud-only demo (no local agent yet).


PHASE 6 – Local Agent MVP 
Local Agent app:
 Python package with CLI:
Command: phi-agent run --config path/to/config.yaml
 config.py – load and validate YAML.
 client.py – HTTP client to orchestrator/core-api.
 registry.py:
On startup: POST /local-agents/heartbeat.
 worker.py:
Loop:
GET /local-agents/{id}/pending-tasks (implement this in orchestrator).
For each tool task, call relevant local tool implementation.
POST result to /tool-callbacks.
Tools (local-agent/tools):
 DBTool:
Reads DSN or host/user/password from local .env or config.
Executes SQL from payload.
Returns JSON (list of rows).
 FileTool:
Reads local CSV or Excel from configured directory.
Returns parsed JSON.
Backend (orchestrator updates):
 Maintain local_agents table via heartbeat.
 Implement:
GET /local-agents/{id}/pending-tasks – returns tool tasks for that local agent.
Internally, store “pending tool calls” associated to tasks and local_agent_id.
 Tool nodes in LangGraph:
Instead of stub, create a “tool task”, wait for callback.
When callback arrives, continue workflow.
End-to-end:
 Run:
docker-compose (db, core-api, orchestrator, web).
Local agent with config referencing the test agent.
 Confirm:
Running “Daily Warehouse Report” uses local DB via local-agent.


PHASE 7 – Reliability, Logging, Metrics (ongoing)
 Add structured logging in all services (log JSON with org_id, agent_id, task_id).
 Add retries for:
LLM calls
Local agent communication
 Add task timeouts & failure states.
 Add basic metrics tables or integrate Prometheus later.
 Build simple admin-only page:
List tasks across orgs.
Inspect task events.


PHASE 8 – Self-Hosted LLM Router (later)
 Create llm-router-service:
Endpoints: /chat, /complete, /embed.
Implement providers:
OpenAI (default)
Local Llama/Qwen (when you have GPUs).
 Change orchestrator & core-api to call router instead of OpenAI directly.
 Add logic to route:
Lightweight tasks → local models.
Heavy/critical reasoning → best available model.
 Benchmark and tune.




 # Phi Agents – Task Backlog (From Current Status Onwards)

You already have:
- Core platform (auth, orgs, agents, docs, tasks)
- Daily Warehouse Report workflow
- PROJECT_STATUS_REPORT.md & USER_FEATURES_REPORT.md

Below are the next tasks, in order.




Phase 8 – Local Agent Runtime (Core CLI + Task Protocol)
🎯 Goal: Have a local-agent process that registers with cloud, polls for work, and can execute simple tools (no CCTV/web yet).
8.1. Local agent project setup
In apps/local-agent/:
 Create Python project with this structure:

 apps/local-agent/
  phi_agent/
    __init__.py
    main.py           # CLI entry
    config.py         # load/validate YAML config
    client.py         # HTTP client to orchestrator/core-api
    registry.py       # register + heartbeat
    worker.py         # polling loop
    tools/
      __init__.py
      base.py
      db.py           # basic DB tool (stub or simple)
      file.py         # basic file read/write
  pyproject.toml


 Add dependencies: httpx or requests, pydantic, pyyaml, sqlalchemy (for DB later).
8.2. Agent config format
Task for Cursor:
 Define a pydantic model for AgentLocalConfig in config.py that loads the YAML produced by /agents/{id}/config and extends it with local-only settings, e.g.:

 agent_id: "..."
org_id: "..."
name: "Warehouse Analyst"
server:
  base_url: "https://api.yourdomain.com"
  api_token: "..."
local:
  db:
    dsn: "postgresql://user:pass@localhost:5432/wms"
  file_roots:
    reports: "/var/phi/reports"
    exports: "/var/phi/exports"
8.3. CLI
In main.py:
 Implement phi-agent CLI using argparse or typer:

 phi-agent run --config /path/to/phi-agent-config.yaml


This should:
Load config
Call registry.register()
Start worker.run_loop()
8.4. Registration & heartbeat
Add backend endpoints in orchestrator:
 POST /local-agents/heartbeat
body: { agent_id, org_id, name, status, metadata }
response: { local_agent_id }
Cursor tasks:
 Implement local_agents table is already defined in schema; wire it up.
 In registry.py, call heartbeat on startup and periodically (e.g. every 30s) with status = ACTIVE.
Phase 9 – Local Tools: Files, DB, Processes
🎯 Goal: Local agent can actually do things on the machine: read/write files, query DB, run whitelisted commands.
9.1. Tool protocol
In orchestrator:
 Add a minimal “tool task” model (either new table or reuse task_events with a type):
tool_task_id, task_id, local_agent_id, tool_name, payload, status.
 Add endpoint: GET /local-agents/{id}/pending-tool-tasks
returns list of tool tasks for that local agent.
 Extend /tool-callbacks to accept tool results:
{ tool_task_id, task_id, result, error? }
9.2. DBTool (local)
In tools/db.py:
 Implement DBTool with:
Reads DSN from config.local.db.dsn
Supports payload: { "query": "SELECT ...", "params": {} }
Returns: rows as list of dicts
9.3. FileTool (local)
In tools/file.py:
 Implement FileTool to:
Read CSV/JSON files from allowed directories in config.local.file_roots
Write reports to reports folder
Payload example:
Read: { "action": "read_csv", "path": "exports/daily_orders.csv" }
Write: { "action": "write_text", "path": "reports/daily_report.md", "content": "..." }
9.4. Worker loop connecting it
In worker.py:
 Poll /local-agents/{id}/pending-tool-tasks
 Route each tool task to correct local tool class
 Catch errors, send back results via /tool-callbacks
Now, orchestrator tool nodes can be wired to real local execution via DB/file instead of stubbed data.
Phase 10 – Browser Automation (WebTool)
🎯 Goal: Agent can use web-based tools like a human (login to WMS portal, download exports, etc.).
10.1. Add Playwright to local-agent
Cursor:
 Add dependency: playwright (Python).
 Add init script to install browsers during setup (dev only).
10.2. WebTool implementation
In tools/web.py:
 Implement a WebTool class that exposes a few high-level operations:
login(url, username, password, selectors)
goto(url)
click(selector)
fill(selector, value)
download_report(...) (for known WMS screens)
 Allow payload like:
 {
  "action": "run_script",
  "script": "LOGIN_AND_EXPORT_DAILY_ORDERS",
  "params": {
    "date": "2025-12-04"
  }
}
 Inside WebTool maintain a registry of named scripts; each is a Python function composed of Playwright commands.
10.3. Orchestrator wiring
 Add a WebToolNode in LangGraph for relevant workflows.
 For now, support a simple scenario:
“If WMS is web-only, use WebTool to export CSV instead of DBTool”.
Phase 11 – Dashboard / App Builder (Streamlit)
🎯 Goal: Agent can create a live dashboard app automatically when needed.
11.1. Add Streamlit dependency
In local-agent:
 Add streamlit and pandas to dependencies.
11.2. Dashboard spec & generator
Create phi_agent/dashboard/generator.py:
 Define a DashboardSpec pydantic model:

 class ChartSpec(BaseModel):
    type: Literal["bar", "line", "pie", "scatter"]
    title: str
    data_source: str  # CSV path or inline data key
    x_field: str
    y_field: str

class TableSpec(BaseModel):
    title: str
    data_source: str

class DashboardSpec(BaseModel):
    title: str
    description: Optional[str]
    charts: list[ChartSpec]
    tables: list[TableSpec]


 Implement a function: generate_streamlit_app(spec: DashboardSpec, output_path: Path) that writes a dashboard.py file using the spec and Streamlit components.
11.3. DashboardTool
In tools/dashboard.py:
 Implement DashboardTool that:
Accepts payload: { "spec": { ... DashboardSpec JSON ... } }
Calls generate_streamlit_app
Launches it: e.g. subprocess.Popen(["streamlit", "run", "dashboard.py", "--server.port", "8501"])
Returns the URL: http://localhost:8501
11.4. Orchestrator integration
 Add node that:
Summarises data + insights into a DashboardSpec using LLM (LLM produces JSON)
Sends to local agent via DashboardTool
Stores returned URL in tasks.output
Makes UI show “Open dashboard” link in frontend task result.
Phase 12 – Communication Engine (Email, Slack)
🎯 Goal: Agent can talk to colleagues like a real coworker via email / chat.
12.1. EmailTool in core-api or orchestrator
Backend:
 Add config for SMTP or Microsoft Graph.
 Implement EmailTool server-side:
Input: { to: [...], subject, html_body }
Sends email using configured provider.
12.2. Slack/Teams (basic webhook)
 Implement simple SlackTool using Incoming Webhooks:
Input: { channel_name, text }
Post message.
12.3. Agent config
 Extend agents.config to include:
 "communication": {
  "can_email": true,
  "default_recipients": ["ops_manager@company.com"],
  "can_slack": true,
  "slack_channel": "#warehouse-ops"
}


12.4. Orchestrator nodes
 Add nodes in workflows to:
Send summary email after task success.
Post Slack alert when severe safety issue found.
Phase 13 – Human-like Task Engine (Progress + ETA)
🎯 Goal: Every long task has progress % + ETA + narrative updates.
13.1. DB changes
 Extend tasks table:
progress INTEGER DEFAULT 0
eta_seconds INTEGER NULL
current_step TEXT NULL
13.2. Orchestrator helpers
 Implement a helper in orchestrator:

 def update_task_status(task_id, *, progress: int, eta_seconds: int | None, current_step: str | None):
    # Update DB and emit a task_event


“Implement Phase 8 local-agent CLI as described in PLAN, starting with apps/local-agent/phi_agent/main.py and config.py.”
“Add DBTool and FileTool as in Phase 9.”
“Add WebTool based on Playwright as in Phase 10.”
“Implement DashboardTool with Streamlit (Phase 11).”
“Extend tasks table for progress/eta (Phase 13) and update frontend.”


Landing Page Goal
The landing page must do 3 things:
1. Explain the product clearly:
“A virtual employee that behaves exactly like a human worker.”
2. Build trust:
AI agents usually sound like chatbots. Yours is different. Your page must show this is enterprise-grade.
3. Drive the visitor to act:
Book demo
Sign up
Watch showcase videos
Install local agent
⚡ 2. Landing Page Structure (Complete Blueprint)
Below is the recommended full structure:
A. HERO SECTION
Headline:
Meet Your First Virtual Employee.
An AI-powered worker that performs tasks exactly like a human.
Subheadline:
Phi Agents connect to your systems, understand your workflows, audit your warehouse, generate dashboards, analyse CCTV, send emails, build apps, and communicate like a real colleague — 24/7.
CTA Buttons:
Book a Demo
Try Phi Agent (Free)
Visual:
A looping animation showing:
A human silhouette dissolving into a digital, glowing AI humanoid.
Screens showing CCTV analysis, dashboards, emails being sent, etc.
Or a 3D rotating “Virtual Worker Cube” with feature icons.
B. HOW IT WORKS (High-Level Overview)
3 simple steps:
1. Create your Virtual Employee
Pick a role — Warehouse Analyst, Safety Officer, Ops Manager, HR Assistant, etc.
2. Connect your tools
Give it access to WMS, ERP, CCTV, files, databases, email, browser.
3. It starts working like a real teammate
Your agent performs tasks, communicates, builds dashboards, and sends updates with ETA — exactly like a human.
Visual:
A 3-step horizontal infographic.
C. THE DIFFERENCE: NOT A CHATBOT. A REAL WORKER.
What makes Phi Agents unique?
Feature bullets:
Uses your systems like an employee
Logs into web apps, downloads reports, fills forms, sends emails, reads dashboards.
Sees your warehouse
Analyses CCTV, detects defects, monitors worker safety.
Builds dashboards & apps automatically
If your company doesn't have reporting tools, your agent generates them instantly.
Human-like communication
Talks via text and voice, sends updates, asks clarifying questions.
Runs locally & respects data boundaries
Your data never leaves your environment. Agent executes tasks on-prem.
Visual:
Split-screen of chatbot vs human-like virtual assistant.
D. FEATURE GRID — Show Depth, Show Power
1. Autonomous Workflows
Daily warehouse reports
Safety audits
Inventory accuracy checks
Pick route optimization
Bottleneck detection
Labour productivity analysis
2. Computer Vision Engine
CCTV anomaly detection
Safety violation monitoring
Pallet/box defect recognition
Worker PPE detection
3. Multi-Tool Access
DB queries
File reading & writing
Browser automation
Email sending
Slack/Teams messaging
4. Dashboard Builder
Automatic Streamlit dashboards
Real-time charts & KPIs
Inventory heatmaps
Operational control rooms
5. Communication Interface
Human-like text responses
Voice assistant mode
Status updates + ETA
6. Local Execution Engine
Works on customer's machines
Full privacy & security
Customizable permissions
Layout:
6 cards with icons.
E. USE CASES
Split into 4 vertical cards:
Warehouse & Logistics
Daily operations reporting
CCTV safety compliance
Stock level prediction
Worker productivity scoring
Manufacturing
Defect detection
Line performance analytics
Retail
Inventory auditing
Theft/safety monitoring
Corporate Roles
HR assistant
Data analyst
Finance operations
Compliance reviewer
F. LIVE DEMO SECTION
Interactive Demo Ideas:
Playback of CCTV detection:
Show bounding boxes detecting unsafe forklift behaviour.
Auto-generated dashboard:
Click → “Generate Warehouse Audit” → interactive charts appear.
Human-like communication example:
Chat widget showing:
“I’m running your inventory audit now, ETA 2 min 14 seconds.”
Workflow timeline:
A visual of the agent updating progress like a human.
G. PRICING SECTION
Starter (Free)
1 virtual employee
1 workflow
No CCTV
Pro (£99 / month per agent)
Up to 5 workflows
Local agent runtime
Dashboard builder
Slack/Email integration
Enterprise (Custom)
Unlimited agents
Full CCTV integration
On-prem GPU
Advanced workflows
Priority SLAs
CTA: Contact Sales
H. SECURITY & TRUST
Key messages:
All execution happens locally
Agents run on your machines — not in the cloud.
Fine-grained permission control
Admins choose which tools the agent can access.
Audit logs
Every action is traceable.
Compatible with SOC2, ISO27001
(Even if not certified yet — you are “compatible / alignment-ready”)
I. SOCIAL PROOF / TRUST INDICATORS
If you don’t have actual clients yet, use capability claims, not logos:
“Designed for modern warehouses”
“Supports CCTV, WMS, ERP, BI systems”
“Battle-tested workflows”
Later: add logos & testimonials.
J. FINAL CTA SECTION
Headline:
Hire your first Virtual Employee today.
Subheadline:
Start automating real work in minutes — reports, dashboards, analysis, audits, everything.
Buttons:
Get Started (Free)
Book a Demo
Visual:
A digital worker avatar standing beside a human employee.
⚙️ 3. Technical Layout (Next.js Implementation Blueprint)


pages/
  index.tsx        -> Landing page
  demo.tsx         -> Interactive demo
  pricing.tsx
  security.tsx
  contact.tsx
components/
  HeroSection.tsx
  HowItWorks.tsx
  FeatureGrid.tsx
  UseCases.tsx
  DemoSection.tsx
  PricingCard.tsx
  FinalCTA.tsx
  Footer.tsx
public/
  images/ (hero visuals, icons)
Use:
shadcn/ui
Framer Motion for animations
Next/Image for hero visuals
🎨 4. Visual Branding Suggestions
Colors:
Deep Navy (#0A1A2F)
Electric Blue (#2D8CFF)
Neon Cyan (#5FFBF1)
Steel Grey (#B5C4D4)
Style:
Futuristic
Clean
Minimal lighting effects
Slight 3D elements
Hero Animation:
A digital human silhouette
A 3D warehouse overlay
Real-time data streaming around it
📣 5. Copywriting Tone
Use the tone of:
Apple (“magical but grounded”)
OpenAI (“capable + serious”)
NVIDIA (“powerful + futuristic”)
Simple, crisp, credible.
🚀 6. Marketing Angle (Your Positioning)
Your Unique Position:
"The world’s first realistic AI employee that performs the full job, not just chat."
Main Message:
“AI Agents are the past.
Virtual Employees are the future.”
Sub Message:
“Instead of automating tiny tasks, Phi Agents automate entire jobs.”