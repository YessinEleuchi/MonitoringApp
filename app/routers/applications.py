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
# 🔹 Créer une application
@router.post("/", response_model=ApplicationOut)
def create_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    try:
        payload = data.dict()
        # ✅ Cast URL en str (Pydantic AnyHttpUrl → str)
        if payload.get("auth_url"):
            payload["auth_url"] = str(payload["auth_url"])

        app = Application(**payload)
        db.add(app)
        db.commit()
        db.refresh(app)
        return app
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


# 🔹 Tester tous les endpoints d’une application
@router.post("/{app_id}/test", response_model=List[EndpointConfig])
async def test_application_endpoints(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    results = []
    for ep in app.endpoints:
        config = EndpointConfig(
            url=ep.url,
            method=ep.method,
            headers=ep.headers,
            body=ep.body,
            body_format=ep.body_format,
            expected_status=ep.expected_status,
            response_format=ep.response_format,
            response_conditions=ep.response_conditions,
            application_id=app.id
        )
        result = await tester.test_endpoint(config, db)
        results.append(result)
    return results
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



