"""Task (Aufgabe) Model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.datetime_utils import get_utc_timestamp, get_local_date


class Task(Base):
    """
    Repräsentiert eine erledigte Aufgabe im System.
    Wird verwendet, um offene Aufgaben als "erledigt" zu markieren.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    # Art der Aufgabe (z.B. "bildung_teilhabe", "payment_overdue", etc.)
    task_type = Column(String(100), nullable=False, index=True)

    # Referenz-ID (z.B. participant_id, payment_id, expense_id)
    reference_id = Column(Integer, nullable=False, index=True)

    # Status
    is_completed = Column(Boolean, default=True, nullable=False)

    # Optionale Notiz zur Erledigung
    completion_note = Column(String(500), nullable=True)

    # Foreign Key
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)

    # Timestamps
    completed_at = Column(DateTime, default=get_utc_timestamp, nullable=False)
    created_at = Column(DateTime, default=get_utc_timestamp, nullable=False)

    # Beziehungen
    event = relationship("Event", back_populates="tasks")

    def __repr__(self):
        return f"<Task {self.task_type} for {self.reference_id}>"
