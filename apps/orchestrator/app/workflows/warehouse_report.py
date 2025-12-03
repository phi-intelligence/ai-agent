"""
Daily Warehouse Report Workflow
Uses LangGraph to orchestrate the workflow
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

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
    # In a real implementation, we'd fetch from core API
    # For now, we'll use the agent_config from state
    return state


async def fetch_docs_node(state: WorkflowState) -> WorkflowState:
    """Node 2: Fetch relevant documents"""
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
    # Create tool task for local agent
    # In a real implementation, we'd:
    # 1. Find local agent for this agent_id
    # 2. Create ToolTask
    # 3. Wait for callback
    # For now, simulate with mock data if no local agent
    
    # Check if we have a local agent (simplified - in real impl, query DB)
    # For now, simulate
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
    try:
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            api_key=settings.openai_api_key
        )
        
        system_prompt = state.get("system_prompt", "You are a warehouse analyst.")
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


def create_warehouse_report_workflow():
    """Create the LangGraph workflow for daily warehouse report"""
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("load_agent_config", load_agent_config_node)
    workflow.add_node("fetch_docs", fetch_docs_node)
    workflow.add_node("fetch_wms_data", fetch_wms_data_node)
    workflow.add_node("llm_analysis", llm_analysis_node)
    workflow.add_node("format_report", format_report_node)
    
    # Define edges
    workflow.set_entry_point("load_agent_config")
    workflow.add_edge("load_agent_config", "fetch_docs")
    workflow.add_edge("fetch_docs", "fetch_wms_data")
    workflow.add_edge("fetch_wms_data", "llm_analysis")
    workflow.add_edge("llm_analysis", "format_report")
    workflow.add_edge("format_report", END)
    
    return workflow.compile()

