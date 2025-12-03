import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta
import asyncio

from app.database import get_db, engine, Base
from app.models import Task, TaskEvent, LocalAgent, ToolTask, TaskMetrics
from app.schemas import (
    TaskCreate, TaskResponse, TaskDetailResponse, TaskEventResponse,
    HeartbeatRequest, HeartbeatResponse, ToolCallbackRequest,
    PendingTasksResponse, PendingTaskResponse
)
from app.services.core_api_client import core_api_client
from app.workflows.warehouse_report import create_warehouse_report_workflow
from phi_utils.logging import setup_logging, ContextLogger
from phi_utils.retry import retry_async

# Set up structured logging
logger = setup_logging("orchestrator")

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Phi Agents Orchestrator", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Task timeout configuration (in seconds)
TASK_TIMEOUT = 300  # 5 minutes

async def execute_workflow(task_id: UUID, agent_id: UUID, org_id: UUID, task_type: str, task_input: dict, db: Session):
    """Execute workflow in background with timeout"""
    ctx_logger = ContextLogger(logger, task_id=str(task_id), agent_id=str(agent_id), org_id=str(org_id))
    start_time = datetime.utcnow()
    
    try:
        # Update task status
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            ctx_logger.warning("Task not found in database")
            return
        
        task.status = "RUNNING"
        db.commit()
        
        ctx_logger.info(f"Starting workflow: {task_type}")
        
        # Log event
        event = TaskEvent(
            task_id=task_id,
            event_type="WORKFLOW_STARTED",
            payload={"task_type": task_type}
        )
        db.add(event)
        db.commit()
        
        # Get agent config from core API with retry
        try:
            async def fetch_agent():
                return await core_api_client.get_agent(str(agent_id), token="")
            
            agent_data = await retry_async(
                fetch_agent,
                max_retries=3,
                delay=1.0,
                backoff=2.0,
                exceptions=(Exception,),
                logger=ctx_logger.logger
            )
            system_prompt = agent_data.get("system_prompt", "You are a warehouse analyst.")
            agent_config = agent_data.get("config", {})
            ctx_logger.info("Fetched agent config from core API")
        except Exception as e:
            ctx_logger.warning(f"Could not fetch agent config, using defaults: {str(e)}")
            # Fallback if core API is unavailable
            system_prompt = "You are a warehouse analyst."
            agent_config = {}
        
        initial_state = {
            "task_id": str(task_id),
            "agent_id": str(agent_id),
            "org_id": str(org_id),
            "task_type": task_type,
            "agent_config": agent_config,
            "system_prompt": system_prompt,
            "doc_chunks": [],
            "wms_data": {},
            "llm_analysis": "",
            "report": {},
            "error": None
        }
        
        # Run workflow with timeout
        try:
            if task_type == "DAILY_WAREHOUSE_REPORT":
                workflow = create_warehouse_report_workflow()
                final_state = await asyncio.wait_for(
                    workflow.ainvoke(initial_state),
                    timeout=TASK_TIMEOUT
                )
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Save results
            if final_state.get("error"):
                task.status = "FAILED"
                task.error = final_state["error"]
                ctx_logger.error(f"Workflow failed: {final_state['error']}")
            else:
                task.status = "SUCCESS"
                task.output = final_state.get("report", {})
                ctx_logger.info("Workflow completed successfully")
            
            # Log completion event
            event = TaskEvent(
                task_id=task_id,
                event_type="WORKFLOW_COMPLETED",
                payload={"status": task.status}
            )
            db.add(event)
            
            # Calculate and store metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            metrics = TaskMetrics(
                task_id=task_id,
                org_id=org_id,
                agent_id=agent_id,
                task_type=task_type,
                duration_seconds=duration,
                llm_calls=1,  # Simplified - in real impl, count actual calls
                tool_calls=0  # Simplified - in real impl, count actual tool calls
            )
            db.add(metrics)
            db.commit()
            
            ctx_logger.info(f"Task completed in {duration:.2f}s")
            
        except asyncio.TimeoutError:
            task.status = "FAILED"
            task.error = f"Task timed out after {TASK_TIMEOUT} seconds"
            ctx_logger.error(f"Task timeout after {TASK_TIMEOUT}s")
            
            event = TaskEvent(
                task_id=task_id,
                event_type="WORKFLOW_TIMEOUT",
                payload={"timeout_seconds": TASK_TIMEOUT}
            )
            db.add(event)
            
            # Store metrics for failed task
            duration = (datetime.utcnow() - start_time).total_seconds()
            metrics = TaskMetrics(
                task_id=task_id,
                org_id=org_id,
                agent_id=agent_id,
                task_type=task_type,
                duration_seconds=duration,
                llm_calls=0,
                tool_calls=0
            )
            db.add(metrics)
            db.commit()
            
        except Exception as e:
            task.status = "FAILED"
            task.error = str(e)
            ctx_logger.exception("Workflow execution error")
            
            event = TaskEvent(
                task_id=task_id,
                event_type="WORKFLOW_ERROR",
                payload={"error": str(e)}
            )
            db.add(event)
            
            # Store metrics for failed task
            duration = (datetime.utcnow() - start_time).total_seconds()
            metrics = TaskMetrics(
                task_id=task_id,
                org_id=org_id,
                agent_id=agent_id,
                task_type=task_type,
                duration_seconds=duration,
                llm_calls=0,
                tool_calls=0
            )
            db.add(metrics)
            db.commit()
        
    except Exception as e:
        # Update task with error
        ctx_logger.exception("Fatal error in workflow execution")
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "FAILED"
            task.error = str(e)
            db.commit()
            
            event = TaskEvent(
                task_id=task_id,
                event_type="WORKFLOW_ERROR",
                payload={"error": str(e)}
            )
            db.add(event)
            
            # Store metrics for failed task
            duration = (datetime.utcnow() - start_time).total_seconds()
            metrics = TaskMetrics(
                task_id=task_id,
                org_id=org_id,
                agent_id=agent_id,
                task_type=task_type,
                duration_seconds=duration,
                llm_calls=0,
                tool_calls=0
            )
            db.add(metrics)
            db.commit()
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        ctx_logger.info(f"Workflow execution failed after {duration}s")


