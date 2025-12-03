from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr


# Auth schemas
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class MembershipResponse(BaseModel):
    id: UUID
    org_id: UUID
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithMemberships(UserResponse):
    memberships: list[MembershipResponse]


# Organization schemas
class OrganizationCreate(BaseModel):
    name: str


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    owner_user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Industry schemas
class IndustryResponse(BaseModel):
    id: UUID
    key: str
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


# Role Template schemas
class RoleTemplateResponse(BaseModel):
    id: UUID
    industry_id: UUID
    key: str
    name: str
    default_capabilities: Optional[Dict[str, Any]]
    default_tools: Optional[Dict[str, Any]]
    description: Optional[str]

    class Config:
        from_attributes = True


# Tool schemas
class ToolResponse(BaseModel):
    id: UUID
    key: str
    name: str
    config_schema: Optional[Dict[str, Any]]
    description: Optional[str]

    class Config:
        from_attributes = True


# Agent schemas
class AgentToolCreate(BaseModel):
    tool_id: UUID
    config: Optional[Dict[str, Any]] = None


class AgentCreate(BaseModel):
    industry_id: UUID
    role_template_id: UUID
    name: str
    tool_ids: List[UUID] = []


class AgentToolResponse(BaseModel):
    id: UUID
    tool_id: UUID
    config: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class AgentResponse(BaseModel):
    id: UUID
    org_id: UUID
    industry_id: Optional[UUID]
    role_template_id: Optional[UUID]
    name: str
    status: str
    system_prompt: Optional[str]
    config: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class AgentDetailResponse(AgentResponse):
    agent_tools: List[AgentToolResponse] = []


# Document schemas
class DocumentResponse(BaseModel):
    id: UUID
    org_id: UUID
    agent_id: Optional[UUID]
    name: str
    source_type: str
    storage_path: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    chunk_text: str
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class DocumentSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


class DocumentSearchResponse(BaseModel):
    query: str
    chunks: List[DocumentChunkResponse]


# Task schemas (for admin endpoints)
class TaskEventResponse(BaseModel):
    id: UUID
    task_id: UUID
    timestamp: datetime
    event_type: str
    payload: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True
