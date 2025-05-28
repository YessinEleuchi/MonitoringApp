from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Endpoint(Base):
    __tablename__ = "endpoints"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    headers = Column(JSON, nullable=True)
    body = Column(JSON, nullable=True)
    body_format = Column(String(10), default="JSON")
    auth_type = Column(String(10), default="none")
    jwt_token = Column(String(500), nullable=True)
    auth_url = Column(String(255), nullable=True)
    auth_credentials = Column(JSON, nullable=True)
    expected_status = Column(Integer, default=200)
    response_format = Column(String(10), default="JSON")
    response_conditions = Column(JSON, nullable=True)

    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    application = relationship("Application", back_populates="endpoints")
    monitoring_results = relationship("MonitoringResult", back_populates="endpoint")
