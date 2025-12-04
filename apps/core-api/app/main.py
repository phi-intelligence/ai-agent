import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import get_db, engine, Base
from app.models import User, Organization, OrganizationMember
from app.schemas import (
    UserSignup, UserLogin, Token, UserWithMemberships,
    OrganizationCreate, OrganizationResponse, MembershipResponse
)
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user
)
from app.routers import industries, role_templates, tools, agents, documents, admin
from app.routers.agents import agent_detail_router
from phi_utils.logging import setup_logging, ContextLogger

# Set up structured logging
logger = setup_logging("core-api")

# Create tables (in production, use migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Phi Agents Core API", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server (default port)
        "http://localhost:3001",  # Next.js dev server (alternative port)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/auth/signup", response_model=Token)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=UserWithMemberships)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    memberships = db.query(OrganizationMember).filter(
        OrganizationMember.user_id == current_user.id
    ).all()
    
    return UserWithMemberships(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at,
        memberships=[
            MembershipResponse(
                id=m.id,
                org_id=m.org_id,
                role=m.role,
                created_at=m.created_at
            )
            for m in memberships
        ]
    )


@app.post("/orgs", response_model=OrganizationResponse)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create organization
    org = Organization(
        name=org_data.name,
        owner_user_id=current_user.id
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Add owner as member
    member = OrganizationMember(
        org_id=org.id,
        user_id=current_user.id,
        role="OWNER"
    )
    db.add(member)
    db.commit()
    
    return org


@app.get("/orgs", response_model=list[OrganizationResponse])
async def list_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get all orgs where user is a member
    memberships = db.query(OrganizationMember).filter(
        OrganizationMember.user_id == current_user.id
    ).all()
    org_ids = [m.org_id for m in memberships]
    
    orgs = db.query(Organization).filter(Organization.id.in_(org_ids)).all()
    return orgs


@app.get("/orgs/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user is a member
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.org_id == org_id,
        OrganizationMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return org


# Include routers
app.include_router(industries.router)
app.include_router(role_templates.router)
app.include_router(tools.router)
app.include_router(agents.router)
app.include_router(agents.agent_detail_router)
app.include_router(documents.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/internal/agents/{agent_id}")
async def get_agent_internal(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Internal endpoint for service-to-service calls (no auth required)"""
    from uuid import UUID
    from app.models import Agent, AgentTool
    from app.schemas import AgentDetailResponse
    
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


@app.post("/internal/agents/{agent_id}/documents/search-docs")
async def search_documents_internal(
    agent_id: str,
    search_request: dict,
    db: Session = Depends(get_db)
):
    """Internal endpoint for document search (no auth required for service-to-service calls)"""
    from uuid import UUID
    from app.models import Agent, DocumentChunk
    from app.services.document_service import generate_embedding
    from sqlalchemy import text
    
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
    
    query = search_request.get("query", "")
    top_k = search_request.get("top_k", 5)
    
    if not query:
        return {"query": query, "chunks": []}
    
    # Generate embedding for query
    query_embedding = generate_embedding(query)
    
    # Convert embedding list to string format for pgvector
    embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
    
    # Use raw SQL for vector similarity search
    # Note: Using CAST for UUID to avoid parameter binding issues
    from sqlalchemy import text
    chunks_query = text("""
        SELECT id, document_id, chunk_text, metadata
        FROM document_chunks
        WHERE agent_id = CAST(:agent_id AS uuid)
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
    """)
    
    result = db.execute(
        chunks_query,
        {
            "agent_id": str(agent_uuid),
            "embedding": embedding_str,
            "limit": top_k
        }
    )
    
    chunks_data = result.fetchall()
    
    # Build response from results
    chunks = []
    for row in chunks_data:
        chunks.append({
            "id": str(row[0]),
            "document_id": str(row[1]),
            "chunk_text": row[2],
            "metadata": row[3] if row[3] else {}
        })
    
    return {
        "query": query,
        "chunks": chunks
    }

