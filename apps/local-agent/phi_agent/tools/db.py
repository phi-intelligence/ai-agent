import os
from typing import Any, Dict
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from phi_agent.tools.base import BaseTool
from phi_agent.config import Settings

settings = Settings()


class DBTool(BaseTool):
    """Database tool for executing SQL queries"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.engine: Engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize database connection"""
        # Get DSN from config or environment
        dsn = self.config.get("dsn") or settings.db_dsn
        if not dsn:
            # Try to build from individual components
            host = self.config.get("host") or os.getenv("DB_HOST", "localhost")
            port = self.config.get("port") or os.getenv("DB_PORT", "5432")
            database = self.config.get("database") or os.getenv("DB_NAME", "postgres")
            username = self.config.get("username") or os.getenv("DB_USER", "postgres")
            password = self.config.get("password") or os.getenv("DB_PASSWORD", "postgres")
            dsn = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        
        self.engine = create_engine(dsn)
    
    async def execute(self, payload: Dict[str, Any]) -> Any:
        """Execute SQL query and return results"""
        query = payload.get("query")
        if not query:
            raise ValueError("Query is required in payload")
        
        # Execute query
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            
            # Convert to list of dicts
            columns = result.keys()
            rows = []
            for row in result:
                rows.append(dict(zip(columns, row)))
        
        return rows
    
    @property
    def name(self) -> str:
        return "db"


