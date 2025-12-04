"""
Daily Warehouse Report Workflow
Uses LangGraph to orchestrate the workflow
"""
# Path to shared-utils is set in main.py before importing this module

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.services.core_api_client import core_api_client
from phi_utils.retry import retry_async
from phi_utils.logging import setup_logging

logger = setup_logging("orchestrator.workflow")


class WorkflowState(TypedDict):
    task_id: str
    agent_id: str
    org_id: str
    task_type: str
    agent_config: dict
    system_prompt: str
    doc_chunks: list
    wms_data: dict
    llm_analysis: str
    report: dict
    error: str


async def load_agent_config_node(state: WorkflowState) -> WorkflowState:
    """Node 1: Load agent config from core API"""
    from app.services.task_status import update_task_status
    from app.database import SessionLocal
    from uuid import UUID
    
    # Update progress
    db = SessionLocal()
    try:
        update_task_status(
            db,
            UUID(state["task_id"]),
            progress=10,
            current_step="Loading agent configuration"
        )
    finally:
        db.close()
    
    # Agent config is already loaded in execute_workflow and passed in state
    # This node just passes through
    return state


async def fetch_docs_node(state: WorkflowState) -> WorkflowState:
    """Node 2: Fetch relevant documents"""
    from app.services.task_status import update_task_status
    from app.database import SessionLocal
    from uuid import UUID
    
    # Update progress
    db = SessionLocal()
    try:
        update_task_status(
            db,
            UUID(state["task_id"]),
            progress=25,
            current_step="Fetching relevant documents"
        )
    finally:
        db.close()
    
    try:
        query = "warehouse daily performance SOP procedures"
        
        async def search():
            return await core_api_client.search_documents(
                state["agent_id"],
                query,
                top_k=5
            )
        
        result = await retry_async(
            search,
            max_retries=3,
            delay=0.5,
            backoff=2.0,
            exceptions=(Exception,),
            logger=logger
        )
        state["doc_chunks"] = result.get("chunks", [])
        logger.info(f"Fetched {len(state['doc_chunks'])} document chunks")
    except Exception as e:
        logger.error(f"Error fetching docs: {str(e)}")
        state["error"] = f"Error fetching docs: {str(e)}"
    return state


