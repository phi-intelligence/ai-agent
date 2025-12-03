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