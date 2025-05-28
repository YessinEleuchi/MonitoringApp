from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class EndpointResult(BaseModel):
    timestamp: datetime
    url: str
    method: str
    status_code: int
    response_time: float
    success: bool
    response_content: Optional[Dict] = None
    error_message: Optional[str] = None