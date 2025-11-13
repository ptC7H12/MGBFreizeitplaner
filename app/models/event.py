"""Event (Freizeit) Model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
import secrets
import string

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

    # Multi-Tenancy
    code = Column(String(20), unique=True, nullable=False, index=True)  # Eindeutiger Code für Zugriff
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Beziehungen
    participants = relationship("Participant", back_populates="event", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="event", cascade="all, delete-orphan")
    rulesets = relationship("Ruleset", back_populates="event", cascade="all, delete-orphan")
    families = relationship("Family", back_populates="event", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="event", cascade="all, delete-orphan")
    settings = relationship("Setting", back_populates="event", cascade="all, delete-orphan", uselist=False)

    @staticmethod
    def generate_code(length=8):
        """Generiert einen zufälligen alphanumerischen Code"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))

    def __repr__(self):
        return f"<Event {self.name} ({self.code})>"
