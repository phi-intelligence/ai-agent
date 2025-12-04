from pathlib import Path
from typing import Optional, List, Dict, Any
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class LLMConfig(BaseModel):
    model: str = "gpt-4"
    temperature: float = 0.2


class ToolConfig(BaseModel):
    key: str
    required_settings: List[str] = Field(default_factory=list)


class MemoryConfig(BaseModel):
    org_namespace: str
    agent_namespace: str


class WorkflowConfig(BaseModel):
    type: str
    name: Optional[str] = None
    description: Optional[str] = None
    schedule: Optional[str] = None


class ServerConfig(BaseModel):
    """Server connection settings"""
    base_url: str = "http://localhost:8001"
    api_token: Optional[str] = None


class LocalDBConfig(BaseModel):
    """Local database configuration"""
    dsn: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class LocalFileConfig(BaseModel):
    """Local file system configuration"""
    reports: Optional[str] = None
    exports: Optional[str] = None
    base_path: Optional[str] = None


class LocalConfig(BaseModel):
    """Local agent configuration"""
    db: Optional[LocalDBConfig] = None
    file_roots: Optional[LocalFileConfig] = None


class AgentConfig(BaseModel):
    """Complete agent configuration"""
    agent_id: str
    org_id: str
    name: str
    industry: Optional[str] = None
    role: Optional[str] = None
    llm: LLMConfig
    tools: List[ToolConfig] = Field(default_factory=list)
    memory: MemoryConfig
    workflows: List[WorkflowConfig] = Field(default_factory=list)
    server: Optional[ServerConfig] = None
    local: Optional[LocalConfig] = None


class Settings(BaseSettings):
    orchestrator_url: str = "http://localhost:8001"
    core_api_url: str = "http://localhost:8000"
    db_dsn: Optional[str] = None
    file_base_path: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


def load_config(config_path: str) -> AgentConfig:
    """Load and validate agent config from YAML file"""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    
    # Set defaults for server if not provided
    if "server" not in data:
        data["server"] = {
            "base_url": settings.orchestrator_url
        }
    elif "base_url" not in data["server"]:
        data["server"]["base_url"] = settings.orchestrator_url
    
    return AgentConfig(**data)


