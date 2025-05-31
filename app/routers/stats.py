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
from humanize import naturaltime  




router = APIRouter(
    prefix="/stats",
    tags=["Stats"],
    dependencies=[Depends(get_current_user)]
)
@router.get("/url/{app_id}")
async def get_stats(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        return {"error": "Application not found"}

    stats = db.query(ApplicationStats).filter(ApplicationStats.application_id == app.id).first()
    if not stats:
        return {"error": "No stats available"}
    endpoint_count = db.query(Endpoint).filter(Endpoint.application_id == app.id).count()
    last_check = db.query(func.max(MonitoringResult.timestamp))\
                   .join(Endpoint)\
                   .filter(Endpoint.application_id == app.id)\
                   .scalar()

    return {
        "app_id": app_id,
        "success_rate": stats.success_rate,
        "avg_response_time": stats.avg_response_time,
        "last_updated": stats.last_updated.isoformat(),
        "endpoints": endpoint_count,
        "last_health_check": naturaltime(datetime.utcnow() - last_check) if last_check else "No health check"
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

@router.get("/all")
async def get_all_stats(db: Session = Depends(get_db)):
    # Compter le nombre total d'applications
    total_apps = db.query(Application).count()
    # Compter le nombre total d'endpoints
    total_endpoints = db.query(Endpoint).count()
    
    apps = db.query(Application).all()
    results = []

    for app in apps:
        stats = db.query(ApplicationStats).filter(ApplicationStats.application_id == app.id).first()
        endpoint_count = db.query(Endpoint).filter(Endpoint.application_id == app.id).count()
        last_check = db.query(func.max(MonitoringResult.timestamp))\
                       .join(Endpoint)\
                       .filter(Endpoint.application_id == app.id)\
                       .scalar()

        results.append({
            "app_id": app.id,
            "endpoints": endpoint_count,
            "last_health_check": naturaltime(datetime.utcnow() - last_check) if last_check else "No health check",
            "success_rate": stats.success_rate if stats else 0,
            "avg_response_time": stats.avg_response_time if stats else 0
        })

    return {
        "total_applications": total_apps,
        "total_endpoints": total_endpoints,
        "applications": results
    }


