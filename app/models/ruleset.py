"""Ruleset (Regelwerk) Model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.datetime_utils import get_utc_timestamp, get_local_date


class Ruleset(Base):
    """
    Repräsentiert ein Regelwerk für Preisberechnungen
    """
    __tablename__ = "rulesets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    ruleset_type = Column(String(50), nullable=False)  # z.B. "kinder", "jugend", "familie"
    description = Column(Text, nullable=True)

    # Gültigkeitszeitraum
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=False)

    # Regelwerk-Daten (als JSON gespeichert)
    age_groups = Column(JSON, nullable=False)  # Liste von Altersgruppen mit Preisen
    role_discounts = Column(JSON, nullable=True)  # Rabatte nach Rollen
    family_discount = Column(JSON, nullable=True)  # Familienrabatt-Konfiguration

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Source
    source_file = Column(String(500), nullable=True)  # Pfad zur Original-YAML-Datei

    # Foreign Key
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=get_utc_timestamp, nullable=False)
    updated_at = Column(DateTime, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    # Beziehungen
    event = relationship("Event", back_populates="rulesets")

    def __repr__(self):
        return f"<Ruleset {self.name}>"
