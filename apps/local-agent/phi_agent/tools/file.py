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
        """Execute file operation (read or write)"""
        action = payload.get("action", "read_csv")
        file_path = payload.get("path") or payload.get("file_path")
        
        if not file_path:
            raise ValueError("path or file_path is required in payload")
        
        # Resolve full path
        if not os.path.isabs(file_path):
            full_path = Path(self.base_path) / file_path
        else:
            full_path = Path(file_path)
        
        if action.startswith("read"):
            # Read operation
            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {full_path}")
            
            # Read based on extension
            ext = full_path.suffix.lower()
            
            if ext == ".csv" or action == "read_csv":
                df = pd.read_csv(full_path)
            elif ext in [".xlsx", ".xls"] or action == "read_excel":
                df = pd.read_excel(full_path)
            elif ext == ".json" or action == "read_json":
                import json
                with open(full_path, "r") as f:
                    return json.load(f)
            else:
                raise ValueError(f"Unsupported file type: {ext}")
            
            # Convert to list of dicts
            return df.to_dict("records")
        
        elif action.startswith("write"):
            # Write operation
            # Ensure directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = payload.get("content")
            if content is None:
                raise ValueError("content is required for write operations")
            
            if action == "write_text":
                with open(full_path, "w") as f:
                    f.write(content)
                return {"status": "success", "path": str(full_path)}
            elif action == "write_json":
                import json
                with open(full_path, "w") as f:
                    json.dump(content, f, indent=2)
                return {"status": "success", "path": str(full_path)}
            else:
                raise ValueError(f"Unsupported write action: {action}")
        
        else:
            raise ValueError(f"Unsupported action: {action}")
    
    @property
    def name(self) -> str:
        return "file"


