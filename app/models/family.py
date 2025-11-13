"""Family (Familie) Model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Family(Base):
    """
    Repräsentiert eine Familie mit mehreren Teilnehmern
    """
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)  # z.B. "Familie Müller"
    contact_person = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Beziehungen
    participants = relationship("Participant", back_populates="family")
    payments = relationship("Payment", back_populates="family", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Family {self.name}>"
