from app.schemas.endpoint import EndpointConfig, ResponseCondition
from app.schemas.result import EndpointResult
from app.models.application import Application
from app.models.endpoint import Endpoint
from app.models.monitoring_result import MonitoringResult
from app.models.application_stats import ApplicationStats
from app.services.jwt_auth import fetch_jwt_token
from app.core.logger import logger
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from urllib.parse import urlparse
import httpx
import xml.etree.ElementTree as ET

# Évaluer les conditions de réponse

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

# Test un endpoint
async def test_endpoint(config: EndpointConfig, db: Session) -> EndpointResult:
    logger.info(f"Testing endpoint: {config.url}")
    start_time = datetime.now()
    headers = config.headers or {}
    body = config.body
    result = EndpointResult(
        timestamp=start_time,
        url=str(config.url),
        method=config.method,
        status_code=0,
        response_time=0.0,
        success=False
    )

    if config.auth_type == "jwt":
        if config.jwt_token:
            headers["Authorization"] = f"Bearer {config.jwt_token}"
        elif config.auth_url and config.auth_credentials:
            try:
                token = await fetch_jwt_token(str(config.auth_url), config.auth_credentials)
                headers["Authorization"] = f"Bearer {token}"
            except HTTPException as e:
                result.error_message = str(e.detail)
                return result

    if body and config.body_format.name == "XML":
        root = ET.Element("request")
        for key, value in body.items():
            elem = ET.SubElement(root, key)
            elem.text = str(value)
        body = ET.tostring(root, encoding="unicode")

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

async def test_all_endpoints():
    db = SessionLocal()
    try:
        applications = db.query(Application).all()
        for app in applications:
            endpoints = db.query(Endpoint).filter(Endpoint.application_id == app.id).all()
            for db_endpoint in endpoints:
                try:
                    config = EndpointConfig(
                        url=db_endpoint.url,
                        method=db_endpoint.method,
                        auth_type=db_endpoint.auth_type,
                        jwt_token=db_endpoint.jwt_token,
                        auth_url=db_endpoint.auth_url,
                        auth_credentials=db_endpoint.auth_credentials,
                        expected_status=db_endpoint.expected_status,
                        response_format=db_endpoint.response_format,
                        response_conditions=db_endpoint.response_conditions
                    )
                    result = await test_endpoint(config, db)
                    logger.info(f"Tested {config.url}: Success={result.success}")
                except Exception as e:
                    logger.error(f"Failed to test endpoint {db_endpoint.url}: {str(e)}")
                    continue  # Passe à l'endpoint suivant en cas d'erreur

            all_results = []
            for endpoint in endpoints:
                results = db.query(MonitoringResult).filter(MonitoringResult.endpoint_id == endpoint.id).all()
                all_results.extend(results)
            if all_results:
                success_count = sum(1 for r in all_results if r.success)
                total = len(all_results)
                avg_time = sum(r.response_time for r in all_results) / total if total > 0 else 0
                app_stats = db.query(ApplicationStats).filter(ApplicationStats.application_id == app.id).first()
                if app_stats:
                    app_stats.success_rate = (success_count / total) * 100
                    app_stats.avg_response_time = avg_time
                    app_stats.last_updated = func.now()
                else:
                    app_stats = ApplicationStats(application_id=app.id, success_rate=(success_count / total) * 100, avg_response_time=avg_time)
                    db.add(app_stats)
                db.commit()
                logger.info(f"Updated stats for {app.base_url}: Success rate {app_stats.success_rate}%, Avg time {app_stats.avg_response_time}s")
    except Exception as e:
        logger.error(f"Error in test_all_endpoints: {str(e)}")
    finally:
        db.close()
