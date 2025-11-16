"""
Migration Checker Utility

Prüft beim App-Start ob Alembic-Migrationen ausstehen und führt diese automatisch aus.
"""
import logging
import subprocess
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


def check_migrations_pending() -> Tuple[bool, Optional[str]]:
    """
    Prüft ob Alembic-Migrationen ausstehen.

    Returns:
        Tuple (has_pending, current_version)
        - has_pending: True wenn Migrationen ausstehen
        - current_version: Aktuelle DB-Version (oder None)
    """
    try:
        # Prüfe ob alembic verfügbar ist
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            logger.warning(f"Alembic current check failed: {result.stderr}")
            return False, None

        current_output = result.stdout.strip()

        # Prüfe head version
        result = subprocess.run(
            ["alembic", "heads"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            logger.warning(f"Alembic heads check failed: {result.stderr}")
            return False, None

        head_output = result.stdout.strip()

        # Parse versions
        current_version = None
        if current_output and "(head)" not in current_output.lower():
            # Extrahiere Version-ID (erste Wort der Zeile)
            parts = current_output.split()
            if parts:
                current_version = parts[0]
                logger.info(f"Current DB version: {current_version}")

        # Wenn current version nicht head ist, sind Migrationen ausstehend
        has_pending = current_version is None or "(head)" not in current_output.lower()

        return has_pending, current_version

    except FileNotFoundError:
        logger.error("Alembic nicht gefunden! Bitte installieren: pip install alembic")
        return False, None
    except subprocess.TimeoutExpired:
        logger.error("Alembic-Befehl hat Timeout überschritten")
        return False, None
    except Exception as e:
        logger.error(f"Fehler beim Prüfen der Migrationen: {e}", exc_info=True)
        return False, None


def run_migrations() -> bool:
    """
    Führt ausstehende Alembic-Migrationen aus.

    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        logger.info("Führe Alembic-Migrationen aus...")

        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            timeout=60  # Max 60 Sekunden für Migrationen
        )

        if result.returncode == 0:
            logger.info("✓ Migrationen erfolgreich ausgeführt!")
            if result.stdout:
                logger.info(f"Output: {result.stdout}")
            return True
        else:
            logger.error(f"✗ Migrationen fehlgeschlagen!")
            logger.error(f"Stderr: {result.stderr}")
            logger.error(f"Stdout: {result.stdout}")
            return False

    except FileNotFoundError:
        logger.error("Alembic nicht gefunden!")
        return False
    except subprocess.TimeoutExpired:
        logger.error("Migrations-Timeout überschritten (>60s)!")
        return False
    except Exception as e:
        logger.error(f"Fehler beim Ausführen der Migrationen: {e}", exc_info=True)
        return False


def check_and_run_migrations(auto_upgrade: bool = True) -> None:
    """
    Prüft und führt Migrationen aus (wenn auto_upgrade=True).

    Args:
        auto_upgrade: Wenn True, werden Migrationen automatisch ausgeführt

    Raises:
        RuntimeError: Wenn Migrationen fehlschlagen und auto_upgrade=True
    """
    logger.info("Prüfe Alembic-Migrationen...")

    has_pending, current_version = check_migrations_pending()

    if not has_pending:
        logger.info("✓ Datenbank ist auf dem neuesten Stand")
        return

    logger.warning("⚠️  Ausstehende Migrationen gefunden!")
    if current_version:
        logger.warning(f"   Aktuelle Version: {current_version}")
    logger.warning(f"   Auto-Upgrade: {'Aktiviert' if auto_upgrade else 'Deaktiviert'}")

    if auto_upgrade:
        logger.info("Starte automatisches Upgrade...")
        success = run_migrations()

        if not success:
            error_msg = (
                "Migrations-Upgrade fehlgeschlagen! "
                "Bitte manuell ausführen: alembic upgrade head"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.info("✓ Auto-Upgrade erfolgreich abgeschlossen")
    else:
        logger.warning(
            "⚠️  Auto-Upgrade ist deaktiviert. "
            "Bitte manuell ausführen: alembic upgrade head"
        )


def get_current_db_version() -> Optional[str]:
    """
    Gibt die aktuelle Datenbank-Version zurück.

    Returns:
        Version-String oder None
    """
    try:
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and result.stdout:
            # Parse erste Zeile
            first_line = result.stdout.strip().split('\n')[0]
            parts = first_line.split()
            if parts:
                return parts[0]

        return None

    except Exception as e:
        logger.error(f"Fehler beim Abrufen der DB-Version: {e}")
        return None
