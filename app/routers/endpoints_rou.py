from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.endpoint_sch import EndpointCreate, EndpointUpdate, EndpointOut, EndpointConfig
from app.models.endpoint import Endpoint
from app.services import tester
from typing import List
from app.models.application import Application

router = APIRouter(prefix="/endpoints", tags=["Endpoints"])

# 🔹 Ajouter un endpoint (sans test)
# 🔹 Ajouter un endpoint lié à une application
@router.post("/", response_model=EndpointConfig)
def create_endpoint(config: EndpointCreate, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == config.application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    endpoint = Endpoint(
        url=config.url,
        method=config.method,
        headers=config.headers,
        body=config.body,
        auth_type=config.auth_type,
        jwt_token=config.jwt_token,
        auth_url=config.auth_url,
        auth_credentials=config.auth_credentials,
        expected_status=config.expected_status,
        response_format=config.response_format,
        response_conditions=config.response_conditions,
        application_id=config.application_id
    )

    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)

    return endpoint

# 🔹 Lister tous les endpoints
@router.get("/", response_model=List[EndpointOut])
def list_endpoints(db: Session = Depends(get_db)):
    return db.query(Endpoint).all()

# 🔹 Obtenir un endpoint par ID
@router.get("/{endpoint_id}", response_model=EndpointOut)
def get_endpoint(endpoint_id: int, db: Session = Depends(get_db)):
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return endpoint

# 🔹 Modifier un endpoint
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

# 🔹 Supprimer un endpoint
@router.delete("/{endpoint_id}")
def delete_endpoint(endpoint_id: int, db: Session = Depends(get_db)):
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    db.delete(endpoint)
    db.commit()
    return {"message": "Endpoint deleted successfully"}

# 🔹 Tester un endpoint existant (manuel)
@router.post("/{endpoint_id}/test", response_model=EndpointConfig)
async def test_existing_endpoint(endpoint_id: int, db: Session = Depends(get_db)):
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    config = EndpointConfig(
        url=endpoint.url,
        method=endpoint.method,
        headers=None,
        body=None,
        auth_type=endpoint.auth_type,
        jwt_token=endpoint.jwt_token,
        auth_url=endpoint.auth_url,
        auth_credentials=endpoint.auth_credentials,
        expected_status=endpoint.expected_status,
        response_format=endpoint.response_format,
        response_conditions=endpoint.response_conditions
    )
    result = await tester.test_endpoint(config, db)
    return result
# 🔹 Tester un endpoint avec configuration personnalisée
@router.post("/test", response_model=EndpointConfig)
async def test_custom_endpoint(config: EndpointConfig, db: Session = Depends(get_db)):
    result = await tester.test_endpoint(config, db)
    return result