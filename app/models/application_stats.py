from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class ApplicationStats(Base):
    __tablename__ = "application_stats"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    success_rate = Column(Float)
    avg_response_time = Column(Float)
    last_updated = Column(DateTime, default=func.now())
    application = relationship("Application", back_populates="stats")