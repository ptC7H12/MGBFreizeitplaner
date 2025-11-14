"""Pydantic Schemas für Setting"""
from typing import Optional
from pydantic import BaseModel, Field


class SettingBase(BaseModel):
    """Basis-Schema für Einstellungen"""
    organization_name: Optional[str] = Field(None, max_length=200)
    organization_address: Optional[str] = None
    bank_account_holder: Optional[str] = Field(None, max_length=200)
    bank_iban: Optional[str] = Field(None, max_length=34)
    bank_bic: Optional[str] = Field(None, max_length=11)
    invoice_subject_prefix: Optional[str] = Field(None, max_length=100)
    invoice_footer_text: Optional[str] = None


class SettingUpdate(SettingBase):
    """Schema für das Aktualisieren von Einstellungen"""
    pass


class SettingResponse(SettingBase):
    """Schema für die Antwort"""
    id: int
    event_id: int

    class Config:
        from_attributes = True
