# app/models/application.py

from sqlalchemy import Column, Integer, String, JSON, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.schemas.enums import AppStatusEnum
from sqlalchemy import Enum as SqlEnum



class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    base_url = Column(String(255), nullable=False, unique=True)
    name = Column(String(100), nullable=True)
    description = Column(String(255), nullable=True)  # ✅ nouveau champ
    status = Column(SqlEnum(AppStatusEnum), default=AppStatusEnum.active)

    auth_type = Column(String(10), default="none")
    auth_url = Column(String(255), nullable=True)
    auth_credentials = Column(JSON, nullable=True)

    endpoints = relationship("Endpoint", back_populates="application")
    stats = relationship("ApplicationStats", back_populates="application")
