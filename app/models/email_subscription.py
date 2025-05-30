# app/models/email_subscription.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class EmailSubscription(Base):
    __tablename__ = "email_subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String(120), nullable=False, unique=True)

user = relationship("User", back_populates="subscription")
