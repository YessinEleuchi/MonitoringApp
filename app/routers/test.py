from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.endpoint_sch import EndpointConfig
from app.schemas.result import EndpointResult
from app.services.tester import test_endpoint

router = APIRouter(prefix="/test", tags=["Test"])

@router.post("/endpoint", response_model=EndpointResult)
async def test_endpoint_route(config: EndpointConfig, db: Session = Depends(get_db)):
    return await test_endpoint(config, db)