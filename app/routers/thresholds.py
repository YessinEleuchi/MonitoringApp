from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.thresholds import Thresholds
from app.schemas.thresholds_sch import ThresholdsCreate, ThresholdsUpdate, ThresholdsOut
from app.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/thresholds",
    tags=["Thresholds"],
    dependencies=[Depends(get_current_user)]
)
@router.post("/", response_model=ThresholdsOut)
def create_thresholds(data: ThresholdsCreate, db: Session = Depends(get_db)):
    existing = db.query(Thresholds).first()
    if existing:
        raise HTTPException(status_code=400, detail="Seuils déjà définis. Utilisez PUT pour mettre à jour.")
    
    thresholds = Thresholds(**data.dict())
    db.add(thresholds)
    db.commit()
    db.refresh(thresholds)
    return thresholds


@router.get("/", response_model=ThresholdsOut)
def get_thresholds(db: Session = Depends(get_db)):
    thresholds = db.query(Thresholds).first()
    if not thresholds:
        raise HTTPException(status_code=404, detail="No thresholds found")
    return thresholds

@router.put("/", response_model=ThresholdsOut)
def update_thresholds(data: ThresholdsUpdate, db: Session = Depends(get_db)):
    thresholds = db.query(Thresholds).first()
    if not thresholds:
        raise HTTPException(status_code=404, detail="No thresholds found")
    for key, value in data.dict().items():
        setattr(thresholds, key, value)
    db.commit()
    db.refresh(thresholds)
    return thresholds
