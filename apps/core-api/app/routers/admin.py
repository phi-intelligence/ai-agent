from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models import Task, TaskEvent, User, OrganizationMember
from app.schemas import TaskEventResponse
from app.auth import get_current_user
from phi_utils.logging import setup_logging, ContextLogger

# Import TaskResponse from orchestrator schemas or create here
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class TaskResponse(BaseModel):
    id: UUID
    agent_id: UUID
    org_id: UUID
    type: str
    status: str
    input: Optional[Dict[str, Any]]
    output: Optional[Dict[str, Any]]
    error: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

logger = setup_logging("core-api.admin")
router = APIRouter(prefix="/admin", tags=["admin"])


def check_admin_access(current_user: User, db: Session):
    """Check if user has admin access (owner of any org)"""
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.user_id == current_user.id,
        OrganizationMember.role.in_(["OWNER", "ADMIN"])
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return membership


@router.get("/tasks", response_model=list[TaskResponse])
async def list_all_tasks(
    org_id: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List tasks across organizations (admin only)"""
    check_admin_access(current_user, db)
    
    ctx_logger = ContextLogger(logger, user_id=str(current_user.id))
    ctx_logger.info("Admin task listing requested")
    
    query = db.query(Task)
    
    if org_id:
        try:
            org_uuid = UUID(org_id)
            query = query.filter(Task.org_id == org_uuid)
            ctx_logger = ctx_logger.with_context(org_id=org_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid org_id"
            )
    
    if agent_id:
        try:
            agent_uuid = UUID(agent_id)
            query = query.filter(Task.agent_id == agent_uuid)
            ctx_logger = ctx_logger.with_context(agent_id=agent_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid agent_id"
            )
    
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    tasks = query.order_by(Task.created_at.desc()).limit(limit).all()
    
    ctx_logger.info(f"Returning {len(tasks)} tasks")
    return tasks


@router.get("/tasks/{task_id}/events", response_model=list[TaskEventResponse])
async def get_task_events(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all events for a task (admin only)"""
    check_admin_access(current_user, db)
    
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID"
        )
    
    ctx_logger = ContextLogger(
        logger,
        user_id=str(current_user.id),
        task_id=task_id
    )
    
    task = db.query(Task).filter(Task.id == task_uuid).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    events = db.query(TaskEvent).filter(
        TaskEvent.task_id == task_uuid
    ).order_by(TaskEvent.timestamp).all()
    
    ctx_logger.info(f"Returning {len(events)} events for task")
    
    return [
        TaskEventResponse(
            id=e.id,
            task_id=e.task_id,
            timestamp=e.timestamp,
            event_type=e.event_type,
            payload=e.payload
        )
        for e in events
    ]

