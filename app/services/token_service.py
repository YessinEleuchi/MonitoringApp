# app/services/auth_service.py
import httpx
from datetime import datetime, timedelta

class AuthService:
    token_cache = {}  # { app_id: {"token": ..., "expires_at": datetime } }

    @staticmethod
    async def get_jwt_token(application, force_refresh=False) -> str:
        cache = AuthService.token_cache.get(application.id)
        if not force_refresh and cache and cache["expires_at"] > datetime.utcnow():
            return cache["token"]

        if application.auth_type != "jwt":
            return None

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(application.auth_url, json=application.auth_credentials)
            response.raise_for_status()
            data = response.json()

            print("🧾 Réponse Auth complète :", data)

            token = data.get("access_token") or data.get("token")
            if not token:
                raise ValueError("Token non trouvé dans la réponse")

            expires_in = data.get("expires_in", 3300)
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            AuthService.token_cache[application.id] = {
                "token": token,
                "expires_at": expires_at
            }
            return token
