from core.database import Base, engine
from models.application import Application
from models.endpoint import Endpoint
from models.monitoring_result import MonitoringResult
from models.application_stats import ApplicationStats

# Création des tables
Base.metadata.create_all(bind=engine)
print("✅ Tables créées avec succès.")