"""
Datetime Utilities für konsistentes Zeit-Handling

Strategie für lokale Single-User Anwendung:
- Timestamps (created_at, updated_at): UTC für Konsistenz
- Business Dates (expense_date, payment_date): Lokale Zeit für Benutzerfreundlichkeit

Warum UTC für Timestamps?
- Vermeidet Probleme mit Sommerzeit-Umstellung
- Konsistent bei Server-Neustart
- Standard für Datenbank-Timestamps

Warum lokale Zeit für Business Dates?
- Benutzer denkt in lokaler Zeit
- Datums-Felder haben keine Zeitzone
- Einfachere Handhabung für Single-User lokal
"""
from datetime import datetime, date, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def utcnow() -> datetime:
    """
    Gibt die aktuelle UTC-Zeit zurück (timezone-aware).

    Ersetzt datetime.utcnow() (deprecated in Python 3.12)
    mit datetime.now(timezone.utc).

    Returns:
        Timezone-aware UTC datetime
    """
    return datetime.now(timezone.utc)


def now() -> datetime:
    """
    Gibt die aktuelle lokale Zeit zurück (timezone-aware).

    Returns:
        Timezone-aware lokale datetime
    """
    return datetime.now()


def today() -> date:
    """
    Gibt das aktuelle lokale Datum zurück.

    Returns:
        Lokales date Objekt
    """
    return date.today()


def to_local(dt: datetime) -> datetime:
    """
    Konvertiert UTC datetime zu lokalem datetime.

    Args:
        dt: UTC datetime (timezone-aware oder naive)

    Returns:
        Lokales datetime
    """
    if dt.tzinfo is None:
        # Naive datetime - assume UTC
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone()


def to_utc(dt: datetime) -> datetime:
    """
    Konvertiert lokales datetime zu UTC datetime.

    Args:
        dt: Lokales datetime (timezone-aware oder naive)

    Returns:
        UTC datetime
    """
    if dt.tzinfo is None:
        # Naive datetime - assume local
        logger.warning("Converting naive datetime to UTC - assuming local timezone")
        dt = dt.astimezone(timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    return dt


def naive_utc_to_aware(dt: datetime) -> datetime:
    """
    Konvertiert naive UTC datetime zu timezone-aware UTC datetime.

    Nützlich für bestehende Datenbank-Einträge die als naive UTC gespeichert wurden.

    Args:
        dt: Naive datetime (sollte UTC sein)

    Returns:
        Timezone-aware UTC datetime
    """
    if dt.tzinfo is not None:
        return dt

    return dt.replace(tzinfo=timezone.utc)


# Für SQLAlchemy default Funktionen
def get_utc_timestamp() -> datetime:
    """
    Wrapper für utcnow() zur Verwendung in SQLAlchemy Column defaults.

    Verwendung:
        created_at = Column(DateTime, default=get_utc_timestamp)
    """
    return utcnow()


def get_local_date() -> date:
    """
    Wrapper für today() zur Verwendung in SQLAlchemy Column defaults.

    Verwendung:
        registration_date = Column(Date, default=get_local_date)
    """
    return today()
