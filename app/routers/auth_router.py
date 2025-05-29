# app/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.application import Application
from app.services.auth_service import AuthService

router = APIRouter(prefix="/applications", tags=["Auth"])

@router.post("/{app_id}/login")
async def login_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application non trouvée")
    
    try:
        token = await AuthService.get_jwt_token(app, force_refresh=True)
        return {"token": token, "message": "Token généré et mis en cache"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'authentification : {str(e)}")
