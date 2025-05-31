# app/schemas/application_sch.py

from pydantic import BaseModel, AnyHttpUrl
from typing import Optional, Dict, Literal
from app.schemas.enums import AppStatusEnum

class ApplicationCreate(BaseModel):
    base_url: str
    name: Optional[str] = None
    description: Optional[str] = None  
    status: Optional[AppStatusEnum] = AppStatusEnum.active
    auth_type: Optional[str] = None
    auth_url: Optional[AnyHttpUrl] = None
    auth_credentials: Optional[Dict[str, str]] = None

class ApplicationUpdate(BaseModel):
    base_url: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None  
    status: Optional[Literal["active", "inactive", "maintenance"]] = None  
    auth_type: Optional[str] = None
    auth_url: Optional[AnyHttpUrl] = None
    auth_credentials: Optional[Dict[str, str]] = None

class ApplicationOut(ApplicationCreate):
    id: int

    class Config:
        from_attributes = True
        use_enum_values = True  # ✅ ici !

