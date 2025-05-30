from fastapi import FastAPI
from app.core.database import Base, engine
from app.core.scheduler import lifespan
from app.routers import applications, applications_token, endpoints_rou, logs, stats , auth_router , thresholds

app = FastAPI(title="Application de Monitoring", lifespan=lifespan)

# Création des tables dans la base de données
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app.include_router(endpoints_rou.router)
app.include_router(applications.router)
app.include_router(auth_router.router)
app.include_router(thresholds.router)
app.include_router(applications_token.router)
app.include_router(logs.router, prefix="/logs")
app.include_router(stats.router, prefix="/stats")

