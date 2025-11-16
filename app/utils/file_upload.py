"""File Upload Utility für Beleg-/Quittungs-Uploads"""
import logging
import os
import uuid
import re
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

# Magic Bytes für Dateityp-Validierung (erste Bytes der Datei)
FILE_SIGNATURES = {
    'pdf': b'%PDF',
    'png': b'\x89PNG\r\n\x1a\n',
    'jpg': b'\xff\xd8\xff',
    'jpeg': b'\xff\xd8\xff',
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


def validate_file_content(file_content: bytes, expected_ext: str) -> Tuple[bool, Optional[str]]:
    """
    Validiert Dateiinhalt anhand der Magic Bytes (File Signature).

    Args:
        file_content: Datei-Bytes
        expected_ext: Erwartete Dateierweiterung (ohne Punkt, z.B. 'pdf')

    Returns:
        Tuple (is_valid, error_message)
    """
    if expected_ext not in FILE_SIGNATURES:
        # Keine Signatur hinterlegt, überspringen
        return True, None

    signature = FILE_SIGNATURES[expected_ext]
    if not file_content.startswith(signature):
        return False, f"Dateiinhalt entspricht nicht dem Typ {expected_ext.upper()}"

    return True, None


def validate_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
    """
    Validiert eine hochgeladene Datei (Extension und MIME-Type).

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

    Security:
    - Verhindert Path Traversal (../, ../../, etc.)
    - Entfernt gefährliche Zeichen
    - Normalisiert Pfade
    - Begrenzt Länge

    Args:
        filename: Originaler Dateiname

    Returns:
        Bereinigter Dateiname (nur Dateiname ohne Pfad)
    """
    # Nur Dateiname ohne Pfad extrahieren (verhindert Path Traversal)
    filename = os.path.basename(filename)

    # Zusätzliche Path-Normalisierung
    filename = Path(filename).name

    # Null-Bytes entfernen (Sicherheitslücke)
    filename = filename.replace('\x00', '')

    # Erlaube nur alphanumerische Zeichen, Unterstriche, Bindestriche und Punkte
    # Alle anderen Zeichen werden durch Unterstrich ersetzt
    filename = re.sub(r'[^\w\s\-\.]', '_', filename)

    # Mehrfache Unterstriche durch einen ersetzen
    filename = re.sub(r'_+', '_', filename)

    # Leerzeichen durch Unterstriche ersetzen
    filename = filename.replace(' ', '_')

    # Mehrfache Punkte entfernen (außer vor Extension)
    # Verhindert: "file...pdf" oder "file..pdf"
    stem = Path(filename).stem
    extension = Path(filename).suffix
    stem = stem.replace('..', '_').replace('.', '_')
    filename = f"{stem}{extension}"

    # Maximale Länge begrenzen (255 Zeichen ist Filesystem-Limit)
    max_length = 200  # Konservativ, lässt Platz für Präfixe
    if len(filename) > max_length:
        # Extension beibehalten, Stem kürzen
        extension = Path(filename).suffix
        stem = Path(filename).stem
        stem = stem[:max_length - len(extension)]
        filename = f"{stem}{extension}"

    # Fallback falls Dateiname leer ist
    if not filename or filename == extension:
        filename = f"file{extension}"

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

    Security Features:
    - Extension whitelist
    - MIME-Type validation
    - Magic Bytes validation
    - File size limit
    - Path traversal prevention
    - Filename sanitization

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
        # 1. Extension und MIME-Type Validierung
        is_valid, error = validate_file(file)
        if not is_valid:
            logger.warning(f"File validation failed: {error}")
            return None, error

        # 2. Datei lesen
        contents = await file.read()
        file_size = len(contents)

        # 3. Dateigröße prüfen
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})")
            return None, f"Datei zu groß ({file_size / 1024 / 1024:.1f} MB). Maximum: 7 MB"

        if file_size == 0:
            logger.warning("Empty file uploaded")
            return None, "Datei ist leer"

        # 4. Magic Bytes Validierung (Dateiinhalt prüfen)
        file_ext = Path(file.filename).suffix.lower().lstrip('.')
        is_content_valid, content_error = validate_file_content(contents, file_ext)
        if not is_content_valid:
            logger.warning(f"File content validation failed: {content_error}")
            return None, content_error

        # 5. Upload-Verzeichnis erstellen
        upload_dir = get_upload_dir(event_id, transaction_type)

        # 6. Eindeutigen Dateinamen generieren (bereits sanitized)
        unique_filename = generate_unique_filename(file.filename, transaction_id, transaction_type)

        # 7. Vollständigen Pfad erstellen und normalisieren (Path Traversal Schutz)
        file_path = (upload_dir / unique_filename).resolve()

        # 8. Sicherheitsprüfung: Stelle sicher dass der Pfad im Upload-Verzeichnis liegt
        # Verhindert Path Traversal Angriffe
        try:
            file_path.relative_to(upload_dir.resolve())
        except ValueError:
            logger.error(f"Path traversal attempt detected: {file_path}")
            return None, "Ungültiger Dateipfad"

        # 9. Datei speichern
        with open(file_path, 'wb') as f:
            f.write(contents)

        # 10. Relativen Pfad zurückgeben (für Datenbank)
        # Verwende os.path.relpath für sichere Pfad-Berechnung
        try:
            relative_path = os.path.relpath(file_path, start=Path.cwd())
        except ValueError:
            # Fallback: Verwende str() wenn relpath fehlschlägt
            relative_path = str(file_path)

        logger.info(f"Receipt saved: {relative_path} ({file_size} bytes)")
        return relative_path, None

    except Exception as e:
        logger.error(f"Error saving receipt file: {e}", exc_info=True)
        return None, f"Fehler beim Speichern der Datei: {str(e)}"


def delete_receipt_file(file_path: str) -> bool:
    """
    Löscht eine Beleg-Datei sicher.

    Security:
    - Verhindert Löschen von Dateien außerhalb des Upload-Verzeichnisses
    - Path Traversal Schutz

    Args:
        file_path: Pfad zur Datei (relativ oder absolut)

    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        # Pfad normalisieren und auflösen
        path = Path(file_path).resolve()

        # Sicherheitsprüfung: Datei muss im uploads/ Verzeichnis liegen
        uploads_dir = Path("uploads").resolve()
        try:
            path.relative_to(uploads_dir)
        except ValueError:
            logger.error(f"Attempt to delete file outside uploads directory: {file_path}")
            return False

        # Datei löschen
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
