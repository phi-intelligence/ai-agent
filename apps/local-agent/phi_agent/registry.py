from typing import Optional, Dict, Any
from phi_agent.config import AgentConfig
from phi_agent.client import OrchestratorClient


class LocalAgentRegistry:
    """Handles local agent registration and heartbeat"""
    
    def __init__(self, config: AgentConfig, client: OrchestratorClient):
        self.config = config
        self.client = client
        self.local_agent_id: Optional[str] = None
    
    async def register(self) -> str:
        """Register local agent and return local_agent_id"""
        capabilities = {
            "tools": [tool.key for tool in self.config.tools]
        }
        
        result = await self.client.heartbeat(
            local_agent_id=self.local_agent_id,
            agent_id=self.config.agent_id,
            org_id=self.config.org_id,
            name=self.config.name,
            capabilities=capabilities,
            status="ACTIVE"
        )
        
        self.local_agent_id = result.get("id")
        return self.local_agent_id
    
    async def heartbeat(self):
        """Send heartbeat to keep registration alive"""
        if not self.local_agent_id:
            await self.register()
            return
        
        capabilities = {
            "tools": [tool.key for tool in self.config.tools]
        }
        
        await self.client.heartbeat(
            local_agent_id=self.local_agent_id,
            agent_id=self.config.agent_id,
            org_id=self.config.org_id,
            name=self.config.name,
            capabilities=capabilities,
            status="ACTIVE"
        )


