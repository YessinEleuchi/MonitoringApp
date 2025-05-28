from pydantic import BaseModel
from typing import Optional

class ApplicationCreate(BaseModel):
    base_url: str
    name: Optional[str] = None

class ApplicationOut(ApplicationCreate):
    id: int

    class Config:
        orm_mode = True
