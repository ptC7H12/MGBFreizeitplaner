"""Family (Familie) Model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.datetime_utils import get_utc_timestamp, get_local_date


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

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)  # Index für Filter
    deleted_at = Column(DateTime, nullable=True, index=True)  # Index für Soft-Delete Queries

    # Foreign Key
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=get_utc_timestamp, nullable=False)
    updated_at = Column(DateTime, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    # Beziehungen
    event = relationship("Event", back_populates="families")
    participants = relationship("Participant", back_populates="family")
    payments = relationship("Payment", back_populates="family", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Family {self.name}>"
