"""Settings (Einstellungen) Model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.datetime_utils import get_utc_timestamp, get_local_date


class Setting(Base):
    """
    Repräsentiert Einstellungen für ein Event (Organisation, Bankdaten, etc.)
    """
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)

    # Organisation
    organization_name = Column(String(200), nullable=False, default="Freizeit-Kassen-System")
    organization_address = Column(Text, nullable=True, default="Musterstraße 123\n12345 Musterstadt")

    # Bankdaten
    bank_account_holder = Column(String(200), nullable=False, default="Freizeit-Kassen-System")
    bank_iban = Column(String(34), nullable=False, default="DE89 3704 0044 0532 0130 00")
    bank_bic = Column(String(11), nullable=True, default="COBADEFFXXX")

    # Rechnungs-Einstellungen
    invoice_subject_prefix = Column(String(100), nullable=True, default="Teilnahme an")
    invoice_footer_text = Column(Text, nullable=True, default="Vielen Dank für Ihre Zahlung!")

    # Regelwerk-Einstellungen
    default_github_repo = Column(String(500), nullable=True, default=None)

    # Timestamps
    created_at = Column(DateTime, default=get_utc_timestamp, nullable=False)
    updated_at = Column(DateTime, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    # Beziehungen
    event = relationship("Event", back_populates="settings")

    def __repr__(self):
        return f"<Setting for Event {self.event_id}>"
