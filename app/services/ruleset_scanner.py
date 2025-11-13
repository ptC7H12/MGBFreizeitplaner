"""Ruleset Scanner Service - Automatisches Scannen von Regelwerk-Verzeichnissen"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from app.services.ruleset_parser import RulesetParser

logger = logging.getLogger(__name__)


class RulesetScanner:
    """Service zum Scannen von Verzeichnissen nach Regelwerk-YAML-Dateien"""

    @staticmethod
    def scan_directory(directory_path: Path, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Scannt ein Verzeichnis nach YAML-Dateien und validiert sie als Rulesets

        Args:
            directory_path: Pfad zum zu scannenden Verzeichnis
            recursive: Ob Unterverzeichnisse durchsucht werden sollen

        Returns:
            Liste von Dictionaries mit Ruleset-Informationen:
            {
                "file_path": Path,
                "relative_path": str,
                "name": str,
                "type": str,
                "valid_from": str,
                "valid_until": str,
                "is_valid": bool,
                "error": str (optional)
            }
        """
        rulesets = []

        if not directory_path.exists() or not directory_path.is_dir():
            logger.warning(f"Directory does not exist: {directory_path}")
            return rulesets

        # Finde alle YAML-Dateien
        if recursive:
            yaml_files = list(directory_path.rglob("*.yaml")) + list(directory_path.rglob("*.yml"))
        else:
            yaml_files = list(directory_path.glob("*.yaml")) + list(directory_path.glob("*.yml"))

        logger.info(f"Found {len(yaml_files)} YAML files in {directory_path}")

        for yaml_file in yaml_files:
            ruleset_info = RulesetScanner._parse_ruleset_file(yaml_file, directory_path)
            if ruleset_info:
                rulesets.append(ruleset_info)

        return rulesets

    @staticmethod
    def _parse_ruleset_file(yaml_file: Path, base_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parst eine einzelne YAML-Datei und validiert sie als Ruleset

        Args:
            yaml_file: Pfad zur YAML-Datei
            base_path: Basis-Pfad für relative Pfadangabe

        Returns:
            Dictionary mit Ruleset-Informationen oder None bei Fehler
        """
        try:
            parser = RulesetParser()
            data = parser.parse_yaml_file(yaml_file)

            # Validieren
            is_valid, error_msg = parser.validate_ruleset(data)

            relative_path = yaml_file.relative_to(base_path)

            ruleset_info = {
                "file_path": str(yaml_file),
                "relative_path": str(relative_path),
                "name": data.get("name", "Unbekannt"),
                "type": data.get("type", "unknown"),
                "description": data.get("description"),
                "valid_from": data.get("valid_from"),
                "valid_until": data.get("valid_until"),
                "is_valid": is_valid,
                "has_role_discounts": bool(data.get("role_discounts")),
                "has_family_discount": bool(data.get("family_discount")),
                "age_groups_count": len(data.get("age_groups", [])),
            }

            if not is_valid:
                ruleset_info["error"] = error_msg
                logger.warning(f"Invalid ruleset in {yaml_file}: {error_msg}")

            return ruleset_info

        except Exception as e:
            logger.error(f"Error parsing {yaml_file}: {e}")
            return {
                "file_path": str(yaml_file),
                "relative_path": str(yaml_file.relative_to(base_path)),
                "name": yaml_file.stem,
                "type": "unknown",
                "is_valid": False,
                "error": str(e)
            }

    @staticmethod
    def get_default_ruleset_directories() -> List[Path]:
        """
        Gibt eine Liste von Standard-Verzeichnissen zurück, die nach Rulesets durchsucht werden sollen

        Returns:
            Liste von Path-Objekten
        """
        from app.config import settings

        directories = []

        # 1. Projekt-eigenes rulesets/ Verzeichnis
        project_rulesets = Path("rulesets")
        if project_rulesets.exists():
            directories.append(project_rulesets)

        # 2. Konfiguriertes Verzeichnis aus Settings (falls vorhanden)
        if hasattr(settings, 'ruleset_directory'):
            custom_dir = Path(settings.ruleset_directory)
            if custom_dir.exists() and custom_dir not in directories:
                directories.append(custom_dir)

        return directories

    @staticmethod
    def scan_all_default_directories() -> Dict[str, List[Dict[str, Any]]]:
        """
        Scannt alle Standard-Verzeichnisse nach Rulesets

        Returns:
            Dictionary mit Verzeichnis-Pfad als Key und Liste von Rulesets als Value
        """
        all_rulesets = {}

        for directory in RulesetScanner.get_default_ruleset_directories():
            rulesets = RulesetScanner.scan_directory(directory)
            if rulesets:
                all_rulesets[str(directory)] = rulesets

        return all_rulesets

    @staticmethod
    def filter_valid_rulesets(rulesets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtert nur valide Rulesets aus einer Liste

        Args:
            rulesets: Liste von Ruleset-Informationen

        Returns:
            Liste nur der validen Rulesets
        """
        return [r for r in rulesets if r.get("is_valid", False)]
