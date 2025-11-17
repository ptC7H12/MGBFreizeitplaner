"""Pydantic Schemas für Payment"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class PaymentBase(BaseModel):
    """Basis-Schema für Zahlungen"""
    amount: float = Field(..., gt=0)
    payment_date: date
    payment_method: Optional[str] = Field(None, max_length=50)
    reference: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    participant_id: Optional[int] = None
    family_id: Optional[int] = None

    @field_validator('participant_id', 'family_id', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Konvertiert leere Strings zu None"""
        if v == '' or (isinstance(v, str) and v.strip() == ''):
            return None
        return v


class PaymentCreate(PaymentBase):
    """Schema für das Erstellen einer Zahlung"""
    pass


class PaymentUpdate(BaseModel):
    """Schema für das Aktualisieren einer Zahlung"""
    amount: Optional[float] = Field(None, gt=0)
    payment_date: Optional[date] = None
    payment_method: Optional[str] = Field(None, max_length=50)
    reference: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    participant_id: Optional[int] = None
    family_id: Optional[int] = None

    @field_validator('participant_id', 'family_id', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Konvertiert leere Strings zu None"""
        if v == '' or (isinstance(v, str) and v.strip() == ''):
            return None
        return v


class PaymentResponse(PaymentBase):
    """Schema für die Antwort"""
    id: int

    class Config:
        from_attributes = True
