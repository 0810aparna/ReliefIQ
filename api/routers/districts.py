import sys
sys.path.append(".")
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.base import get_db
from database.models import District
from database.schemas import DistrictOut

router = APIRouter()


@router.get("/districts", response_model=list[DistrictOut])
def list_districts(db: Session = Depends(get_db)):
    return db.query(District).all()