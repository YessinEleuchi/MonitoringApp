from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.application import Application
from app.models.endpoint import Endpoint
from app.schemas.application_sch import ApplicationCreate, ApplicationOut
from app.schemas.endpoint_sch import EndpointConfig
from app.services import tester
from app.dependencies.auth import get_current_user



router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
    dependencies=[Depends(get_current_user)]
)
@router.post("/", response_model=ApplicationOut)
def create_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    # 🔒 Vérifier l'unicité de base_url
    if db.query(Application).filter(Application.base_url == data.base_url).first():
        raise HTTPException(status_code=409, detail="Une application avec cette URL existe déjà.")

    # 🔐 Si auth_type est 'jwt', auth_url et auth_credentials doivent être fournis
    if data.auth_type == "jwt":
        if not data.auth_url or not data.auth_credentials:
            raise HTTPException(
                status_code=400,
                detail="auth_url et auth_credentials sont obligatoires pour l'authentification JWT."
            )

    try:
        payload = data.dict()
        if payload.get("auth_url"):
            payload["auth_url"] = str(payload["auth_url"])  # Pydantic → str

        app = Application(**payload)
        db.add(app)
        db.commit()
        db.refresh(app)
        return app

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Violation d'intégrité des données.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création : {str(e)}")


# 🔹 Liste des applications
@router.get("/", response_model=List[ApplicationOut])
def list_applications(db: Session = Depends(get_db)):
    return db.query(Application).all()

# 🔹 Obtenir une application par ID
@router.get("/{app_id}", response_model=ApplicationOut)
def get_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

    
# 🔹 Supprimer une application
@router.delete("/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(app)
    db.commit()
    return {"message": f"Application {app.name or app.base_url} supprimée avec succès."}
from app.schemas.application_sch import ApplicationUpdate

@router.put("/{app_id}", response_model=ApplicationOut)


def update_application(app_id: int, data: ApplicationUpdate, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(app, field, value)

    db.commit()
    db.refresh(app)
    return app