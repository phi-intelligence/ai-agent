from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Industry
from app.schemas import IndustryResponse

router = APIRouter(prefix="/industries", tags=["industries"])


@router.get("", response_model=list[IndustryResponse])
async def list_industries(db: Session = Depends(get_db)):
    """List all industries"""
    industries = db.query(Industry).all()
    return industries


