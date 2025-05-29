from fastapi import FastAPI
from app.core.database import Base, engine
from app.core.scheduler import lifespan
from app.routers import endpoints_rou, logs, stats, test , applications_rou , auth_router

app = FastAPI(title="Application de Monitoring", lifespan=lifespan)

# Création des tables dans la base de données

Base.metadata.create_all(bind=engine)

app.include_router(endpoints_rou.router)
app.include_router(applications_rou.router)
app.include_router(auth_router.router)
app.include_router(logs.router, prefix="/logs")
app.include_router(stats.router, prefix="/stats")
app.include_router(test.router, prefix="/test")