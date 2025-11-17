"""Pydantic Schemas für Event"""
from datetime import date
from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class EventBase(BaseModel):
    """Basis-Schema für Event"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    event_type: str = Field(..., min_length=1, max_length=50)
    start_date: Union[str, date]
    end_date: Union[str, date]
    location: Optional[str] = Field(None, max_length=200)
    code: Optional[str] = Field(None, max_length=20)
    is_active: bool = True

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validiert den Namen"""
        if not v or not v.strip():
            raise ValueError("Name darf nicht leer sein")
        return v.strip()

    @field_validator('event_type')
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        """Validiert den Event-Typ"""
        if not v or not v.strip():
            raise ValueError("Event-Typ darf nicht leer sein")
        return v.strip().lower()

    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v: Union[str, date]) -> date:
        """Validiert das Startdatum"""
        if isinstance(v, date):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Startdatum muss im Format YYYY-MM-DD vorliegen")

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: Union[str, date]) -> date:
        """Validiert das Enddatum"""
        if isinstance(v, date):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Enddatum muss im Format YYYY-MM-DD vorliegen")


class EventCreate(EventBase):
    """Schema für das Erstellen eines Events"""
    pass


class EventUpdate(BaseModel):
    """Schema für das Aktualisieren eines Events"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    event_type: Optional[str] = Field(None, min_length=1, max_length=50)
    start_date: Optional[Union[str, date]] = None
    end_date: Optional[Union[str, date]] = None
    location: Optional[str] = Field(None, max_length=200)
    code: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validiert den Namen"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Name darf nicht leer sein")
        return v.strip() if v else None

    @field_validator('event_type')
    @classmethod
    def validate_event_type(cls, v: Optional[str]) -> Optional[str]:
        """Validiert den Event-Typ"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Event-Typ darf nicht leer sein")
        return v.strip().lower() if v else None

    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v: Optional[Union[str, date]]) -> Optional[date]:
        """Validiert das Startdatum"""
        if v is None:
            return None
        if isinstance(v, date):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Startdatum muss im Format YYYY-MM-DD vorliegen")

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: Optional[Union[str, date]]) -> Optional[date]:
        """Validiert das Enddatum"""
        if v is None:
            return None
        if isinstance(v, date):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Enddatum muss im Format YYYY-MM-DD vorliegen")


class EventResponse(BaseModel):
    """Schema für die Antwort"""
    id: int
    name: str
    description: Optional[str]
    event_type: str
    start_date: date
    end_date: date
    location: Optional[str]
    code: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
