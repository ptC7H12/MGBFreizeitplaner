"""Participant (Teilnehmer) Model"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship

from app.database import Base


class Participant(Base):
    """
    Repräsentiert einen Teilnehmer an einer Freizeit
    """
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)

    # Persönliche Daten
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False, index=True)
    birth_date = Column(Date, nullable=False)
    gender = Column(String(20), nullable=True)  # "männlich", "weiblich"

    # Kontaktdaten
    email = Column(String(200), nullable=True, index=True)  # Index für Suche
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)

    # Zusätzliche Eigenschaften
    bildung_teilhabe_id = Column(String(100), nullable=True)  # Bildung & Teilhabe Nummer
    allergies = Column(Text, nullable=True)
    medical_notes = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Preis und Rabatte
    calculated_price = Column(Float, default=0.0, nullable=False)  # Berechneter Preis
    manual_price_override = Column(Float, nullable=True)  # Manuell überschriebener Preis
    discount_percent = Column(Float, default=0.0, nullable=False)  # Zusätzlicher Rabatt in %
    discount_reason = Column(String(200), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)  # Index für Filter
    registration_date = Column(Date, default=date.today, nullable=False)
    deleted_at = Column(DateTime, nullable=True, index=True)  # Index für Soft-Delete Queries

    # Foreign Keys
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Beziehungen
    event = relationship("Event", back_populates="participants")
    role = relationship("Role", back_populates="participants")
    family = relationship("Family", back_populates="participants")
    payments = relationship("Payment", back_populates="participant", cascade="all, delete-orphan")

    @property
    def full_name(self):
        """Vollständiger Name des Teilnehmers"""
        return f"{self.first_name} {self.last_name}"

    @property
    def age_at_event(self):
        """Berechnet das Alter des Teilnehmers zum Zeitpunkt des Events"""
        if not self.event or not self.birth_date:
            return None
        event_start = self.event.start_date
        age = event_start.year - self.birth_date.year
        # Geburtstag noch nicht erreicht?
        if (event_start.month, event_start.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    @property
    def final_price(self):
        """Endgültiger Preis (manuell oder berechnet)"""
        return self.manual_price_override if self.manual_price_override is not None else self.calculated_price

    def __repr__(self):
        return f"<Participant {self.full_name}>"
