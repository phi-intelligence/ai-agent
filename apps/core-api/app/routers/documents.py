import os
import uuid
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document, DocumentChunk, Agent, OrganizationMember
from app.schemas import DocumentResponse, DocumentChunkResponse, DocumentSearchRequest, DocumentSearchResponse
from app.auth import get_current_user
from app.models import User
from app.services.document_service import process_document

router = APIRouter(prefix="/agents/{agent_id}/documents", tags=["documents"])

# Create uploads directory if it doesn't exist
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)


@router.post("", response_model=DocumentResponse)
async def upload_document(
    agent_id: str,
    file: UploadFile = File(...),
    source_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process a document for an agent"""
    try:
        agent_uuid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid agent ID"
        )
    
    # Check if agent exists and user has access
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
    
    # Validate source_type
    valid_source_types = ["JD", "SOP", "POLICY", "MANUAL", "OTHER"]
    if source_type not in valid_source_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source_type. Must be one of: {', '.join(valid_source_types)}"
        )
    
    # Save file
    file_ext = Path(file.filename).suffix
    file_id = str(uuid.uuid4())
    file_path = UPLOADS_DIR / f"{file_id}{file_ext}"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Process document
        document = process_document(
            db=db,
            file_path=str(file_path),
            file_name=file.filename,
            org_id=agent.org_id,
            agent_id=agent_uuid,
            source_type=source_type
        )
        
        return document
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents for an agent"""
    try:
        agent_uuid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid agent ID"
        )
    
    # Check if agent exists and user has access
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
    
    documents = db.query(Document).filter(Document.agent_id == agent_uuid).all()
    return documents


@router.post("/search-docs", response_model=DocumentSearchResponse)
async def search_documents(
    agent_id: str,
    search_request: DocumentSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search documents using vector similarity"""
    try:
        agent_uuid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid agent ID"
        )
    
    # Check if agent exists and user has access
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
    
    # Generate embedding for query
    from app.services.document_service import generate_embedding
    query_embedding = generate_embedding(search_request.query)
    
    # Vector search using cosine similarity
    # Using pgvector's cosine distance operator
    top_k = search_request.top_k or 5
    
    # Convert embedding list to string format for pgvector
    embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
    
    # Use raw SQL for vector similarity search
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
            "id": row[0],
            "document_id": row[1],
            "chunk_text": row[2],
            "metadata": row[3] if row[3] else {}
        })
    
    return DocumentSearchResponse(
        query=search_request.query,
        chunks=[
            DocumentChunkResponse(
                id=chunk["id"],
                document_id=chunk["document_id"],
                chunk_text=chunk["chunk_text"],
                metadata=chunk["metadata"]
            )
            for chunk in chunks
        ]
    )

