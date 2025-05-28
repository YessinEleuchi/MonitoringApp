from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.application import Application
from app.models.endpoint import Endpoint
from app.schemas.application_sch import ApplicationCreate, ApplicationOut
from app.schemas.endpoint_sch import EndpointConfig
from app.services import tester

router = APIRouter(prefix="/applications", tags=["Applications"])

# 🔹 Créer une application
@router.post("/", response_model=ApplicationOut)
def create_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    app = Application(**data.dict())
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

# 🔹 Liste des applications
@router.get("/", response_model=List[ApplicationOut])
def list_applications(db: Session = Depends(get_db)):
    return db.query(Application).all()

# 🔹 Tester tous les endpoints d’une application
@router.post("/{app_id}/test", response_model=List[EndpointConfig])
async def test_application_endpoints(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    results = []
    for ep in app.endpoints:
        config = EndpointConfig(
            url=ep.url,
            method=ep.method,
            auth_type=ep.auth_type,
            jwt_token=ep.jwt_token,
            auth_url=ep.auth_url,
            auth_credentials=ep.auth_credentials,
            expected_status=ep.expected_status,
            response_format=ep.response_format,
            response_conditions=ep.response_conditions
        )
        result = await tester.test_endpoint(config, db)
        results.append(result)
    return results