@app.post("/agents/{agent_id}/run-task", response_model=TaskResponse)
async def run_task(
    agent_id: str,
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create and run a task"""
    try:
        agent_uuid = UUID(agent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid agent ID"
        )
    
    # Get agent from core API to get org_id
    try:
        agent_data = await core_api_client.get_agent(agent_id, token="")
        org_uuid = UUID(agent_data["org_id"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not fetch agent: {str(e)}"
        )
    
    # Create task
    task = Task(
        agent_id=agent_uuid,
        org_id=org_uuid,
        type=task_data.type,
        status="PENDING",
        input=task_data.input
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Start workflow in background
    # Note: We need to create a new DB session for background task
    from app.database import SessionLocal
    import asyncio
    
    async def run_workflow_async():
        db_session = SessionLocal()
        try:
            await execute_workflow(
                task.id,
                agent_uuid,
                org_uuid,
                task_data.type,
                task_data.input or {},
                db_session
            )
        finally:
            db_session.close()
    
    def run_workflow():
        asyncio.run(run_workflow_async())
    
    background_tasks.add_task(run_workflow)
    
    return task


@app.get("/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Get task details"""
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID"
        )
    
    task = db.query(Task).filter(Task.id == task_uuid).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    events = db.query(TaskEvent).filter(TaskEvent.task_id == task_uuid).order_by(TaskEvent.timestamp).all()
    
    return TaskDetailResponse(
        id=task.id,
        agent_id=task.agent_id,
        org_id=task.org_id,
        type=task.type,
        status=task.status,
        input=task.input,
        output=task.output,
        error=task.error,
        created_at=task.created_at,
        updated_at=task.updated_at,
        events=[
            TaskEventResponse(
                id=e.id,
                task_id=e.task_id,
                timestamp=e.timestamp,
                event_type=e.event_type,
                payload=e.payload
            )
            for e in events
        ]
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/local-agents/heartbeat", response_model=HeartbeatResponse)
async def heartbeat(
    request: HeartbeatRequest,
    db: Session = Depends(get_db)
):
    """Register or update local agent heartbeat"""
    ctx_logger = ContextLogger(
        logger,
        agent_id=request.agent_id,
        org_id=request.org_id
    )
    
    try:
        agent_uuid = UUID(request.agent_id)
        org_uuid = UUID(request.org_id)
    except ValueError:
        ctx_logger.error("Invalid agent_id or org_id in heartbeat")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid agent_id or org_id"
        )
    
    # Find or create local agent
    if request.local_agent_id:
        try:
            local_agent_uuid = UUID(request.local_agent_id)
            local_agent = db.query(LocalAgent).filter(LocalAgent.id == local_agent_uuid).first()
        except ValueError:
            local_agent = None
    else:
        local_agent = None
    
    if not local_agent:
        # Create new local agent
        local_agent = LocalAgent(
            agent_id=agent_uuid,
            org_id=org_uuid,
            name=request.name,
            status=request.status,
            metadata=request.capabilities
        )
        db.add(local_agent)
    else:
        # Update existing
        local_agent.status = request.status
        local_agent.last_heartbeat_at = datetime.utcnow()
        local_agent.metadata = request.capabilities
    
    db.commit()
    db.refresh(local_agent)
    
    ctx_logger.info(f"Local agent heartbeat: {local_agent.status}")
    
    return HeartbeatResponse(
        id=str(local_agent.id),
        status=local_agent.status
    )


