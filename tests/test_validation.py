"""Tests für Pydantic-Validierung (IBAN, BIC, Participant, etc.)"""
import pytest
from datetime import date, timedelta
from pydantic import ValidationError

from app.schemas import (
    ParticipantCreateSchema,
    SettingUpdateSchema,
    PaymentCreateSchema
)


@pytest.mark.unit
class TestIBANValidation:
    """Tests für IBAN-Validierung"""

    def test_valid_german_iban(self):
        """Test: Gültige deutsche IBAN"""
        data = {
            "bank_iban": "DE89370400440532013000",
            "bank_bic": "COBADEFFXXX",
            "bank_account_holder": "Test Org",
            "organization_name": "Test"
        }
        schema = SettingUpdateSchema(**data)
        assert schema.bank_iban == "DE89370400440532013000"

    def test_valid_iban_with_spaces(self):
        """Test: IBAN mit Leerzeichen wird normalisiert"""
        data = {
            "bank_iban": "DE89 3704 0044 0532 0130 00",
            "bank_bic": "COBADEFFXXX",
            "bank_account_holder": "Test Org",
            "organization_name": "Test"
        }
        schema = SettingUpdateSchema(**data)
        # Leerzeichen sollten entfernt werden
        assert " " not in schema.bank_iban

    def test_invalid_iban_too_short(self):
        """Test: Zu kurze IBAN (< 15 Zeichen)"""
        data = {
            "bank_iban": "DE891234",  # Nur 8 Zeichen
            "bank_bic": "COBADEFFXXX",
            "bank_account_holder": "Test Org",
            "organization_name": "Test"
        }
        with pytest.raises(ValidationError) as exc_info:
            SettingUpdateSchema(**data)
        assert "IBAN muss zwischen 15 und 34 Zeichen" in str(exc_info.value)

    def test_invalid_iban_too_long(self):
        """Test: Zu lange IBAN (> 34 Zeichen)"""
        data = {
            "bank_iban": "DE89" + "1234567890" * 4,  # > 34 Zeichen
            "bank_bic": "COBADEFFXXX",
            "bank_account_holder": "Test Org",
            "organization_name": "Test"
        }
        with pytest.raises(ValidationError) as exc_info:
            SettingUpdateSchema(**data)
        assert "IBAN muss zwischen 15 und 34 Zeichen" in str(exc_info.value)

    def test_invalid_iban_format(self):
        """Test: Ungültiges IBAN-Format (muss mit 2 Buchstaben + 2 Ziffern beginnen)"""
        data = {
            "bank_iban": "1234567890123456",  # Beginnt nicht mit Ländercode
            "bank_bic": "COBADEFFXXX",
            "bank_account_holder": "Test Org",
            "organization_name": "Test"
        }
        with pytest.raises(ValidationError) as exc_info:
            SettingUpdateSchema(**data)
        assert "Ungültige IBAN" in str(exc_info.value)

    def test_iban_case_insensitive(self):
        """Test: IBAN Groß-/Kleinschreibung"""
        data = {
            "bank_iban": "de89370400440532013000",  # Kleinbuchstaben
            "bank_bic": "COBADEFFXXX",
            "bank_account_holder": "Test Org",
            "organization_name": "Test"
        }
        schema = SettingUpdateSchema(**data)
        # IBAN sollte normalisiert werden (Großbuchstaben)
        assert schema.bank_iban.startswith("DE")


