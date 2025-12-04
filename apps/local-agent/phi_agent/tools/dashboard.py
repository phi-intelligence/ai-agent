"""
DashboardTool for generating and launching Streamlit dashboards
"""
import subprocess
import asyncio
from pathlib import Path
from typing import Any, Dict
from phi_agent.tools.base import BaseTool
from phi_agent.dashboard.generator import generate_streamlit_app, DashboardSpec


class DashboardTool(BaseTool):
    """Tool for generating and launching Streamlit dashboards"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_path = config.get("base_path", "/tmp/phi_dashboards")
        self.port = config.get("port", 8501)
        self.running_dashboards: Dict[str, subprocess.Popen] = {}
    
    async def execute(self, payload: Dict[str, Any]) -> Any:
        """Generate and launch a Streamlit dashboard"""
        spec_data = payload.get("spec")
        if not spec_data:
            raise ValueError("spec is required in payload")
        
        # Parse dashboard spec
        spec = DashboardSpec(**spec_data)
        
        # Generate dashboard file
        dashboard_name = spec.title.lower().replace(" ", "_")
        dashboard_path = Path(self.base_path) / f"{dashboard_name}.py"
        
        generated_path = generate_streamlit_app(spec, dashboard_path)
        
        # Launch Streamlit
        port = payload.get("port", self.port)
        process = subprocess.Popen(
            [
                "streamlit", "run", generated_path,
                "--server.port", str(port),
                "--server.headless", "true",
                "--server.enableCORS", "false",
                "--server.enableXsrfProtection", "false"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Store process
        dashboard_id = f"{dashboard_name}_{port}"
        self.running_dashboards[dashboard_id] = process
        
        # Wait a moment for server to start
        await asyncio.sleep(2)
        
        url = f"http://localhost:{port}"
        
        return {
            "status": "success",
            "url": url,
            "dashboard_id": dashboard_id,
            "path": generated_path
        }
    
    @property
    def name(self) -> str:
        return "dashboard"

