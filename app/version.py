"""Zentrale Versionsverwaltung für MGBFreizeitplaner

Die Version wird aus der version.txt Datei im Root-Verzeichnis gelesen.
Dies ermöglicht eine zentrale Pflege der Versionsnummer.
"""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Pfad zur version.txt im Root-Verzeichnis
VERSION_FILE = Path(__file__).parent.parent / "version.txt"

def get_version() -> str:
    """
    Liest die Version aus der version.txt Datei.

    Returns:
        str: Die Version als String (z.B. "0.1.0")

    Fallback:
        Falls die Datei nicht existiert oder nicht gelesen werden kann,
        wird "0.0.0" zurückgegeben.
    """
    try:
        if VERSION_FILE.exists():
            version = VERSION_FILE.read_text().strip()
            if version:
                return version
            else:
                logger.warning("version.txt ist leer, verwende Fallback '0.0.0'")
                return "0.0.0"
        else:
            logger.warning(f"version.txt nicht gefunden unter {VERSION_FILE}, verwende Fallback '0.0.0'")
            return "0.0.0"
    except Exception as e:
        logger.error(f"Fehler beim Lesen der version.txt: {e}, verwende Fallback '0.0.0'")
        return "0.0.0"


# Version wird beim Import einmal ausgelesen
__version__ = get_version()
