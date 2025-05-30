# models/thresholds.py
from sqlalchemy import Column, Integer, Float
from app.core.database import Base

class Thresholds(Base):
    __tablename__ = "thresholds"
    id = Column(Integer, primary_key=True, index=True)
    critical_success_rate = Column(Float, default=0.8)   # ex: 80%
    critical_latency = Column(Float, default=2.0)        # ex: 2s
    test_frequency_minutes = Column(Integer, default=5)  # ex: every 5 minutes
