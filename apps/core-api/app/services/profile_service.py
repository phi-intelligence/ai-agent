import os
import sys
import json
from typing import Dict, Any, List
from openai import OpenAI
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from phi_utils.retry import retry_async
from phi_utils.logging import setup_logging

logger = setup_logging("core-api.profile_service")

from app.models import Agent, Industry, RoleTemplate, DocumentChunk, Tool, AgentTool

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))


def generate_agent_profile(
    db: Session,
    agent: Agent
) -> tuple[str, Dict[str, Any]]:
    """Generate agent profile using LLM"""
    
    # Load industry and role template
    industry = db.query(Industry).filter(Industry.id == agent.industry_id).first()
    role_template = db.query(RoleTemplate).filter(RoleTemplate.id == agent.role_template_id).first()
    
    # Get sample document chunks (5-10 chunks from JDs and SOPs)
    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.agent_id == agent.id
    ).limit(10).all()
    
    # Get agent tools
    agent_tools = db.query(AgentTool).filter(AgentTool.agent_id == agent.id).all()
    tool_ids = [at.tool_id for at in agent_tools]
    tools = db.query(Tool).filter(Tool.id.in_(tool_ids)).all() if tool_ids else []
    
    # Build context
    industry_info = f"Industry: {industry.name if industry else 'Unknown'}\n{industry.description if industry and industry.description else ''}"
    role_info = f"Role: {role_template.name if role_template else 'Unknown'}\n{role_template.description if role_template and role_template.description else ''}"
    
    # Sample document chunks
    doc_context = ""
    if chunks:
        doc_context = "\n\nSample Context from Documents:\n"
        for i, chunk in enumerate(chunks[:10], 1):
            doc_context += f"\n--- Chunk {i} ---\n{chunk.chunk_text[:500]}\n"
    
    # Tools info
    tools_info = ""
    if tools:
        tools_info = "\n\nAvailable Tools:\n"
        for tool in tools:
            tools_info += f"- {tool.name} ({tool.key}): {tool.description or 'No description'}\n"
    
    # Build prompt
    prompt = f"""You are building a virtual employee (AI agent) for a company. Based on the following information, generate a comprehensive agent profile.

{industry_info}

{role_info}

{tools_info}

{doc_context}

Please generate:
1. A detailed system prompt that defines the agent's role, responsibilities, and behavior
2. A list of capabilities the agent should have
3. Example workflows the agent might perform
4. Safety constraints and guidelines
5. Tool usage rules and best practices

Format your response as JSON with the following structure:
{{
  "system_prompt": "A comprehensive system prompt (2-3 paragraphs) that defines the agent's identity, role, and behavior...",
  "capabilities": ["capability1", "capability2", ...],
  "workflows": [
    {{
      "type": "WORKFLOW_TYPE",
      "name": "Workflow Name",
      "description": "Description of what this workflow does",
      "schedule": "optional cron expression"
    }}
  ],
  "safety_constraints": ["constraint1", "constraint2", ...],
  "tool_usage_rules": {{
    "tool_key": "rules for using this tool"
  }}
}}

Be specific and detailed. The system prompt should be professional and clearly define the agent's purpose."""
    
    # Call OpenAI with retry (sync version)
    from phi_utils.retry import retry_sync
    
    def call_llm():
        return openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at designing AI agent profiles and system prompts. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
    
    try:
        response = retry_sync(
            call_llm,
            max_retries=3,
            delay=1.0,
            backoff=2.0,
            exceptions=(Exception,),
            logger=logger
        )
    except Exception as e:
        logger.error(f"Failed to generate profile after retries: {str(e)}")
        raise
    
    # Parse response
    content = response.choices[0].message.content.strip()
    
    # Try to extract JSON from markdown code blocks if present
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    
    try:
        profile_data = json.loads(content)
    except json.JSONDecodeError:
        # Fallback: create a basic profile
        profile_data = {
            "system_prompt": f"You are a {role_template.name if role_template else 'virtual employee'} in the {industry.name if industry else 'business'} industry. Your role is to assist with tasks related to your position.",
            "capabilities": role_template.default_capabilities if role_template and role_template.default_capabilities else [],
            "workflows": [],
            "safety_constraints": ["Always follow company policies", "Respect data privacy", "Escalate critical issues"],
            "tool_usage_rules": {}
        }
    
    system_prompt = profile_data.get("system_prompt", "")
    config = {
        "capabilities": profile_data.get("capabilities", []),
        "workflows": profile_data.get("workflows", []),
        "safety_constraints": profile_data.get("safety_constraints", []),
        "tool_usage_rules": profile_data.get("tool_usage_rules", {})
    }
    
    return system_prompt, config


def generate_agent_config(
    db: Session,
    agent: Agent
) -> Dict[str, Any]:
    """Generate config YAML/JSON for local agent"""
    
    # Get tools
    agent_tools = db.query(AgentTool).filter(AgentTool.agent_id == agent.id).all()
    tool_ids = [at.tool_id for at in agent_tools]
    tools = db.query(Tool).filter(Tool.id.in_(tool_ids)).all() if tool_ids else []
    
    # Get industry and role
    industry = db.query(Industry).filter(Industry.id == agent.industry_id).first()
    role_template = db.query(RoleTemplate).filter(RoleTemplate.id == agent.role_template_id).first()
    
    # Extract required settings from tool config schemas
    tool_configs = []
    for tool in tools:
        required_settings = []
        if tool.config_schema and isinstance(tool.config_schema, dict):
            required_settings = tool.config_schema.get("required", [])
        tool_configs.append({
            "key": tool.key,
            "required_settings": required_settings
        })
    
    config = {
        "agent_id": str(agent.id),
        "org_id": str(agent.org_id),
        "name": agent.name,
        "industry": industry.key if industry else None,
        "role": role_template.key if role_template else None,
        "llm": {
            "model": "gpt-4",
            "temperature": 0.2
        },
        "tools": tool_configs,
        "memory": {
            "org_namespace": f"org_{agent.org_id}",
            "agent_namespace": f"agent_{agent.id}"
        },
        "workflows": agent.config.get("workflows", []) if agent.config and isinstance(agent.config, dict) else []
    }
    
    return config