@app.get("/local-agents/{local_agent_id}/pending-tasks", response_model=PendingTasksResponse)
async def get_pending_tasks(
    local_agent_id: str,
    db: Session = Depends(get_db)
):
    """Get pending tool tasks for a local agent"""
    try:
        local_agent_uuid = UUID(local_agent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid local agent ID"
        )
    
    # Get pending tool tasks
    tool_tasks = db.query(ToolTask).filter(
        ToolTask.local_agent_id == local_agent_uuid,
        ToolTask.status == "PENDING"
    ).all()
    
    return PendingTasksResponse(
        tasks=[
            PendingTaskResponse(
                task_tool_id=str(tt.id),
                task_id=str(tt.task_id),
                tool=tt.tool_name,
                payload=tt.payload
            )
            for tt in tool_tasks
        ]
    )


@app.post("/tool-callbacks")
async def tool_callback(
    callback: ToolCallbackRequest,
    db: Session = Depends(get_db)
):
    """Receive tool execution result from local agent"""
    ctx_logger = ContextLogger(
        logger,
        task_id=callback.task_id
    )
    
    try:
        task_uuid = UUID(callback.task_id)
    except ValueError:
        ctx_logger.error("Invalid task ID in tool callback")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID"
        )
    
    # Find tool task
    tool_task = db.query(ToolTask).filter(
        ToolTask.task_id == task_uuid,
        ToolTask.step_id == callback.step_id
    ).first()
    
    if not tool_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool task not found"
        )
    
    # Update tool task
    if callback.error:
        tool_task.status = "FAILED"
        tool_task.error = callback.error
    else:
        tool_task.status = "COMPLETED"
        tool_task.result = callback.result
    tool_task.completed_at = datetime.utcnow()
    
    db.commit()
    
    # Log event
    event = TaskEvent(
        task_id=task_uuid,
        event_type="TOOL_COMPLETED" if not callback.error else "TOOL_FAILED",
        payload={
            "step_id": callback.step_id,
            "tool_name": callback.tool_name,
            "error": callback.error
        }
    )
    db.add(event)
    db.commit()
    
    ctx_logger.info(f"Tool callback received: {callback.tool_name} - {tool_task.status}")
    
    return {"status": "ok"}


@app.on_event("shutdown")
async def shutdown():
    await core_api_client.close()

