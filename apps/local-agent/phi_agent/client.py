import httpx
from typing import Optional, Dict, Any
from phi_agent.config import Settings

settings = Settings()


class OrchestratorClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.orchestrator_url
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def heartbeat(
        self,
        local_agent_id: Optional[str],
        agent_id: str,
        org_id: str,
        name: str,
        capabilities: Dict[str, Any],
        status: str = "ACTIVE"
    ) -> Dict[str, Any]:
        """Register or update local agent heartbeat"""
        response = await self.client.post(
            "/local-agents/heartbeat",
            json={
                "local_agent_id": local_agent_id,
                "agent_id": agent_id,
                "org_id": org_id,
                "name": name,
                "capabilities": capabilities,
                "status": status
            }
        )
        response.raise_for_status()
        return response.json()

    async def get_pending_tasks(self, local_agent_id: str) -> Dict[str, Any]:
        """Get pending tool tasks for this local agent"""
        response = await self.client.get(
            f"/local-agents/{local_agent_id}/pending-tasks"
        )
        response.raise_for_status()
        return response.json()

    async def send_tool_callback(
        self,
        task_id: str,
        step_id: str,
        tool_name: str,
        result: Any,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send tool execution result back to orchestrator"""
        response = await self.client.post(
            "/tool-callbacks",
            json={
                "task_id": task_id,
                "step_id": step_id,
                "tool_name": tool_name,
                "result": result,
                "error": error
            }
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()


class CoreAPIClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.core_api_url
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def close(self):
        await self.client.aclose()


