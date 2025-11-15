"""Expense (Ausgabe) Model"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Expense(Base):
    """
    Repräsentiert eine Ausgabe für die Freizeit (z.B. Material, Transport, Verpflegung)
    """
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    expense_date = Column(Date, default=date.today, nullable=False)
    category = Column(String(100), nullable=True)  # z.B. "Verpflegung", "Material", "Transport"
    receipt_number = Column(String(100), nullable=True)
    paid_by = Column(String(200), nullable=True)  # Wer hat die Ausgabe vorgestreckt (falls zutreffend)
    is_settled = Column(Boolean, default=False, nullable=False)  # Wurde die Ausgabe beglichen/erstattet?
    notes = Column(Text, nullable=True)
    receipt_file_path = Column(String(500), nullable=True)  # Pfad zum hochgeladenen Beleg (PDF/Bild)

    # Foreign Key
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Beziehungen
    event = relationship("Event", back_populates="expenses")

    def __repr__(self):
        return f"<Expense {self.title}: {self.amount}€>"
