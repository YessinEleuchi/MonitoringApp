# app/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user_sch import UserCreate, UserLogin, UserOut
from app.models.user import User
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    user_obj = User(
        username=user.username,
        email=user.email,
        password_hash=auth_service.hash_password(user.password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.email == form_data.username).first()
    if not user_db or not auth_service.verify_password(form_data.password, user_db.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    token = auth_service.create_access_token({"sub": user_db.email})
    return {"access_token": token, "token_type": "bearer"}

