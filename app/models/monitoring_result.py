from sqlalchemy import Column, Integer, Float, Boolean, DateTime, JSON, ForeignKey , String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class MonitoringResult(Base):
    __tablename__ = "monitoring"
    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id"), nullable=False)
    timestamp = Column(DateTime, default=func.now())
    status_code = Column(Integer, nullable=False)
    response_time = Column(Float, nullable=False)
    success = Column(Boolean, nullable=False)
    response_content = Column(JSON)
    error_message = Column(String(255))
    endpoint = relationship("Endpoint", back_populates="monitoring_results")