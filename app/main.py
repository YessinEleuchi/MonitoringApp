from fastapi import FastAPI
from app.core.database import Base, engine
from app.core.scheduler import lifespan
from app.routers import endpoints, logs, stats, test

app = FastAPI(title="Application de Monitoring", lifespan=lifespan)

Base.metadata.create_all(bind=engine)

app.include_router(endpoints.router)
app.include_router(logs.router, prefix="/logs")
app.include_router(stats.router, prefix="/stats")
app.include_router(test.router, prefix="/test")