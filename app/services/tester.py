from app.schemas.endpoint_sch import EndpointConfig
from app.schemas.result import EndpointResult
from app.models.application import Application
from app.services.token_service import AuthService
from app.core.logger import logger
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
import httpx
import xml.etree.ElementTree as ET


# 🔍 Vérifie les conditions de contenu
def evaluate_conditions(response_data, conditions):
    for condition in conditions:
        try:
            keys = condition.field.split(".")
            value = response_data
            for key in keys:
                value = value[key] if isinstance(value, dict) else value[int(key.strip("[]"))]
            if condition.condition == "not_null" and value is None:
                return False, f"Field {condition.field} is null"
            elif condition.condition == "equals" and value != condition.value:
                return False, f"Field {condition.field} does not equal {condition.value}"
            elif condition.condition == "contains" and condition.value not in value:
                return False, f"Field {condition.field} does not contain {condition.value}"
        except Exception:
            return False, f"Field {condition.field} not found or invalid"
    return True, ""

# 🔹 Test d’un endpoint
# app/services/tester.py (ou similaire)

async def test_endpoint(config: EndpointConfig, db: Session) -> EndpointResult:
    logger.info(f"Testing endpoint: {config.url}")
    start_time = datetime.now()

    app = db.query(Application).filter(Application.id == config.application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    headers = config.headers or {}
    body = config.body

    # 🔐 Ajouter token JWT si déjà en cache
    if app.auth_type == "jwt":
        cache = AuthService.token_cache.get(app.id)
        if cache and cache["expires_at"] > datetime.utcnow():
            headers["Authorization"] = f"Bearer {cache['token']}"
        else:
            return EndpointResult(
                timestamp=start_time,
                url=str(config.url),
                method=config.method,
                status_code=0,
                response_time=0.0,
                success=False,
                error_message="No valid token found. Please authenticate first using /applications/{id}/login"
            )

    # 🧾 Gérer XML si besoin
    if body and config.body_format.name == "XML":
        import xml.etree.ElementTree as ET
        root = ET.Element("request")
        for key, value in body.items():
            elem = ET.SubElement(root, key)
            elem.text = str(value)
        body = ET.tostring(root, encoding="unicode")

    result = EndpointResult(
        timestamp=start_time,
        url=str(config.url),
        method=config.method,
        status_code=0,
        response_time=0.0,
        success=False
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=config.method,
                url=str(config.url),
                headers=headers,
                json=body if config.body_format.name == "JSON" else None,
                content=body if config.body_format.name == "XML" else None
            )
            result.status_code = response.status_code
            result.response_time = (datetime.now() - start_time).total_seconds()

            if response.status_code == config.expected_status:
                content = response.json() if config.response_format.name == "JSON" else {}
                result.response_content = content
                if config.response_conditions:
                    success, error = evaluate_conditions(content, config.response_conditions)
                    result.success = success
                    result.error_message = error
                else:
                    result.success = True
            else:
                result.error_message = f"Unexpected status code: {response.status_code}"
    except Exception as e:
        result.error_message = f"Request failed: {str(e)}"

    return result

