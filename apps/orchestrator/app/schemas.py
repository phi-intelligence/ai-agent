from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class TaskCreate(BaseModel):
    type: str
    input: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    id: UUID
    agent_id: UUID
    org_id: UUID
    type: str
    status: str
    input: Optional[Dict[str, Any]]
    output: Optional[Dict[str, Any]]
    error: Optional[str]
    progress: Optional[int] = 0
    eta_seconds: Optional[int] = None
    current_step: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskEventResponse(BaseModel):
    id: UUID
    task_id: UUID
    timestamp: datetime
    event_type: str
    payload: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class TaskDetailResponse(TaskResponse):
    events: list[TaskEventResponse] = []


class HeartbeatRequest(BaseModel):
    local_agent_id: Optional[str] = None
    agent_id: str
    org_id: str
    name: str
    capabilities: Dict[str, Any]
    status: str = "ACTIVE"


class HeartbeatResponse(BaseModel):
    id: str
    status: str


class ToolCallbackRequest(BaseModel):
    task_id: str
    step_id: str
    tool_name: str
    result: Optional[Any] = None
    error: Optional[str] = None


class PendingTaskResponse(BaseModel):
    task_tool_id: str
    task_id: str
    tool: str
    payload: Dict[str, Any]


class PendingTasksResponse(BaseModel):
    tasks: list[PendingTaskResponse] = []