@pytest.mark.unit
class TestBICValidation:
    """Tests für BIC-Validierung"""

    def test_valid_bic_11_chars(self):
        """Test: Gültiger BIC mit 11 Zeichen"""
        data = {
            "bank_iban": "DE89370400440532013000",
            "bank_bic": "COBADEFFXXX",
            "bank_account_holder": "Test Org",
            "organization_name": "Test"
        }
        schema = SettingUpdateSchema(**data)
        assert schema.bank_bic == "COBADEFFXXX"

    def test_valid_bic_8_chars(self):
        """Test: Gültiger BIC mit 8 Zeichen"""
        data = {
            "bank_iban": "DE89370400440532013000",
            "bank_bic": "COBADEFF",
            "bank_account_holder": "Test Org",
            "organization_name": "Test"
        }
        schema = SettingUpdateSchema(**data)
        assert schema.bank_bic == "COBADEFF"

    def test_bic_optional(self):
        """Test: BIC ist optional"""
        data = {
            "bank_iban": "DE89370400440532013000",
            "bank_bic": None,
            "bank_account_holder": "Test Org",
            "organization_name": "Test"
        }
        schema = SettingUpdateSchema(**data)
        assert schema.bank_bic is None

    def test_invalid_bic_too_short(self):
        """Test: BIC zu kurz (< 8 Zeichen)"""
        data = {
            "bank_iban": "DE89370400440532013000",
            "bank_bic": "COBAD",  # Nur 5 Zeichen
            "bank_account_holder": "Test Org",
            "organization_name": "Test"
        }
        with pytest.raises(ValidationError) as exc_info:
            SettingUpdateSchema(**data)
        assert "BIC muss 8 oder 11 Zeichen" in str(exc_info.value)

    def test_invalid_bic_wrong_length(self):
        """Test: BIC ungültige Länge (9 oder 10 Zeichen)"""
        data = {
            "bank_iban": "DE89370400440532013000",
            "bank_bic": "COBADEFFX",  # 9 Zeichen (ungültig)
            "bank_account_holder": "Test Org",
            "organization_name": "Test"
        }
        with pytest.raises(ValidationError) as exc_info:
            SettingUpdateSchema(**data)
        assert "BIC muss 8 oder 11 Zeichen" in str(exc_info.value)

    def test_invalid_bic_format(self):
        """Test: BIC ungültiges Format (muss mit 6 Buchstaben beginnen)"""
        data = {
            "bank_iban": "DE89370400440532013000",
            "bank_bic": "123456XX",  # Beginnt mit Zahlen
            "bank_account_holder": "Test Org",
            "organization_name": "Test"
        }
        with pytest.raises(ValidationError) as exc_info:
            SettingUpdateSchema(**data)
        assert "Ungültiger BIC" in str(exc_info.value)


@pytest.mark.unit
class TestParticipantValidation:
    """Tests für Participant-Validierung"""

    def test_valid_participant(self):
        """Test: Gültiger Teilnehmer"""
        data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "birth_date": "2010-05-15",
            "email": "max@mustermann.de",
            "phone": "0123456789"
        }
        schema = ParticipantCreateSchema(**data)
        assert schema.first_name == "Max"
        assert schema.email == "max@mustermann.de"

    def test_birth_date_not_in_future(self):
        """Test: Geburtsdatum darf nicht in der Zukunft liegen"""
        future_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "birth_date": future_date,
            "email": "max@mustermann.de"
        }
        with pytest.raises(ValidationError) as exc_info:
            ParticipantCreateSchema(**data)
        assert "Geburtsdatum darf nicht in der Zukunft liegen" in str(exc_info.value)

    def test_birth_date_not_before_1900(self):
        """Test: Geburtsdatum nicht vor 1900"""
        data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "birth_date": "1899-12-31",
            "email": "max@mustermann.de"
        }
        with pytest.raises(ValidationError) as exc_info:
            ParticipantCreateSchema(**data)
        assert "Geburtsdatum muss nach 1900 liegen" in str(exc_info.value)

    def test_email_validation(self):
        """Test: E-Mail-Validierung"""
        # Gültige E-Mail
        data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "birth_date": "2010-05-15",
            "email": "max@example.com"
        }
        schema = ParticipantCreateSchema(**data)
        assert schema.email == "max@example.com"

    def test_invalid_email_format(self):
        """Test: Ungültiges E-Mail-Format"""
        data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "birth_date": "2010-05-15",
            "email": "not-an-email"
        }
        with pytest.raises(ValidationError) as exc_info:
            ParticipantCreateSchema(**data)
        assert "Ungültige E-Mail-Adresse" in str(exc_info.value)

    def test_email_optional(self):
        """Test: E-Mail ist optional"""
        data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "birth_date": "2010-05-15",
            "email": None
        }
        schema = ParticipantCreateSchema(**data)
        assert schema.email is None

    def test_name_validation(self):
        """Test: Namen-Validierung"""
        # Zu kurzer Name
        data = {
            "first_name": "M",
            "last_name": "Mustermann",
            "birth_date": "2010-05-15"
        }
        with pytest.raises(ValidationError) as exc_info:
            ParticipantCreateSchema(**data)
        assert "Vorname muss mindestens 2 Zeichen" in str(exc_info.value)

        # Zu langer Name (> 100 Zeichen)
        data = {
            "first_name": "M" * 101,
            "last_name": "Mustermann",
            "birth_date": "2010-05-15"
        }
        with pytest.raises(ValidationError) as exc_info:
            ParticipantCreateSchema(**data)
        assert "Vorname darf maximal 100 Zeichen" in str(exc_info.value)


