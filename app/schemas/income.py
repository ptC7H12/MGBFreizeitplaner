"""Pydantic Schemas für Income"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class IncomeBase(BaseModel):
    """Basis-Schema für Einnahmen"""
    name: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    date: date
    description: Optional[str] = None
    role_id: Optional[int] = None

    @field_validator('role_id', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Konvertiert leere Strings zu None"""
        if v == '' or (isinstance(v, str) and v.strip() == ''):
            return None
        return v


class IncomeCreate(IncomeBase):
    """Schema für das Erstellen einer Einnahme"""
    pass


class IncomeUpdate(BaseModel):
    """Schema für das Aktualisieren einer Einnahme"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[float] = Field(None, gt=0)
    date: Optional[date] = None
    description: Optional[str] = None
    role_id: Optional[int] = None

    @field_validator('role_id', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Konvertiert leere Strings zu None"""
        if v == '' or (isinstance(v, str) and v.strip() == ''):
            return None
        return v


class IncomeResponse(IncomeBase):
    """Schema für die Antwort"""
    id: int

    class Config:
        from_attributes = True
