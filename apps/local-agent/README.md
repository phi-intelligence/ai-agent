# Local Agent

Python CLI application that runs on customer infrastructure and executes tools locally.

## Installation

```bash
cd apps/local-agent
poetry install
```

## Usage

1. Download agent config from web UI (YAML file)

2. Create `.env` file with tool settings:
   ```bash
   DB_DSN=postgresql://user:password@localhost:5432/warehouse_db
   FILE_BASE_PATH=/path/to/data/files
   ```

3. Run the agent:
   ```bash
   phi-agent run --config ./phi-agent-config.yaml
   ```

## Configuration

The agent config YAML should include:
- `agent_id` - Agent UUID
- `org_id` - Organization UUID
- `tools` - List of tools to enable
- `memory` - Memory namespaces

## Tools

### Database Tool
Executes SQL queries on local database. Configure via:
- `DB_DSN` environment variable, or
- Individual `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

### File Tool
Reads CSV/Excel files from local filesystem. Configure via:
- `FILE_BASE_PATH` environment variable

## Communication

The local agent:
1. Registers with orchestrator on startup
2. Sends heartbeat every 30 seconds
3. Polls for pending tool tasks every 5 seconds
4. Executes tools and sends results back


