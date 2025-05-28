from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.endpoint import EndpointConfig
from app.services import tester
from app.models.endpoint import Endpoint

router = APIRouter(prefix="/endpoints", tags=["Endpoints"])

@router.post("/", response_model=EndpointConfig)
async def add_endpoint(config: EndpointConfig, db: Session = Depends(get_db)):
    return await tester.test_endpoint(config, db)

@router.get("/", response_model=list[EndpointConfig])
async def list_endpoints(db: Session = Depends(get_db)):
    db_endpoints = db.query(Endpoint).all()
    return [EndpointConfig(
        url=ep.url,
        method=ep.method,
        auth_type=ep.auth_type,
        jwt_token=ep.jwt_token,
        auth_url=ep.auth_url,
        auth_credentials=ep.auth_credentials,
        expected_status=ep.expected_status,
        response_format=ep.response_format,
        response_conditions=ep.response_conditions
    ) for ep in db_endpoints]