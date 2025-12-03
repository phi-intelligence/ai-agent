from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Agent, AgentTool, OrganizationMember, Tool
from app.schemas import AgentCreate, AgentResponse, AgentDetailResponse
from app.auth import get_current_user
from app.models import User
from app.services.profile_service import generate_agent_profile, generate_agent_config
import yaml

router = APIRouter(prefix="/orgs/{org_id}/agents", tags=["agents"])


@router.post("", response_model=AgentResponse)
async def create_agent(
    org_id: str,
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new agent for an organization"""
    try:
        org_uuid = UUID(org_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization ID"
        )
    
    # Check if user is a member of the organization
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.org_id == org_uuid,
        OrganizationMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found or access denied"
        )
    
    # Create agent
    agent = Agent(
        org_id=org_uuid,
        industry_id=agent_data.industry_id,
        role_template_id=agent_data.role_template_id,
        name=agent_data.name,
        status="ACTIVE"
    )
    db.add(agent)
    db.flush()  # Get the agent ID
    
    # Add tools
    for tool_id in agent_data.tool_ids:
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            continue  # Skip invalid tool IDs
        
        agent_tool = AgentTool(
            agent_id=agent.id,
            tool_id=tool_id
        )
        db.add(agent_tool)
    
    db.commit()
    db.refresh(agent)
    
    return agent


@router.get("", response_model=list[AgentResponse])
async def list_agents(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all agents for an organization"""
    try:
        org_uuid = UUID(org_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization ID"
        )
    
    # Check if user is a member of the organization
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.org_id == org_uuid,
        OrganizationMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found or access denied"
        )
    
    agents = db.query(Agent).filter(Agent.org_id == org_uuid).all()
    return agents


# Separate router for agent detail (no org_id in path)
agent_detail_router = APIRouter(prefix="/agents", tags=["agents"])


@agent_detail_router.get("/{agent_id}", response_model=AgentDetailResponse)
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get agent details"""
    try:
        agent_uuid = UUID(agent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid agent ID"
        )
    
    agent = db.query(Agent).filter(Agent.id == agent_uuid).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if user is a member of the organization
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.org_id == agent.org_id,
        OrganizationMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Load agent tools
    agent_tools = db.query(AgentTool).filter(AgentTool.agent_id == agent_uuid).all()
    
    return AgentDetailResponse(
        id=agent.id,
        org_id=agent.org_id,
        industry_id=agent.industry_id,
        role_template_id=agent.role_template_id,
        name=agent.name,
        status=agent.status,
        system_prompt=agent.system_prompt,
        config=agent.config,
        created_at=agent.created_at,
        agent_tools=[
            {
                "id": at.id,
                "tool_id": at.tool_id,
                "config": at.config
            }
            for at in agent_tools
        ]
    )


@agent_detail_router.post("/{agent_id}/generate-profile")
async def generate_profile(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate agent profile using LLM"""
    try:
        agent_uuid = UUID(agent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid agent ID"
        )
    
    agent = db.query(Agent).filter(Agent.id == agent_uuid).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if user is a member of the organization
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.org_id == agent.org_id,
        OrganizationMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    try:
        # Generate profile
        system_prompt, config = generate_agent_profile(db, agent)
        
        # Update agent
        agent.system_prompt = system_prompt
        agent.config = config
        db.commit()
        db.refresh(agent)
        
        return {
            "message": "Profile generated successfully",
            "system_prompt": system_prompt,
            "config": config
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating profile: {str(e)}"
        )


@agent_detail_router.get("/{agent_id}/config")
async def get_agent_config(
    agent_id: str,
    format: str = "yaml",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get agent config for local agent download"""
    try:
        agent_uuid = UUID(agent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid agent ID"
        )
    
    agent = db.query(Agent).filter(Agent.id == agent_uuid).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if user is a member of the organization
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.org_id == agent.org_id,
        OrganizationMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    # Generate config
    config = generate_agent_config(db, agent)
    
    if format.lower() == "yaml":
        from fastapi.responses import Response
        yaml_content = yaml.dump(config, default_flow_style=False, sort_keys=False)
        return Response(
            content=yaml_content,
            media_type="application/x-yaml",
            headers={
                "Content-Disposition": f'attachment; filename="phi-agent-config-{agent.name.replace(" ", "-")}.yaml"'
            }
        )
    else:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content=config,
            headers={
                "Content-Disposition": f'attachment; filename="phi-agent-config-{agent.name.replace(" ", "-")}.json"'
            }
        )

