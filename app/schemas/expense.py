"""Pydantic Schemas für Expense"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class ExpenseBase(BaseModel):
    """Basis-Schema für Ausgaben"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    amount: float = Field(..., gt=0)
    expense_date: date
    category: Optional[str] = Field(None, max_length=100)
    receipt_number: Optional[str] = Field(None, max_length=100)
    paid_by: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    event_id: int


class ExpenseCreate(ExpenseBase):
    """Schema für das Erstellen einer Ausgabe"""
    pass


class ExpenseResponse(ExpenseBase):
    """Schema für die Antwort"""
    id: int

    class Config:
        from_attributes = True
