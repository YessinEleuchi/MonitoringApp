from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Endpoint(Base):
    __tablename__ = "endpoints"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    auth_type = Column(String(10))
    jwt_token = Column(String(500))
    auth_url = Column(String(255))
    auth_credentials = Column(JSON)
    expected_status = Column(Integer, default=200)
    response_format = Column(String(10), default="JSON")
    response_conditions = Column(JSON)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    application = relationship("Application", back_populates="endpoints")
    monitoring_results = relationship("MonitoringResult", back_populates="endpoint")