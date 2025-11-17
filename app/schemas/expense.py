"""Pydantic Schemas für Expense"""
from datetime import date
from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class ExpenseBase(BaseModel):
    """Basis-Schema für Ausgaben (ohne event_id, da es aus Dependency kommt)"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    amount: float = Field(..., gt=0)
    expense_date: Union[str, date]
    category: Optional[str] = Field(None, max_length=100)
    receipt_number: Optional[str] = Field(None, max_length=100)
    paid_by: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validiert den Titel"""
        if not v or not v.strip():
            raise ValueError("Titel darf nicht leer sein")
        return v.strip()

    @field_validator('expense_date')
    @classmethod
    def validate_expense_date(cls, v: Union[str, date]) -> date:
        """Validiert das Ausgabendatum"""
        # Wenn bereits ein date-Objekt, validiere direkt
        if isinstance(v, date):
            expense_date_obj = v
        else:
            # String zu date konvertieren
            try:
                expense_date_obj = datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Ausgabendatum muss im Format YYYY-MM-DD vorliegen")

        # Datum darf nicht in der Zukunft liegen
        if expense_date_obj > date.today():
            raise ValueError("Ausgabendatum darf nicht in der Zukunft liegen")

        return expense_date_obj


class ExpenseCreate(ExpenseBase):
    """Schema für das Erstellen einer Ausgabe"""
    pass


class ExpenseUpdate(BaseModel):
    """Schema für das Aktualisieren einer Ausgabe"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    expense_date: Optional[Union[str, date]] = None
    category: Optional[str] = Field(None, max_length=100)
    receipt_number: Optional[str] = Field(None, max_length=100)
    paid_by: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validiert den Titel"""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Titel darf nicht leer sein")
        return v.strip() if v else None

    @field_validator('expense_date')
    @classmethod
    def validate_expense_date(cls, v: Optional[Union[str, date]]) -> Optional[date]:
        """Validiert das Ausgabendatum"""
        if v is None:
            return None

        # Wenn bereits ein date-Objekt, validiere direkt
        if isinstance(v, date):
            expense_date_obj = v
        else:
            # String zu date konvertieren
            try:
                expense_date_obj = datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Ausgabendatum muss im Format YYYY-MM-DD vorliegen")

        # Datum darf nicht in der Zukunft liegen
        if expense_date_obj > date.today():
            raise ValueError("Ausgabendatum darf nicht in der Zukunft liegen")

        return expense_date_obj


class ExpenseResponse(BaseModel):
    """Schema für die Antwort"""
    id: int
    title: str
    description: Optional[str]
    amount: float
    expense_date: date
    category: Optional[str]
    receipt_number: Optional[str]
    paid_by: Optional[str]
    notes: Optional[str]
    event_id: int

    class Config:
        from_attributes = True
