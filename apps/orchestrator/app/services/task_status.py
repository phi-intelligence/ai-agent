"""
Helper functions for updating task status with progress, ETA, and current step
"""
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Task, TaskEvent
from datetime import datetime


def update_task_status(
    db: Session,
    task_id: UUID,
    *,
    progress: int,
    eta_seconds: Optional[int] = None,
    current_step: Optional[str] = None
) -> None:
    """Update task status with progress, ETA, and current step"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return
    
    # Clamp progress to 0-100
    progress = max(0, min(100, progress))
    
    task.progress = progress
    task.eta_seconds = eta_seconds
    task.current_step = current_step
    task.updated_at = datetime.utcnow()
    
    # Emit event
    event = TaskEvent(
        task_id=task_id,
        event_type="PROGRESS_UPDATE",
        payload={
            "progress": progress,
            "eta_seconds": eta_seconds,
            "current_step": current_step
        }
    )
    db.add(event)
    db.commit()

