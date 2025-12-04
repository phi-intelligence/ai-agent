import asyncio
from typing import Dict, Any
from phi_agent.config import AgentConfig
from phi_agent.client import OrchestratorClient
from phi_agent.tools import DBTool, FileTool, WebTool, DashboardTool


class Worker:
    """Worker that polls for tasks and executes tools"""
    
    def __init__(self, config: AgentConfig, client: OrchestratorClient, local_agent_id: str):
        self.config = config
        self.client = client
        self.local_agent_id = local_agent_id
        self.tools: Dict[str, Any] = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize tool instances based on config"""
        for tool_config in self.config.tools:
            tool_key = tool_config.key
            tool_config_dict = {}
            
            # Get tool-specific config from local config
            if tool_key == "db" and self.config.local and self.config.local.db:
                db_config = self.config.local.db
                if db_config.dsn:
                    tool_config_dict["dsn"] = db_config.dsn
                else:
                    tool_config_dict["host"] = db_config.host
                    tool_config_dict["port"] = db_config.port
                    tool_config_dict["database"] = db_config.database
                    tool_config_dict["username"] = db_config.username
                    tool_config_dict["password"] = db_config.password
                self.tools["db"] = DBTool(tool_config_dict)
            elif tool_key == "file" and self.config.local and self.config.local.file_roots:
                file_config = self.config.local.file_roots
                tool_config_dict["base_path"] = file_config.base_path or file_config.exports or "."
                self.tools["file"] = FileTool(tool_config_dict)
            elif tool_key == "web":
                # WebTool doesn't need special config
                self.tools["web"] = WebTool({})
            elif tool_key == "dashboard":
                # DashboardTool config
                dashboard_config = {}
                if self.config.local and self.config.local.file_roots:
                    dashboard_config["base_path"] = self.config.local.file_roots.reports or "/tmp/phi_dashboards"
                self.tools["dashboard"] = DashboardTool(dashboard_config)
            elif tool_key == "db":
                # Fallback to environment variables
                self.tools["db"] = DBTool({})
            elif tool_key == "file":
                # Fallback to environment variables
                self.tools["file"] = FileTool({})
            elif tool_key == "web":
                self.tools["web"] = WebTool({})
            elif tool_key == "dashboard":
                self.tools["dashboard"] = DashboardTool({})
            # Add more tools as needed
    
    async def process_task(self, task: Dict[str, Any]):
        """Process a single tool task"""
        tool_name = task.get("tool")
        task_tool_id = task.get("task_tool_id")
        task_id = task.get("task_id")
        payload = task.get("payload", {})
        
        if tool_name not in self.tools:
            # Send error callback
            await self.client.send_tool_callback(
                task_id=task_id,
                step_id=task_tool_id,
                tool_name=tool_name,
                result=None,
                error=f"Tool {tool_name} not available"
            )
            return
        
        try:
            # Execute tool
            tool = self.tools[tool_name]
            result = await tool.execute(payload)
            
            # Send success callback
            await self.client.send_tool_callback(
                task_id=task_id,
                step_id=task_tool_id,
                tool_name=tool_name,
                result=result,
                error=None
            )
        except Exception as e:
            # Send error callback
            await self.client.send_tool_callback(
                task_id=task_id,
                step_id=task_tool_id,
                tool_name=tool_name,
                result=None,
                error=str(e)
            )
    
    async def run(self, poll_interval: int = 5):
        """Main worker loop"""
        while True:
            try:
                # Get pending tasks
                response = await self.client.get_pending_tasks(self.local_agent_id)
                tasks = response.get("tasks", [])
                
                # Process each task
                for task in tasks:
                    await self.process_task(task)
                
                # Wait before next poll
                await asyncio.sleep(poll_interval)
            except Exception as e:
                print(f"Error in worker loop: {e}")
                await asyncio.sleep(poll_interval)


