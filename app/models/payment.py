"""Payment (Zahlung) Model"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.datetime_utils import get_utc_timestamp, get_local_date


class Payment(Base):
    """
    Repräsentiert eine Zahlung von einem Teilnehmer oder einer Familie
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date, default=get_local_date, nullable=False)
    payment_method = Column(String(50), nullable=True)  # z.B. "Bar", "Überweisung", "PayPal"
    reference = Column(String(200), nullable=True)  # Referenznummer, Verwendungszweck
    notes = Column(Text, nullable=True)

    # Foreign Keys
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=get_utc_timestamp, nullable=False)
    updated_at = Column(DateTime, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    # Beziehungen
    event = relationship("Event", back_populates="payments")
    participant = relationship("Participant", back_populates="payments")
    family = relationship("Family", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.amount}€ on {self.payment_date}>"
