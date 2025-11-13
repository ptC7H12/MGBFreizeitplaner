"""Role (Rolle) Model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Role(Base):
    """
    Repräsentiert eine Rolle (z.B. Kind, Jugendlicher, Betreuer, Küchenpersonal)
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(100), nullable=False)  # Deutsche Anzeige
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    color = Column(String(20), default="#6B7280")  # Hex-Farbe für UI

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Beziehungen
    participants = relationship("Participant", back_populates="role")

    def __repr__(self):
        return f"<Role {self.display_name}>"
