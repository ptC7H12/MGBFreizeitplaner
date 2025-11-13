"""Pydantic Schemas für Payment"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    """Basis-Schema für Zahlungen"""
    amount: float = Field(..., gt=0)
    payment_date: date
    payment_method: Optional[str] = Field(None, max_length=50)
    reference: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    participant_id: Optional[int] = None
    family_id: Optional[int] = None


class PaymentCreate(PaymentBase):
    """Schema für das Erstellen einer Zahlung"""
    pass


class PaymentResponse(PaymentBase):
    """Schema für die Antwort"""
    id: int

    class Config:
        from_attributes = True
