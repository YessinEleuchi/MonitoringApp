from pydantic import BaseModel, AnyHttpUrl
from typing import Optional, Dict, List, Union
from app.schemas.enums import HttpMethod, ResponseFormat

class ResponseCondition(BaseModel):
    field: str
    condition: str
    value: Optional[Union[str, int, float, bool]] = None

class EndpointConfig(BaseModel):
    url: AnyHttpUrl
    method: HttpMethod
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict] = None
    body_format: Optional[ResponseFormat] = ResponseFormat.JSON
    auth_type: Optional[str] = None
    jwt_token: Optional[str] = None
    auth_url: Optional[AnyHttpUrl] = None
    auth_credentials: Optional[Dict[str, str]] = None
    expected_status: int = 200
    response_format: ResponseFormat = ResponseFormat.JSON
    response_conditions: Optional[List[ResponseCondition]] = None