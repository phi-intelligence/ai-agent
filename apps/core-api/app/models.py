import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, TIMESTAMP, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    name = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    owned_orgs = relationship("Organization", back_populates="owner", foreign_keys="Organization.owner_user_id")
    memberships = relationship("OrganizationMember", back_populates="user")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="owned_orgs", foreign_keys=[owner_user_id])
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # OWNER, ADMIN, MEMBER
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="memberships")


class Industry(Base):
    __tablename__ = "industries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, unique=True, nullable=False, index=True)
    name = Column(Text, nullable=False)
    description = Column(Text)

    # Relationships
    role_templates = relationship("RoleTemplate", back_populates="industry", cascade="all, delete-orphan")


class RoleTemplate(Base):
    __tablename__ = "role_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id"), nullable=False)
    key = Column(String, nullable=False)
    name = Column(Text, nullable=False)
    default_capabilities = Column(JSONB)
    default_tools = Column(JSONB)
    description = Column(Text)

    # Relationships
    industry = relationship("Industry", back_populates="role_templates")
    agents = relationship("Agent", back_populates="role_template")


class Tool(Base):
    __tablename__ = "tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, unique=True, nullable=False, index=True)
    name = Column(Text, nullable=False)
    config_schema = Column(JSONB)
    description = Column(Text)

    # Relationships
    agent_tools = relationship("AgentTool", back_populates="tool")


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id"), nullable=True)
    role_template_id = Column(UUID(as_uuid=True), ForeignKey("role_templates.id"), nullable=True)
    name = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="ACTIVE")  # ACTIVE, DISABLED
    system_prompt = Column(Text)
    config = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    industry = relationship("Industry")
    role_template = relationship("RoleTemplate", back_populates="agents")
    agent_tools = relationship("AgentTool", back_populates="agent", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="agent", cascade="all, delete-orphan")


class AgentTool(Base):
    __tablename__ = "agent_tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("tools.id"), nullable=False)
    config = Column(JSONB)

    # Relationships
    agent = relationship("Agent", back_populates="agent_tools")
    tool = relationship("Tool", back_populates="agent_tools")


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    name = Column(Text, nullable=False)
    source_type = Column(String, nullable=False)  # JD, SOP, POLICY, MANUAL, OTHER
    storage_path = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    agent = relationship("Agent")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI text-embedding-ada-002 dimension
    metadata_json = Column("metadata", JSONB)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="chunks")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)  # e.g. DAILY_WAREHOUSE_REPORT
    status = Column(String, nullable=False, default="PENDING")  # PENDING, RUNNING, SUCCESS, FAILED
    input = Column(JSONB)
    output = Column(JSONB)
    error = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    events = relationship("TaskEvent", back_populates="task", cascade="all, delete-orphan")


class TaskEvent(Base):
    __tablename__ = "task_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    event_type = Column(String, nullable=False)
    payload = Column(JSONB)

    # Relationships
    task = relationship("Task", back_populates="events")


class LocalAgent(Base):
    __tablename__ = "local_agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="ENROLLED")  # ENROLLED, ACTIVE, OFFLINE
    last_heartbeat_at = Column(TIMESTAMP(timezone=True))
    metadata_json = Column("metadata", JSONB)

    # Relationships
    agent = relationship("Agent")
    organization = relationship("Organization")


class TaskMetrics(Base):
    """Basic metrics table for task performance tracking"""
    __tablename__ = "task_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    task_type = Column(String, nullable=False)
    duration_seconds = Column(Float)
    llm_calls = Column(Integer, default=0)
    llm_tokens_used = Column(Integer, default=0)
    tool_calls = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    task = relationship("Task")
    agent = relationship("Agent")
    organization = relationship("Organization")
