"""Pydantic Schemas für Participant"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class ParticipantBase(BaseModel):
    """Basis-Schema für Teilnehmer"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    birth_date: date
    gender: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    bildung_teilhabe_id: Optional[str] = Field(None, max_length=100)
    allergies: Optional[str] = None
    medical_notes: Optional[str] = None
    notes: Optional[str] = None
    discount_percent: float = Field(0.0, ge=0, le=100)
    discount_reason: Optional[str] = Field(None, max_length=200)
    manual_price_override: Optional[float] = Field(None, ge=0)
    event_id: int
    role_id: Optional[int] = None
    family_id: Optional[int] = None


class ParticipantCreate(ParticipantBase):
    """Schema für das Erstellen eines Teilnehmers"""
    pass


class ParticipantUpdate(BaseModel):
    """Schema für das Aktualisieren eines Teilnehmers"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    birth_date: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    bildung_teilhabe_id: Optional[str] = Field(None, max_length=100)
    allergies: Optional[str] = None
    medical_notes: Optional[str] = None
    notes: Optional[str] = None
    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    discount_reason: Optional[str] = Field(None, max_length=200)
    manual_price_override: Optional[float] = Field(None, ge=0)
    event_id: Optional[int] = None
    role_id: Optional[int] = None
    family_id: Optional[int] = None


class ParticipantResponse(ParticipantBase):
    """Schema für die Antwort"""
    id: int
    calculated_price: float
    is_active: bool
    registration_date: date

    class Config:
        from_attributes = True
