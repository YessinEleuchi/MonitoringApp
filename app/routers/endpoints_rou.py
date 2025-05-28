from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.endpoint_sch import EndpointCreate, EndpointUpdate, EndpointOut, EndpointConfig
from app.models.endpoint import Endpoint
from app.services import tester
from typing import List
from app.models.application import Application
from traceback import print_exc
from app.schemas.result import EndpointResult
from fastapi import status

router = APIRouter(prefix="/endpoints", tags=["Endpoints"])

# 🔹 Ajouter un endpoint lié à une application
@router.post("/", response_model=EndpointOut)
def create_endpoint(config: EndpointCreate, db: Session = Depends(get_db)):
    try:
        payload = config.dict()

        # ✅ conversion des Enum en str
        payload["method"] = config.method.value
        payload["body_format"] = config.body_format.value
        payload["response_format"] = config.response_format.value

        # ✅ conversion URL AnyHttpUrl → str
        payload["url"] = str(config.url)

        endpoint = Endpoint(**payload)
        db.add(endpoint)
        db.commit()
        db.refresh(endpoint)
        return endpoint

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")

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
        application_id=endpoint.application_id
    )

    try:
        result = await tester.test_endpoint(config, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur pendant test_endpoint : {str(e)}")

