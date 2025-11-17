"""Pydantic Schemas für Family"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class FamilyBase(BaseModel):
    """Basis-Schema für Familien"""
    name: str = Field(..., min_length=1, max_length=200)
    contact_person: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('email', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Konvertiert leere Strings zu None"""
        if v == '' or (isinstance(v, str) and v.strip() == ''):
            return None
        return v


class FamilyCreate(FamilyBase):
    """Schema für das Erstellen einer Familie"""
    pass


class FamilyUpdate(BaseModel):
    """Schema für das Aktualisieren einer Familie"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    contact_person: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('email', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Konvertiert leere Strings zu None"""
        if v == '' or (isinstance(v, str) and v.strip() == ''):
            return None
        return v


class FamilyResponse(FamilyBase):
    """Schema für die Antwort"""
    id: int

    class Config:
        from_attributes = True
