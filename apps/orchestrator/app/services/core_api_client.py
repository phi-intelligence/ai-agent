import httpx
from app.config import settings


class CoreAPIClient:
    def __init__(self):
        self.base_url = settings.core_api_url
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def get_agent(self, agent_id: str, token: str):
        """Get agent details from core API"""
        response = await self.client.get(
            f"/agents/{agent_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()

    async def search_documents(self, agent_id: str, query: str, top_k: int = 5, token: str = None):
        """Search documents for an agent"""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        response = await self.client.post(
            f"/agents/{agent_id}/documents/search-docs",
            json={"query": query, "top_k": top_k},
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()


core_api_client = CoreAPIClient()


