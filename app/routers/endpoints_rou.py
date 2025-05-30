from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.endpoint_sch import EndpointCreate, EndpointUpdate, EndpointOut, EndpointConfig
from app.models.endpoint import Endpoint
from app.services import tester
from typing import List
from app.models.monitoring_result import MonitoringResult
from app.schemas.result import EndpointResult
from app.services.stats import update_application_stats
from app.dependencies.auth import get_current_user
from app.models.thresholds import Thresholds
from app.models.email_subscription import EmailSubscription
from app.services.email_service import EmailService
from app.models.user import User
import asyncio

router = APIRouter(
    prefix="/endpoints",
    tags=["Endpoints"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=EndpointOut)
def create_endpoint(config: EndpointCreate, db: Session = Depends(get_db)):
    try:
        payload = config.dict()
        payload["method"] = config.method.value
        payload["body_format"] = config.body_format.value
        payload["response_format"] = config.response_format.value
        payload["url"] = str(config.url)

        endpoint = Endpoint(**payload)
        db.add(endpoint)
        db.commit()
        db.refresh(endpoint)
        return endpoint

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")

@router.get("/", response_model=List[EndpointOut])
def list_endpoints(db: Session = Depends(get_db)):
    return db.query(Endpoint).all()

@router.get("/{endpoint_id}", response_model=EndpointOut)
def get_endpoint(endpoint_id: int, db: Session = Depends(get_db)):
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return endpoint

@router.put("/{endpoint_id}", response_model=EndpointOut)
def update_endpoint(endpoint_id: int, data: EndpointUpdate, db: Session = Depends(get_db)):
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(endpoint, field, value)
    db.commit()
    db.refresh(endpoint)
    return endpoint

@router.delete("/{endpoint_id}")
def delete_endpoint(endpoint_id: int, db: Session = Depends(get_db)):
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    db.delete(endpoint)
    db.commit()
    return {"message": "Endpoint deleted successfully"}

@router.post("/{endpoint_id}/test", response_model=EndpointResult)
async def test_existing_endpoint(endpoint_id: int, db: Session = Depends(get_db)):
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    config = EndpointConfig(
        url=endpoint.url,
        method=endpoint.method,
        headers=endpoint.headers,
        body=endpoint.body,
        body_format=endpoint.body_format,
        expected_status=endpoint.expected_status,
        response_format=endpoint.response_format,
        response_conditions=endpoint.response_conditions,
        application_id=endpoint.application_id,
        use_auth=endpoint.use_auth
    )

    try:
        result = await tester.test_endpoint(config, db)

        MAX_LINES = 50
        if isinstance(result.response_content, dict):
            for key, value in result.response_content.items():
                if isinstance(value, list) and len(value) > MAX_LINES:
                    result.response_content[key] = value[:MAX_LINES]

        monitoring = MonitoringResult(
            endpoint_id=endpoint.id,
            timestamp=result.timestamp,
            status_code=result.status_code,
            response_time=result.response_time,
            success=result.success,
            response_content=result.response_content,
            error_message=result.error_message
        )
        db.add(monitoring)
        db.commit()

        update_application_stats(application_id=endpoint.application_id, db=db)

        thresholds = db.query(Thresholds).first()
        if thresholds:
            seuil_latence = thresholds.critical_latency
            seuil_succes = thresholds.critical_success_rate / 100

            anomalie = (result.response_time > seuil_latence) or (not result.success)
            if anomalie:
                subscriptions = db.query(EmailSubscription).filter(
                    EmailSubscription.user_id == endpoint.application_id
                ).all()

                for sub in subscriptions:
                    subject = f"🚨 Anomalie détectée sur {endpoint.url}"
                    html = (
                        f"<p><strong>📅 Date :</strong> {result.timestamp}<br>"
                        f"<strong>🔗 URL :</strong> {endpoint.url}<br>"
                        f"<strong>⏱ Temps :</strong> {result.response_time:.2f}s<br>"
                        f"<strong>✅ Succès :</strong> {'Oui' if result.success else 'Non'}</p>"
                    )
                    email_service = EmailService()
                    await asyncio.to_thread(
                    email_service.send_email,
                    to_email=sub.email,
                    subject=subject,
                    html_content=html
)

        return result

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur pendant test_endpoint : {str(e)}")
