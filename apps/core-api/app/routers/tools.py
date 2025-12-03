from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tool
from app.schemas import ToolResponse

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("", response_model=list[ToolResponse])
async def list_tools(db: Session = Depends(get_db)):
    """List all available tools"""
    tools = db.query(Tool).all()
    return tools


