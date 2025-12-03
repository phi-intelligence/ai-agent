import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, TIMESTAMP, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), nullable=False)
    org_id = Column(UUID(as_uuid=True), nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="PENDING")
    input = Column(JSONB)
    output = Column(JSONB)
    error = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    events = relationship("TaskEvent", back_populates="task", cascade="all, delete-orphan")
    tool_tasks = relationship("ToolTask", back_populates="task", cascade="all, delete-orphan")


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
    agent_id = Column(UUID(as_uuid=True), nullable=False)
    org_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="ENROLLED")
    last_heartbeat_at = Column(TIMESTAMP(timezone=True))
    metadata = Column(JSONB)


class ToolTask(Base):
    """Pending tool tasks for local agents"""
    __tablename__ = "tool_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    local_agent_id = Column(UUID(as_uuid=True), nullable=False)
    step_id = Column(String, nullable=False)  # Identifier for workflow step
    tool_name = Column(String, nullable=False)
    payload = Column(JSONB, nullable=False)
    status = Column(String, nullable=False, default="PENDING")  # PENDING, COMPLETED, FAILED
    result = Column(JSONB)
    error = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    completed_at = Column(TIMESTAMP(timezone=True))

    # Relationships
    task = relationship("Task", back_populates="tool_tasks")


class TaskMetrics(Base):
    """Basic metrics table for task performance tracking"""
    __tablename__ = "task_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), nullable=False)
    org_id = Column(UUID(as_uuid=True), nullable=False)
    agent_id = Column(UUID(as_uuid=True), nullable=False)
    task_type = Column(String, nullable=False)
    duration_seconds = Column(Float)
    llm_calls = Column(Integer, default=0)
    llm_tokens_used = Column(Integer, default=0)
    tool_calls = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
