"""Payment (Zahlung) Model"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.database import Base


class Payment(Base):
    """
    Repräsentiert eine Zahlung von einem Teilnehmer oder einer Familie
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, default=date.today, nullable=False)
    payment_method = Column(String(50), nullable=True)  # z.B. "Bar", "Überweisung", "PayPal"
    reference = Column(String(200), nullable=True)  # Referenznummer, Verwendungszweck
    notes = Column(Text, nullable=True)

    # Foreign Keys
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Beziehungen
    participant = relationship("Participant", back_populates="payments")
    family = relationship("Family", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.amount}€ on {self.payment_date}>"
