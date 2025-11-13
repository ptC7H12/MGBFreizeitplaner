"""Event (Freizeit) Model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Event(Base):
    """
    Repräsentiert eine Freizeit (z.B. Kinderfreizeit 2024, Jugendfreizeit Sommer 2024)
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    event_type = Column(String(50), nullable=False)  # z.B. "kinder", "jugend", "familie"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    location = Column(String(200), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Beziehungen
    participants = relationship("Participant", back_populates="event", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="event", cascade="all, delete-orphan")
    rulesets = relationship("Ruleset", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event {self.name} ({self.event_type})>"
