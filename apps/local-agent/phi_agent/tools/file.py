import os
from pathlib import Path
from typing import Any, Dict
import pandas as pd
from phi_agent.tools.base import BaseTool
from phi_agent.config import Settings

settings = Settings()


class FileTool(BaseTool):
    """File tool for reading CSV and Excel files"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_path = config.get("base_path") or settings.file_base_path or "."
    
    async def execute(self, payload: Dict[str, Any]) -> Any:
        """Read file and return parsed data"""
        file_path = payload.get("file_path")
        if not file_path:
            raise ValueError("file_path is required in payload")
        
        # Resolve full path
        if not os.path.isabs(file_path):
            full_path = Path(self.base_path) / file_path
        else:
            full_path = Path(file_path)
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        
        # Read based on extension
        ext = full_path.suffix.lower()
        
        if ext == ".csv":
            df = pd.read_csv(full_path)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(full_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        # Convert to list of dicts
        return df.to_dict("records")
    
    @property
    def name(self) -> str:
        return "file"


