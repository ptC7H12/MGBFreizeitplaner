"""Pydantic Schemas für Role"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class RoleBase(BaseModel):
    """Basis-Schema für Role"""
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True
    color: str = Field("#6B7280", max_length=20)
    event_id: int

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validiert den technischen Namen"""
        if not v or not v.strip():
            raise ValueError("Name darf nicht leer sein")
        return v.strip().lower()

    @field_validator('display_name')
    @classmethod
    def validate_display_name(cls, v: str) -> str:
        """Validiert den Anzeigenamen"""
        if not v or not v.strip():
            raise ValueError("Anzeigename darf nicht leer sein")
        return v.strip()

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validiert die Farbe (Hex-Code)"""
        v = v.strip()
        if not v.startswith('#') or len(v) not in [4, 7]:
            raise ValueError("Farbe muss ein gültiger Hex-Code sein (z.B. #6B7280)")
        return v


class RoleCreate(RoleBase):
    """Schema für das Erstellen einer Role"""
    pass


class RoleUpdate(BaseModel):
    """Schema für das Aktualisieren einer Role"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    color: Optional[str] = Field(None, max_length=20)
    event_id: Optional[int] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validiert den technischen Namen"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Name darf nicht leer sein")
        return v.strip().lower() if v else None

    @field_validator('display_name')
    @classmethod
    def validate_display_name(cls, v: Optional[str]) -> Optional[str]:
        """Validiert den Anzeigenamen"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Anzeigename darf nicht leer sein")
        return v.strip() if v else None

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validiert die Farbe (Hex-Code)"""
        if v is None:
            return None
        v = v.strip()
        if not v.startswith('#') or len(v) not in [4, 7]:
            raise ValueError("Farbe muss ein gültiger Hex-Code sein (z.B. #6B7280)")
        return v


class RoleResponse(BaseModel):
    """Schema für die Antwort"""
    id: int
    name: str
    display_name: str
    description: Optional[str]
    is_active: bool
    color: str
    event_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
