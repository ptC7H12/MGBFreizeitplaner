"""File Upload Utility für Beleg-/Quittungs-Uploads"""
import logging
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
from fastapi import UploadFile

logger = logging.getLogger(__name__)

# Erlaubte Dateitypen
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/png',
    'image/jpeg',
    'image/jpg'
}

# Max. Dateigröße in Bytes (7 MB)
MAX_FILE_SIZE = 7 * 1024 * 1024


def get_upload_dir(event_id: int, transaction_type: str) -> Path:
    """
    Gibt das Upload-Verzeichnis für ein Event und Transaktionstyp zurück.

    Args:
        event_id: ID des Events
        transaction_type: Typ ('expense' oder 'income')

    Returns:
        Path zum Upload-Verzeichnis
    """
    base_dir = Path("uploads")
    upload_dir = base_dir / "receipts" / f"event_{event_id}" / transaction_type
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def validate_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
    """
    Validiert eine hochgeladene Datei.

    Args:
        file: UploadFile-Objekt

    Returns:
        Tuple (is_valid, error_message)
    """
    # Dateiname-Extension prüfen
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"Dateityp nicht erlaubt. Erlaubt sind: {', '.join(ALLOWED_EXTENSIONS)}"

    # MIME-Type prüfen (falls verfügbar)
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        return False, f"Ungültiger Dateityp: {file.content_type}"

    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Bereinigt einen Dateinamen von gefährlichen Zeichen.

    Args:
        filename: Originaler Dateiname

    Returns:
        Bereinigter Dateiname
    """
    # Nur Dateiname ohne Pfad
    filename = Path(filename).name

    # Gefährliche Zeichen ersetzen
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')

    # Leerzeichen durch Unterstriche ersetzen
    filename = filename.replace(' ', '_')

    return filename


def generate_unique_filename(original_filename: str, transaction_id: int, transaction_type: str) -> str:
    """
    Generiert einen eindeutigen Dateinamen.

    Args:
        original_filename: Originaler Dateiname
        transaction_id: ID der Transaktion
        transaction_type: Typ ('expense' oder 'income')

    Returns:
        Eindeutiger Dateiname
    """
    # Dateiendung extrahieren
    file_ext = Path(original_filename).suffix.lower()

    # Sicheren Dateinamen erstellen
    safe_filename = sanitize_filename(Path(original_filename).stem)

    # Timestamp für Eindeutigkeit
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Format: expense_123_20251115_143022_original_name.pdf
    unique_filename = f"{transaction_type}_{transaction_id}_{timestamp}_{safe_filename}{file_ext}"

    return unique_filename


async def save_receipt_file(
    file: UploadFile,
    event_id: int,
    transaction_id: int,
    transaction_type: str
) -> Tuple[Optional[str], Optional[str]]:
    """
    Speichert eine Beleg-Datei sicher.

    Args:
        file: UploadFile-Objekt
        event_id: ID des Events
        transaction_id: ID der Transaktion
        transaction_type: Typ ('expense' oder 'income')

    Returns:
        Tuple (file_path, error_message)
        - file_path: Relativer Pfad zur gespeicherten Datei (oder None bei Fehler)
        - error_message: Fehlermeldung (oder None bei Erfolg)
    """
    try:
        # Validierung
        is_valid, error = validate_file(file)
        if not is_valid:
            logger.warning(f"File validation failed: {error}")
            return None, error

        # Dateigröße prüfen
        # Datei lesen um Größe zu prüfen
        contents = await file.read()
        file_size = len(contents)

        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})")
            return None, f"Datei zu groß ({file_size / 1024 / 1024:.1f} MB). Maximum: 7 MB"

        if file_size == 0:
            logger.warning("Empty file uploaded")
            return None, "Datei ist leer"

        # Upload-Verzeichnis erstellen
        upload_dir = get_upload_dir(event_id, transaction_type)

        # Eindeutigen Dateinamen generieren
        unique_filename = generate_unique_filename(file.filename, transaction_id, transaction_type)

        # Vollständiger Pfad
        file_path = upload_dir / unique_filename

        # Datei speichern
        with open(file_path, 'wb') as f:
            f.write(contents)

        # Relativen Pfad zurückgeben (für Datenbank)
        relative_path = str(file_path.relative_to(Path("uploads").parent))

        logger.info(f"Receipt saved: {relative_path} ({file_size} bytes)")
        return relative_path, None

    except Exception as e:
        logger.error(f"Error saving receipt file: {e}", exc_info=True)
        return None, f"Fehler beim Speichern der Datei: {str(e)}"


def delete_receipt_file(file_path: str) -> bool:
    """
    Löscht eine Beleg-Datei.

    Args:
        file_path: Pfad zur Datei (relativ oder absolut)

    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        path = Path(file_path)
        if path.exists() and path.is_file():
            path.unlink()
            logger.info(f"Receipt deleted: {file_path}")
            return True
        else:
            logger.warning(f"Receipt file not found: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error deleting receipt file: {e}", exc_info=True)
        return False