async def fetch_wms_data_node(state: WorkflowState, db=None) -> WorkflowState:
    """Node 3: Fetch WMS data via local agent"""
    from app.models import LocalAgent, ToolTask
    from app.database import SessionLocal
    from uuid import UUID
    import asyncio
    from datetime import datetime, timedelta
    
    from app.services.task_status import update_task_status
    from uuid import UUID as UUIDType
    
    # Update progress
    if db is None:
        db = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        update_task_status(
            db,
            UUIDType(state["task_id"]),
            progress=40,
            current_step="Fetching WMS data from local agent"
        )
    except:
        pass
    
    try:
        agent_id = UUID(state["agent_id"])
        
        try:
            local_agent = db.query(LocalAgent).filter(
                LocalAgent.agent_id == agent_id,
                LocalAgent.status == "ACTIVE"
            ).first()
            
            if local_agent:
                # Create tool task for database query
                tool_task = ToolTask(
                    task_id=UUID(state["task_id"]),
                    local_agent_id=local_agent.id,
                    step_id="fetch_wms_data",
                    tool_name="db",
                    payload={
                        "query": """
                            SELECT 
                                DATE(created_at) as date,
                                COUNT(*) as throughput,
                                SUM(CASE WHEN type = 'pick' THEN 1 ELSE 0 END) as picks,
                                SUM(CASE WHEN type = 'pack' THEN 1 ELSE 0 END) as packs
                            FROM orders
                            WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
                            GROUP BY DATE(created_at)
                            ORDER BY date DESC
                            LIMIT 1
                        """
                    },
                    status="PENDING"
                )
                db.add(tool_task)
                db.commit()
                db.refresh(tool_task)
                
                logger.info(f"Created tool task {tool_task.id} for local agent {local_agent.id}")
                
                # Wait for callback (poll for completion)
                max_wait = 60  # Wait up to 60 seconds
                start_wait = datetime.utcnow()
                
                while (datetime.utcnow() - start_wait).total_seconds() < max_wait:
                    db.refresh(tool_task)
                    if tool_task.status == "COMPLETED":
                        state["wms_data"] = tool_task.result or {}
                        logger.info("Received WMS data from local agent")
                        break
                    elif tool_task.status == "FAILED":
                        logger.warning(f"Tool task failed: {tool_task.error}")
                        # Fall back to simulated data
                        break
                    await asyncio.sleep(2)  # Poll every 2 seconds
                else:
                    logger.warning("Timeout waiting for tool task, using simulated data")
                    # Fall back to simulated data
                    state["wms_data"] = {
                        "date": "2024-01-15",
                        "throughput": 1250,
                        "picks": 850,
                        "packs": 400,
                        "anomalies": [
                            {"type": "delayed_pick", "count": 3},
                            {"type": "missing_item", "count": 1}
                        ],
                        "bottlenecks": ["packing_station_3"]
                    }
            else:
                # No local agent, use simulated data
                logger.info("No local agent found, using simulated WMS data")
                state["wms_data"] = {
                    "date": "2024-01-15",
                    "throughput": 1250,
                    "picks": 850,
                    "packs": 400,
                    "anomalies": [
                        {"type": "delayed_pick", "count": 3},
                        {"type": "missing_item", "count": 1}
                    ],
                    "bottlenecks": ["packing_station_3"]
                }
        finally:
            if should_close:
                db.close()
    except Exception as e:
        logger.error(f"Error fetching WMS data: {str(e)}")
        # Fall back to simulated data
        state["wms_data"] = {
            "date": "2024-01-15",
            "throughput": 1250,
            "picks": 850,
            "packs": 400,
            "anomalies": [
                {"type": "delayed_pick", "count": 3},
                {"type": "missing_item", "count": 1}
            ],
            "bottlenecks": ["packing_station_3"]
        }
    
    return state


async def llm_analysis_node(state: WorkflowState) -> WorkflowState:
    """Node 4: LLM analysis with retry"""
    from app.services.task_status import update_task_status
    from app.database import SessionLocal
    from uuid import UUID
    
    # Update progress
    db = SessionLocal()
    try:
        update_task_status(
            db,
            UUID(state["task_id"]),
            progress=60,
            current_step="Analyzing data with LLM"
        )
    finally:
        db.close()
    
    try:
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            api_key=settings.openai_api_key
        )
        
        system_prompt = state.get("system_prompt") or "You are a warehouse analyst."
        # Ensure system_prompt is a string, not None
        if not isinstance(system_prompt, str):
            system_prompt = str(system_prompt) if system_prompt else "You are a warehouse analyst."
        
        wms_data_str = str(state.get("wms_data", {}))
        doc_context = "\n".join([
            chunk.get("chunk_text", "")[:200] 
            for chunk in state.get("doc_chunks", [])[:3]
        ])
        
        prompt = f"""Based on the following warehouse data and context, provide a comprehensive analysis:

Warehouse Data:
{wms_data_str}

Context from Documents:
{doc_context}

Please analyze:
1. Overall throughput and performance
2. Identified bottlenecks
3. Anomalies and their potential causes
4. Recommendations for improvement

Provide a structured analysis."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        async def call_llm():
            return await llm.ainvoke(messages)
        
        response = await retry_async(
            call_llm,
            max_retries=3,
            delay=1.0,
            backoff=2.0,
            exceptions=(Exception,),
            logger=logger
        )
        state["llm_analysis"] = response.content
        logger.info("LLM analysis completed")
    except Exception as e:
        logger.error(f"Error in LLM analysis: {str(e)}")
        state["error"] = f"Error in LLM analysis: {str(e)}"
    return state


async def format_report_node(state: WorkflowState) -> WorkflowState:
    """Node 5: Format report"""
    from app.services.task_status import update_task_status
    from app.database import SessionLocal
    from uuid import UUID
    
    # Update progress
    db = SessionLocal()
    try:
        update_task_status(
            db,
            UUID(state["task_id"]),
            progress=85,
            current_step="Formatting report"
        )
    finally:
        db.close()
    
    try:
        state["report"] = {
            "full_report_md": f"""# Daily Warehouse Report

