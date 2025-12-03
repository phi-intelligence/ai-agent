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


class AgentConfig(BaseModel):
    agent_id: str
    org_id: str
    name: str
    industry: Optional[str] = None
    role: Optional[str] = None
    llm: LLMConfig
    tools: List[ToolConfig] = Field(default_factory=list)
    memory: MemoryConfig
    workflows: List[WorkflowConfig] = Field(default_factory=list)


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
    
    return AgentConfig(**data)


