"""Backup Service für Datenbank-Backups"""
import shutil
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BackupService:
    """Service für die Verwaltung von Datenbank-Backups"""

    def __init__(self, db_path: str = "./freizeit_kassen.db", backup_dir: str = "./backups"):
        """
        Initialisiert den Backup-Service

        Args:
            db_path: Pfad zur Datenbank-Datei
            backup_dir: Verzeichnis für Backups
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True, parents=True)

    def create_backup(self, description: str = "") -> Dict[str, Any]:
        """
        Erstellt ein Backup der Datenbank

        Args:
            description: Beschreibung des Backups

        Returns:
            Dictionary mit Backup-Info
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Datenbank-Datei nicht gefunden: {self.db_path}")

        # Backup-Dateiname mit Zeitstempel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_filename

        # Kopiere Datenbank
        shutil.copy2(self.db_path, backup_path)

        # Meta-Datei erstellen (optional)
        meta_path = self.backup_dir / f"backup_{timestamp}.meta"
        with open(meta_path, 'w', encoding='utf-8') as f:
            f.write(f"created: {datetime.now().isoformat()}\n")
            f.write(f"description: {description}\n")
            f.write(f"size: {backup_path.stat().st_size}\n")

        logger.info(f"Backup erstellt: {backup_filename}")

        return {
            "filename": backup_filename,
            "path": str(backup_path),
            "size": backup_path.stat().st_size,
            "created": datetime.now(),
            "description": description
        }

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        Listet alle vorhandenen Backups auf

        Returns:
            Liste von Backup-Informationen
        """
        backups = []

        for backup_file in sorted(self.backup_dir.glob("backup_*.db"), reverse=True):
            # Lese Meta-Datei falls vorhanden
            meta_file = backup_file.with_suffix('.meta')
            description = ""
            if meta_file.exists():
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('description:'):
                                description = line.split(':', 1)[1].strip()
                except Exception as e:
                    logger.warning(f"Konnte Meta-Datei nicht lesen: {e}")

            backups.append({
                "filename": backup_file.name,
                "path": str(backup_file),
                "size": backup_file.stat().st_size,
                "created": datetime.fromtimestamp(backup_file.stat().st_mtime),
                "description": description
            })

        return backups

    def delete_backup(self, filename: str) -> bool:
        """
        Löscht ein Backup

        Args:
            filename: Name der Backup-Datei

        Returns:
            True bei Erfolg
        """
        backup_path = self.backup_dir / filename
        meta_path = backup_path.with_suffix('.meta')

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup nicht gefunden: {filename}")

        # Lösche Backup und Meta-Datei
        backup_path.unlink()
        if meta_path.exists():
            meta_path.unlink()

        logger.info(f"Backup gelöscht: {filename}")
        return True

    def cleanup_old_backups(self, max_age_days: int = 30, keep_min: int = 5) -> int:
        """
        Löscht alte Backups

        Args:
            max_age_days: Maximales Alter in Tagen
            keep_min: Mindestanzahl zu behaltender Backups

        Returns:
            Anzahl gelöschter Backups
        """
        backups = self.list_backups()
        deleted_count = 0

        # Behalte mindestens keep_min Backups
        if len(backups) <= keep_min:
            return 0

        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        for backup in backups[keep_min:]:  # Überspringe die neuesten keep_min
            if backup['created'] < cutoff_date:
                try:
                    self.delete_backup(backup['filename'])
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Fehler beim Löschen von {backup['filename']}: {e}")

        logger.info(f"Alte Backups aufgeräumt: {deleted_count} gelöscht")
        return deleted_count

    def restore_backup(self, filename: str) -> bool:
        """
        Stellt ein Backup wieder her

        WARNUNG: Überschreibt die aktuelle Datenbank!

        Args:
            filename: Name der Backup-Datei

        Returns:
            True bei Erfolg
        """
        backup_path = self.backup_dir / filename

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup nicht gefunden: {filename}")

        # Erstelle Sicherheits-Backup der aktuellen DB
        safety_backup = self.db_path.with_suffix('.db.before_restore')
        if self.db_path.exists():
            shutil.copy2(self.db_path, safety_backup)

        try:
            # Stelle Backup wieder her
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"Backup wiederhergestellt: {filename}")
            return True
        except Exception as e:
            # Bei Fehler: Stelle alte DB wieder her
            if safety_backup.exists():
                shutil.copy2(safety_backup, self.db_path)
            logger.error(f"Fehler beim Wiederherstellen: {e}")
            raise

    def get_backup_stats(self) -> Dict[str, Any]:
        """
        Liefert Statistiken über Backups

        Returns:
            Dictionary mit Backup-Statistiken
        """
        backups = self.list_backups()

        if not backups:
            return {
                "count": 0,
                "total_size": 0,
                "oldest": None,
                "newest": None
            }

        total_size = sum(b['size'] for b in backups)

        return {
            "count": len(backups),
            "total_size": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "oldest": backups[-1]['created'] if backups else None,
            "newest": backups[0]['created'] if backups else None
        }