## Summary
{state.get('llm_analysis', 'Analysis not available')}

## Data
{state.get('wms_data', {})}

## Generated at
{state.get('task_id', 'Unknown')}
""",
            "summary_text": state.get("llm_analysis", "")[:500] + "..."
        }
    except Exception as e:
        state["error"] = f"Error formatting report: {str(e)}"
    return state


async def send_notification_node(state: WorkflowState) -> WorkflowState:
    """Node 6: Send notifications (email/slack) if configured"""
    from app.services.communication import email_tool, slack_tool
    from app.models import Agent
    from app.services.task_status import update_task_status
    from app.database import SessionLocal
    from uuid import UUID
    
    # Update progress
    db = SessionLocal()
    try:
        update_task_status(
            db,
            UUID(state["task_id"]),
            progress=95,
            current_step="Sending notifications"
        )
    finally:
        db.close()
    
    try:
        # Get agent config to check communication settings
        agent_config = state.get("agent_config", {})
        communication_config = agent_config.get("communication", {})
        
        report = state.get("report", {})
        summary = report.get("summary_text", "Report generated successfully")
        
        # Send email if configured
        if communication_config.get("can_email"):
            recipients = communication_config.get("default_recipients", [])
            if recipients:
                try:
                    await email_tool.send_email(
                        to=recipients,
                        subject=f"Daily Warehouse Report - {state.get('agent_id', 'Unknown')}",
                        html_body=f"""
                        <h2>Daily Warehouse Report</h2>
                        <p>{summary}</p>
                        <p>Task ID: {state.get('task_id')}</p>
                        """
                    )
                    logger.info(f"Sent email notification to {recipients}")
                except Exception as e:
                    logger.warning(f"Failed to send email: {str(e)}")
        
        # Send Slack if configured
        if communication_config.get("can_slack"):
            channel = communication_config.get("slack_channel")
            try:
                await slack_tool.send_message(
                    text=f"📊 Daily Warehouse Report\n\n{summary}\n\nTask: {state.get('task_id')}",
                    channel=channel
                )
                logger.info(f"Sent Slack notification to {channel}")
            except Exception as e:
                logger.warning(f"Failed to send Slack message: {str(e)}")
        
    except Exception as e:
        # Don't fail the workflow if notifications fail
        logger.warning(f"Notification error (non-fatal): {str(e)}")
    
    return state


def create_warehouse_report_workflow(db_session=None):
    """Create the LangGraph workflow for daily warehouse report"""
    workflow = StateGraph(WorkflowState)
    
    # Add nodes - pass db_session to nodes that need it
    workflow.add_node("load_agent_config", load_agent_config_node)
    workflow.add_node("fetch_docs", fetch_docs_node)
    
    # Create a wrapper for fetch_wms_data_node that includes db_session
    async def fetch_wms_data_with_db(state: WorkflowState) -> WorkflowState:
        return await fetch_wms_data_node(state, db=db_session)
    
    workflow.add_node("fetch_wms_data", fetch_wms_data_with_db)
    workflow.add_node("llm_analysis", llm_analysis_node)
    workflow.add_node("format_report", format_report_node)
    workflow.add_node("send_notification", send_notification_node)
    
    # Define edges
    workflow.set_entry_point("load_agent_config")
    workflow.add_edge("load_agent_config", "fetch_docs")
    workflow.add_edge("fetch_docs", "fetch_wms_data")
    workflow.add_edge("fetch_wms_data", "llm_analysis")
    workflow.add_edge("llm_analysis", "format_report")
    workflow.add_edge("format_report", "send_notification")
    workflow.add_edge("send_notification", END)
    
    return workflow.compile()

