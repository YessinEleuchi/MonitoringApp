from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.application import Application
from app.models.application_stats import ApplicationStats
from datetime import datetime, timedelta
from sqlalchemy import func, cast, Date
from app.models.monitoring_result import MonitoringResult
from app.models.endpoint import Endpoint
from sqlalchemy import  Float
from app.dependencies.auth import get_current_user



router = APIRouter(
    prefix="/stats",
    tags=["Stats"],
    dependencies=[Depends(get_current_user)]
)
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


@router.get("/weekly/{application_id}")
async def get_weekly_stats(application_id: int, db: Session = Depends(get_db)):
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    results = (
        db.query(
            cast(MonitoringResult.timestamp, Date).label("day"),
            func.avg(MonitoringResult.response_time).label("avg_response_time"),
            func.avg(cast(MonitoringResult.success, Float)).label("success_rate")
        )
        .join(Endpoint)
        .filter(
            Endpoint.application_id == application_id,
            MonitoringResult.timestamp >= seven_days_ago
        )
        .group_by("day")
        .order_by("day")
        .all()
    )

    return [
        {
            "date": str(row.day),
            "avg_response_time": round(row.avg_response_time, 2),
            "success_rate": round(row.success_rate * 100, 2)  # en %
        }
        for row in results
    ]

