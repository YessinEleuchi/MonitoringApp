from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.application import Application
from app.models.application_stats import ApplicationStats

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/url/{base_url}")
async def get_stats(base_url: str, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.base_url == base_url).first()
    if not app:
        return {"error": "Application not found"}

    stats = db.query(ApplicationStats).filter(ApplicationStats.application_id == app.id).first()
    if not stats:
        return {"error": "No stats available"}

    return {
        "base_url": base_url,
        "success_rate": stats.success_rate,
        "avg_response_time": stats.avg_response_time,
        "last_updated": stats.last_updated.isoformat()
    }