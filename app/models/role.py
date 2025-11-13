"""Role (Rolle) Model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Role(Base):
    """
    Repräsentiert eine Rolle (z.B. Kind, Jugendlicher, Betreuer, Küchenpersonal)
    Event-spezifisch: Jedes Event kann eigene Rollen haben
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)  # Technischer Name (lowercase)
    display_name = Column(String(100), nullable=False)  # Deutsche Anzeige
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    color = Column(String(20), default="#6B7280")  # Hex-Farbe für UI

    # Foreign Key
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Beziehungen
    event = relationship("Event", back_populates="roles")
    participants = relationship("Participant", back_populates="role")
    incomes = relationship("Income", back_populates="role")

    def __repr__(self):
        return f"<Role {self.display_name}>"
