# app/models/message.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    sender = Column(String, nullable=False)   # "user", "assistant", "agent:planner", etc.
    content = Column(String, nullable=False)
    meta = Column(JSON, nullable=True)  # tool calls, step details, etc.

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    session = relationship("Session", back_populates="messages")
