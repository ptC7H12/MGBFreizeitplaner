"""Income Model für zusätzliche Einnahmen (z.B. Zuschüsse)"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Income(Base):
    """Model für Einnahmen wie Zuschüsse, Spenden, etc."""
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)

    # Optional: Verknüpfung mit Rolle (z.B. "50% Zuschuss für alle Kinder")
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True, index=True)

    # Relationships
    event = relationship("Event", back_populates="incomes")
    role = relationship("Role", back_populates="incomes")
