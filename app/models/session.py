# app/models/session.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)  # optional, can auto-generate
    status = Column(String, default="active")  # active / completed / archived

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    messages = relationship("Message", back_populates="session", cascade="all, delete")
