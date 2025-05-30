from sqlalchemy import func
from app.models.application_stats import ApplicationStats
from app.models.monitoring_result import MonitoringResult
from app.models.endpoint import Endpoint

def update_application_stats(application_id: int, db):
    total_tests = db.query(MonitoringResult).join(Endpoint).filter(
        Endpoint.application_id == application_id
    ).count()

    if total_tests == 0:
        return

    successful_tests = db.query(MonitoringResult).join(Endpoint).filter(
        Endpoint.application_id == application_id,
        MonitoringResult.success == True
    ).count()

    average_response_time = db.query(func.avg(MonitoringResult.response_time)).join(Endpoint).filter(
        Endpoint.application_id == application_id
    ).scalar()

    stats = db.query(ApplicationStats).filter(ApplicationStats.application_id == application_id).first()
    if not stats:
        stats = ApplicationStats(application_id=application_id)

    stats.success_rate = round((successful_tests / total_tests) * 100, 2)
    stats.avg_response_time = round(average_response_time or 0.0, 2)
    stats.last_updated = func.now()

    db.add(stats)
    db.commit()
