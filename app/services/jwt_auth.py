import httpx
from fastapi import HTTPException
from typing import Dict
from app.core.logger import logger

async def fetch_jwt_token(auth_url: str, credentials: Dict[str, str]) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(auth_url, json=credentials)
            response.raise_for_status()
            data = response.json()
            return data.get("access_token")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch JWT from {auth_url}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to fetch JWT: {str(e)}")