"""Pydantic Schemas für Input-Validierung"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Union
from datetime import date, datetime
import re


class ParticipantCreateSchema(BaseModel):
    """Schema für das Erstellen eines Teilnehmers"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    birth_date: Union[str, date] = Field(...)
    gender: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    bildung_teilhabe_id: Optional[str] = Field(None, max_length=100)
    allergies: Optional[str] = None
    medical_notes: Optional[str] = None
    notes: Optional[str] = None
    discount_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    discount_reason: Optional[str] = None
    manual_price_override: Optional[float] = Field(None, ge=0.0)
    role_id: int = Field(..., gt=0)
    family_id: Optional[int] = Field(None, gt=0)

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: Union[str, date]) -> date:
        """Validiert das Geburtsdatum"""
        # Wenn bereits ein date-Objekt, validiere direkt
        if isinstance(v, date):
            birth_date_obj = v
        else:
            # String zu date konvertieren
            try:
                birth_date_obj = datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Geburtsdatum muss im Format YYYY-MM-DD vorliegen")

        # Datum darf nicht in der Zukunft liegen
        if birth_date_obj > date.today():
            raise ValueError("Geburtsdatum darf nicht in der Zukunft liegen")

        # Datum muss nach 1900 sein
        if birth_date_obj.year < 1900:
            raise ValueError("Geburtsdatum muss nach 1900 liegen")

        return birth_date_obj

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validiert die E-Mail-Adresse"""
        if v and v.strip():
            # Einfache E-Mail-Validierung
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v.strip()):
                raise ValueError("Ungültige E-Mail-Adresse")
            return v.strip()
        return None

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validiert Namen (keine Leerzeichen am Anfang/Ende)"""
        if not v or not v.strip():
            raise ValueError("Name darf nicht leer sein")
        return v.strip()


class ParticipantUpdateSchema(ParticipantCreateSchema):
    """Schema für das Aktualisieren eines Teilnehmers (gleiche Validierung)"""
    pass


class FamilyCreateSchema(BaseModel):
    """Schema für das Erstellen einer Familie"""
    name: str = Field(..., min_length=1, max_length=200)
    contact_person: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validiert den Familiennamen"""
        if not v or not v.strip():
            raise ValueError("Familienname darf nicht leer sein")
        return v.strip()

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validiert die E-Mail-Adresse"""
        if v and v.strip():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v.strip()):
                raise ValueError("Ungültige E-Mail-Adresse")
            return v.strip()
        return None


class FamilyUpdateSchema(FamilyCreateSchema):
    """Schema für das Aktualisieren einer Familie"""
    pass


class PaymentCreateSchema(BaseModel):
    """Schema für das Erstellen einer Zahlung"""
    amount: float = Field(..., gt=0.0)
    payment_date: Union[str, date] = Field(...)
    payment_method: Optional[str] = Field(None, max_length=50)
    reference: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    participant_id: Optional[int] = Field(None, gt=0)
    family_id: Optional[int] = Field(None, gt=0)

    @field_validator('payment_date')
    @classmethod
    def validate_payment_date(cls, v: Union[str, date]) -> date:
        """Validiert das Zahlungsdatum"""
        # Wenn bereits ein date-Objekt, validiere direkt
        if isinstance(v, date):
            payment_date_obj = v
        else:
            # String zu date konvertieren
            try:
                payment_date_obj = datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Zahlungsdatum muss im Format YYYY-MM-DD vorliegen")

        # Datum darf nicht in der Zukunft liegen
        if payment_date_obj > date.today():
            raise ValueError("Zahlungsdatum darf nicht in der Zukunft liegen")

        return payment_date_obj

    @model_validator(mode='after')
    def validate_participant_or_family(self):
        """Validiert, dass entweder participant_id oder family_id gesetzt ist"""
        if not self.participant_id and not self.family_id:
            raise ValueError("Entweder Teilnehmer oder Familie muss ausgewählt werden")

        if self.participant_id and self.family_id:
            raise ValueError("Es kann nur entweder Teilnehmer oder Familie ausgewählt werden")

        return self


class PaymentUpdateSchema(PaymentCreateSchema):
    """Schema für das Aktualisieren einer Zahlung"""
    pass


class ExpenseCreateSchema(BaseModel):
    """Schema für das Erstellen einer Ausgabe"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    amount: float = Field(..., gt=0.0)
    expense_date: Union[str, date] = Field(...)
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


class ExpenseUpdateSchema(ExpenseCreateSchema):
    """Schema für das Aktualisieren einer Ausgabe"""
    pass


class SettingUpdateSchema(BaseModel):
    """Schema für das Aktualisieren der Einstellungen"""
    organization_name: str = Field(..., min_length=1, max_length=200)
    organization_address: Optional[str] = None
    bank_account_holder: str = Field(..., min_length=1, max_length=200)
    bank_iban: str = Field(..., min_length=15, max_length=34)
    bank_bic: Optional[str] = Field(None, min_length=8, max_length=11)
    invoice_subject_prefix: Optional[str] = Field(None, max_length=100)
    invoice_footer_text: Optional[str] = None
    default_github_repo: Optional[str] = Field(None, max_length=500)

    @field_validator('organization_name', 'bank_account_holder')
    @classmethod
    def validate_required_text(cls, v: str) -> str:
        """Validiert Pflicht-Textfelder"""
        if not v or not v.strip():
            raise ValueError("Feld darf nicht leer sein")
        return v.strip()

    @field_validator('bank_iban')
    @classmethod
    def validate_iban(cls, v: str) -> str:
        """Validiert die IBAN"""
        if not v or not v.strip():
            raise ValueError("IBAN darf nicht leer sein")

        # Leerzeichen entfernen für Validierung
        iban = v.strip().replace(" ", "")

        # IBAN muss mit 2 Buchstaben beginnen, gefolgt von Ziffern
        iban_pattern = r'^[A-Z]{2}[0-9]{2}[A-Z0-9]+$'
        if not re.match(iban_pattern, iban):
            raise ValueError("Ungültige IBAN (Format: DE89370400440532013000)")

        # Länge prüfen (15-34 Zeichen)
        if len(iban) < 15 or len(iban) > 34:
            raise ValueError("IBAN muss zwischen 15 und 34 Zeichen lang sein")

        return iban  # Ohne Leerzeichen zurückgeben

    @field_validator('bank_bic')
    @classmethod
    def validate_bic(cls, v: Optional[str]) -> Optional[str]:
        """Validiert die BIC"""
        if v and v.strip():
            bic = v.strip().replace(" ", "")

            # BIC muss 8 oder 11 Zeichen lang sein
            bic_pattern = r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$'
            if not re.match(bic_pattern, bic):
                raise ValueError("Ungültige BIC (Format: COBADEFFXXX)")

            return bic
        return None
