# app/routers/email_subscription.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.email_sub_sch import EmailSubscriptionCreate
from app.models.email_subscription import EmailSubscription
from app.models.user import User
from app.dependencies.auth import get_current_user  # ✅ JWT token

router = APIRouter(prefix="/notifications", tags=["Email Notifications"])

@router.post("/subscribe")
def subscribe_to_notifications(data: EmailSubscriptionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Vérifier si l'email est déjà utilisé
    existing = db.query(EmailSubscription).filter_by(email=data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà abonné")

    subscription = EmailSubscription(user_id=user.id, email=data.email)
    db.add(subscription)
    db.commit()
    return {"message": "Abonnement aux notifications réussi"}
