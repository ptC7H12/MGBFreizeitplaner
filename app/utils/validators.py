"""Zentrale Validierungs-Funktionen für wiederverwendbare Logik"""
import re
from typing import Optional
from datetime import date


class Validators:
    """Sammlung von wiederverwendbaren Validierungs-Funktionen"""

    # Regex-Pattern als Klassen-Konstanten
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    IBAN_PATTERN = r'^[A-Z]{2}[0-9]{2}[A-Z0-9]+$'
    BIC_PATTERN = r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$'

    @staticmethod
    def validate_email(email: Optional[str]) -> Optional[str]:
        """
        Validiert eine E-Mail-Adresse.

        Args:
            email: E-Mail-Adresse als String (oder None)

        Returns:
            Bereinigte E-Mail (stripped) oder None

        Raises:
            ValueError: Wenn E-Mail ungültig ist
        """
        if email and email.strip():
            if not re.match(Validators.EMAIL_PATTERN, email.strip()):
                raise ValueError("Ungültige E-Mail-Adresse")
            return email.strip()
        return None

    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> str:
        """
        Validiert einen Namen (kein Leerstring, getrimmt).

        Args:
            name: Name als String
            field_name: Feldname für Fehlermeldung (z.B. "Vorname", "Nachname")

        Returns:
            Bereinigter Name (stripped)

        Raises:
            ValueError: Wenn Name leer ist
        """
        if not name or not name.strip():
            raise ValueError(f"{field_name} darf nicht leer sein")
        return name.strip()

    @staticmethod
    def validate_date(
        date_value: date,
        min_year: int = 1900,
        max_date: Optional[date] = None,
        field_name: str = "Datum"
    ) -> date:
        """
        Validiert ein Datum.

        Args:
            date_value: Datum-Objekt
            min_year: Minimales Jahr (default: 1900)
            max_date: Maximales Datum (default: heute)
            field_name: Feldname für Fehlermeldung

        Returns:
            Validiertes Datum

        Raises:
            ValueError: Wenn Datum ungültig ist
        """
        if max_date is None:
            max_date = date.today()

        if date_value > max_date:
            raise ValueError(f"{field_name} darf nicht in der Zukunft liegen")

        if date_value.year < min_year:
            raise ValueError(f"{field_name} muss nach {min_year} liegen")

        return date_value

    @staticmethod
    def validate_iban(iban: str) -> str:
        """
        Validiert eine IBAN.

        Args:
            iban: IBAN als String

        Returns:
            Bereinigte IBAN (ohne Leerzeichen)

        Raises:
            ValueError: Wenn IBAN ungültig ist
        """
        if not iban or not iban.strip():
            raise ValueError("IBAN darf nicht leer sein")

        # Leerzeichen entfernen
        iban_clean = iban.strip().replace(" ", "")

        # Format prüfen
        if not re.match(Validators.IBAN_PATTERN, iban_clean):
            raise ValueError("Ungültige IBAN (Format: DE89370400440532013000)")

        # Länge prüfen
        if len(iban_clean) < 15 or len(iban_clean) > 34:
            raise ValueError("IBAN muss zwischen 15 und 34 Zeichen lang sein")

        return iban_clean

    @staticmethod
    def validate_bic(bic: Optional[str]) -> Optional[str]:
        """
        Validiert eine BIC.

        Args:
            bic: BIC als String (oder None)

        Returns:
            Bereinigte BIC (ohne Leerzeichen) oder None

        Raises:
            ValueError: Wenn BIC ungültig ist
        """
        if bic and bic.strip():
            bic_clean = bic.strip().replace(" ", "")

            # Format prüfen
            if not re.match(Validators.BIC_PATTERN, bic_clean):
                raise ValueError("Ungültige BIC (Format: COBADEFFXXX)")

            return bic_clean

        return None

    @staticmethod
    def validate_required_text(text: str, field_name: str = "Feld") -> str:
        """
        Validiert einen Pflicht-Text (darf nicht leer sein).

        Args:
            text: Text als String
            field_name: Feldname für Fehlermeldung

        Returns:
            Bereinigter Text (stripped)

        Raises:
            ValueError: Wenn Text leer ist
        """
        if not text or not text.strip():
            raise ValueError(f"{field_name} darf nicht leer sein")
        return text.strip()
