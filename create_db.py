from app.core.database import Base, engine
from app.models.application import Application
from app.models.endpoint import Endpoint
from app.models.monitoring_result import MonitoringResult
from app.models.application_stats import ApplicationStats
from app.models.user import User  
from app.models.thresholds import Thresholds


# Création des tables
Base.metadata.create_all(bind=engine)
print("✅ Tables créées avec succès.")
print("📦 Tables détectées :", Base.metadata.tables.keys())
