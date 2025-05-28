from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    base_url = Column(String(255), nullable=False, unique=True)
    name = Column(String(100), nullable=True)

    # 🔐 Champs d'authentification
    auth_type = Column(String(10), default="none")  # "jwt", "none", etc.
    auth_url = Column(String(255), nullable=True)  # URL d'authentification JWT
    auth_credentials = Column(JSON, nullable=True)  # { "email": "...", "password": "..." }

    # 🔁 Relations
    endpoints = relationship("Endpoint", back_populates="application")
    stats = relationship("ApplicationStats", back_populates="application")
