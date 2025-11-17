"""Logging-Konfiguration für strukturiertes und professionelles Logging"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(debug: bool = False, log_file: str = "freizeit_kassen.log") -> None:
    """
    Konfiguriert das Logging-System mit Console und File Handler.

    Args:
        debug: Wenn True, wird DEBUG-Level verwendet, sonst INFO
        log_file: Pfad zur Log-Datei

    Features:
        - Strukturiertes Format mit Timestamp, Level, Module, Message
        - Rotierende Log-Dateien (max 10 MB, 5 Backups)
        - Console-Output für Entwicklung
        - File-Output für Produktion und Debugging
        - Unterschiedliche Log-Levels für Debug/Production
    """
    # Log-Level bestimmen
    level = logging.DEBUG if debug else logging.INFO

    # Format: "2024-01-15 14:30:45 - app.routers.participants - INFO - Participant created"
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # === Console Handler ===
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # === File Handler (Rotating) ===
    # Log-Verzeichnis erstellen falls nicht vorhanden
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,  # Behalte 5 alte Logs
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # === Root Logger konfigurieren ===
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Alte Handler entfernen (falls vorhanden)
    root_logger.handlers.clear()

    # Neue Handler hinzufügen
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # === Externe Libraries leiser machen ===
    # SQLAlchemy ist zu verbose auf INFO
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)

    # Uvicorn access logs nur auf WARNING (zu verbose)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)

    # Startup-Nachricht
    root_logger.info(f"Logging initialisiert (Level: {logging.getLevelName(level)})")
    root_logger.info(f"Log-Datei: {log_path.absolute()}")


def get_logger(name: str) -> logging.Logger:
    """
    Gibt einen Logger mit dem angegebenen Namen zurück.

    Usage:
        logger = get_logger(__name__)
        logger.info("Something happened")
    """
    return logging.getLogger(name)
