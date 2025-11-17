"""Pydantic Schemas für Ruleset"""
from datetime import date
from typing import Optional, Union, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class RulesetBase(BaseModel):
    """Basis-Schema für Ruleset"""
    name: str = Field(..., min_length=1, max_length=200)
    ruleset_type: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    valid_from: Union[str, date]
    valid_until: Union[str, date]
    age_groups: Dict[str, Any]
    role_discounts: Optional[Dict[str, Any]] = None
    family_discount: Optional[Dict[str, Any]] = None
    is_active: bool = True
    source_file: Optional[str] = Field(None, max_length=500)
    event_id: int

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validiert den Namen"""
        if not v or not v.strip():
            raise ValueError("Name darf nicht leer sein")
        return v.strip()

    @field_validator('ruleset_type')
    @classmethod
    def validate_ruleset_type(cls, v: str) -> str:
        """Validiert den Ruleset-Typ"""
        if not v or not v.strip():
            raise ValueError("Ruleset-Typ darf nicht leer sein")
        return v.strip().lower()

    @field_validator('valid_from')
    @classmethod
    def validate_valid_from(cls, v: Union[str, date]) -> date:
        """Validiert das Startdatum"""
        if isinstance(v, date):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Gültig-von-Datum muss im Format YYYY-MM-DD vorliegen")

    @field_validator('valid_until')
    @classmethod
    def validate_valid_until(cls, v: Union[str, date]) -> date:
        """Validiert das Enddatum"""
        if isinstance(v, date):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Gültig-bis-Datum muss im Format YYYY-MM-DD vorliegen")

    @field_validator('age_groups')
    @classmethod
    def validate_age_groups(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validiert die Altersgruppen"""
        if not v or not isinstance(v, dict):
            raise ValueError("Altersgruppen müssen als Dictionary angegeben werden")
        return v


class RulesetCreate(RulesetBase):
    """Schema für das Erstellen eines Rulesets"""
    pass


class RulesetUpdate(BaseModel):
    """Schema für das Aktualisieren eines Rulesets"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    ruleset_type: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    valid_from: Optional[Union[str, date]] = None
    valid_until: Optional[Union[str, date]] = None
    age_groups: Optional[Dict[str, Any]] = None
    role_discounts: Optional[Dict[str, Any]] = None
    family_discount: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    source_file: Optional[str] = Field(None, max_length=500)
    event_id: Optional[int] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validiert den Namen"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Name darf nicht leer sein")
        return v.strip() if v else None

    @field_validator('ruleset_type')
    @classmethod
    def validate_ruleset_type(cls, v: Optional[str]) -> Optional[str]:
        """Validiert den Ruleset-Typ"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Ruleset-Typ darf nicht leer sein")
        return v.strip().lower() if v else None

    @field_validator('valid_from')
    @classmethod
    def validate_valid_from(cls, v: Optional[Union[str, date]]) -> Optional[date]:
        """Validiert das Startdatum"""
        if v is None:
            return None
        if isinstance(v, date):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Gültig-von-Datum muss im Format YYYY-MM-DD vorliegen")

    @field_validator('valid_until')
    @classmethod
    def validate_valid_until(cls, v: Optional[Union[str, date]]) -> Optional[date]:
        """Validiert das Enddatum"""
        if v is None:
            return None
        if isinstance(v, date):
            return v
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Gültig-bis-Datum muss im Format YYYY-MM-DD vorliegen")

    @field_validator('age_groups')
    @classmethod
    def validate_age_groups(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validiert die Altersgruppen"""
        if v is not None and (not v or not isinstance(v, dict)):
            raise ValueError("Altersgruppen müssen als Dictionary angegeben werden")
        return v


class RulesetResponse(BaseModel):
    """Schema für die Antwort"""
    id: int
    name: str
    ruleset_type: str
    description: Optional[str]
    valid_from: date
    valid_until: date
    age_groups: Dict[str, Any]
    role_discounts: Optional[Dict[str, Any]]
    family_discount: Optional[Dict[str, Any]]
    is_active: bool
    source_file: Optional[str]
    event_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
