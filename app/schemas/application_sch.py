from pydantic import BaseModel, AnyHttpUrl
from typing import Optional, Dict

class ApplicationCreate(BaseModel):
    base_url: str
    name: Optional[str] = None
    auth_type: Optional[str] = None
    auth_url: Optional[AnyHttpUrl] = None
    auth_credentials: Optional[Dict[str, str]] = None

class ApplicationUpdate(BaseModel):
    base_url: Optional[str] = None
    name: Optional[str] = None
    auth_type: Optional[str] = None
    auth_url: Optional[AnyHttpUrl] = None
    auth_credentials: Optional[Dict[str, str]] = None

class ApplicationOut(ApplicationCreate):
    id: int

    class Config:
        from_attributes = True  # ✅ Pour Pydantic v2
