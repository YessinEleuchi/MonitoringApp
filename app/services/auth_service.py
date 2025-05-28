# app/services/auth_service.py

import httpx
from datetime import datetime, timedelta

class AuthService:
    token_cache = {}  # { app_id: {"token": ..., "expires_at": datetime } }

    @staticmethod
    async def get_jwt_token(application) -> str:
        cache = AuthService.token_cache.get(application.id)
        if cache and cache["expires_at"] > datetime.utcnow():
            return cache["token"]

        if application.auth_type != "jwt":
            return None

        async with httpx.AsyncClient() as client:
            response = await client.post(application.auth_url, json=application.auth_credentials)
            response.raise_for_status()
            data = response.json()
            print("🧾 Réponse Auth complète :", response.json())


            token = data.get("token")
            expires_in = data.get("expires_in", 3300)  # fallback 55min
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            AuthService.token_cache[application.id] = {
                "token": token,
                "expires_at": expires_at
            }
            return token
