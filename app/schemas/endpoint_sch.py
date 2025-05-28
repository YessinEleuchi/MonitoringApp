from pydantic import BaseModel, AnyHttpUrl
from typing import Optional, Dict, List, Union
from app.schemas.enums import HttpMethod, ResponseFormat

# 🔹 Condition de réponse attendue
class ResponseCondition(BaseModel):
    field: str
    condition: str  # "equals", "not_null", "contains"
    value: Optional[Union[str, int, float, bool]] = None

# 🔹 Schéma de base commun
class EndpointBase(BaseModel):
    url: AnyHttpUrl
    method: HttpMethod
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict] = None
    body_format: Optional[ResponseFormat] = ResponseFormat.JSON
    expected_status: int = 200
    response_format: ResponseFormat = ResponseFormat.JSON
    response_conditions: Optional[List[ResponseCondition]] = []

# 🔹 Création d’un endpoint
class EndpointCreate(EndpointBase):
    application_id: int

# 🔹 Mise à jour d’un endpoint
class EndpointUpdate(EndpointBase):
    pass

# 🔹 Réponse d’un endpoint (GET)
class EndpointOut(EndpointBase):
    id: int
    application_id: int

    class Config:
        from_attributes = True  # ✅ Pydantic v2

# 🔹 Configuration de test d’un endpoint
class EndpointConfig(EndpointBase):
    application_id: int