@pytest.mark.unit
class TestPaymentValidation:
    """Tests für Payment-Validierung"""

    def test_valid_payment_for_participant(self):
        """Test: Gültige Zahlung für Teilnehmer"""
        data = {
            "amount": 100.50,
            "payment_date": date.today().strftime("%Y-%m-%d"),
            "payment_method": "Überweisung",
            "participant_id": 1,
            "family_id": None
        }
        schema = PaymentCreateSchema(**data)
        assert schema.amount == 100.50
        assert schema.participant_id == 1

    def test_valid_payment_for_family(self):
        """Test: Gültige Zahlung für Familie"""
        data = {
            "amount": 300.00,
            "payment_date": date.today().strftime("%Y-%m-%d"),
            "payment_method": "Bar",
            "participant_id": None,
            "family_id": 5
        }
        schema = PaymentCreateSchema(**data)
        assert schema.amount == 300.00
        assert schema.family_id == 5

    def test_payment_requires_participant_or_family(self):
        """Test: Zahlung benötigt entweder participant_id oder family_id"""
        data = {
            "amount": 100.00,
            "payment_date": date.today().strftime("%Y-%m-%d"),
            "payment_method": "Überweisung",
            "participant_id": None,
            "family_id": None
        }
        with pytest.raises(ValidationError) as exc_info:
            PaymentCreateSchema(**data)
        assert "Entweder participant_id oder family_id muss angegeben werden" in str(exc_info.value)

    def test_payment_not_both_participant_and_family(self):
        """Test: Zahlung kann nicht gleichzeitig für Teilnehmer UND Familie sein"""
        data = {
            "amount": 100.00,
            "payment_date": date.today().strftime("%Y-%m-%d"),
            "payment_method": "Überweisung",
            "participant_id": 1,
            "family_id": 5
        }
        with pytest.raises(ValidationError) as exc_info:
            PaymentCreateSchema(**data)
        assert "Es kann nur participant_id ODER family_id angegeben werden" in str(exc_info.value)

    def test_payment_amount_positive(self):
        """Test: Zahlungsbetrag muss positiv sein"""
        data = {
            "amount": -50.00,
            "payment_date": date.today().strftime("%Y-%m-%d"),
            "payment_method": "Überweisung",
            "participant_id": 1
        }
        with pytest.raises(ValidationError) as exc_info:
            PaymentCreateSchema(**data)
        # Pydantic Field constraint (ge=0.01)
        assert "greater than or equal to 0.01" in str(exc_info.value).lower()

    def test_payment_date_format(self):
        """Test: Zahlungsdatum Format"""
        # Gültiges Format
        data = {
            "amount": 100.00,
            "payment_date": "2024-01-15",
            "payment_method": "Überweisung",
            "participant_id": 1
        }
        schema = PaymentCreateSchema(**data)
        assert schema.payment_date == date(2024, 1, 15)

        # Ungültiges Format
        with pytest.raises(ValidationError):
            data["payment_date"] = "15.01.2024"  # Deutsches Format
            PaymentCreateSchema(**data)
