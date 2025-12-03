from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RoleTemplate, Industry
from app.schemas import RoleTemplateResponse

router = APIRouter(prefix="/role-templates", tags=["role-templates"])


@router.get("", response_model=list[RoleTemplateResponse])
async def list_role_templates(
    industry_key: Optional[str] = Query(None, alias="industry_key"),
    db: Session = Depends(get_db)
):
    """List role templates, optionally filtered by industry"""
    query = db.query(RoleTemplate)
    
    if industry_key:
        industry = db.query(Industry).filter(Industry.key == industry_key).first()
        if industry:
            query = query.filter(RoleTemplate.industry_id == industry.id)
        else:
            return []
    
    role_templates = query.all()
    return role_templates

