"""Regelwerk-Parser Service"""
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RulesetParser:
    """Service zum Parsen und Validieren von Regelwerk-YAML-Dateien"""

    @staticmethod
    def parse_yaml_file(file_path: Path) -> Dict[str, Any]:
        """
        Parst eine YAML-Datei und gibt die Daten zurück

        Args:
            file_path: Pfad zur YAML-Datei

        Returns:
            Dictionary mit Regelwerk-Daten

        Raises:
            FileNotFoundError: Wenn die Datei nicht existiert
            yaml.YAMLError: Wenn die YAML-Datei ungültig ist
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        return data

    @staticmethod
    def parse_yaml_string(yaml_string: str) -> Dict[str, Any]:
        """
        Parst einen YAML-String und gibt die Daten zurück

        Args:
            yaml_string: YAML als String

        Returns:
            Dictionary mit Regelwerk-Daten
        """
        return yaml.safe_load(yaml_string)

    @staticmethod
    def validate_ruleset(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validiert ein Regelwerk auf Vollständigkeit und Korrektheit

        Args:
            data: Regelwerk-Daten

        Returns:
            Tuple (is_valid, error_message)
        """
        # Pflichtfelder prüfen
        required_fields = ["name", "type", "valid_from", "valid_until", "age_groups"]
        for field in required_fields:
            if field not in data:
                return False, f"Pflichtfeld '{field}' fehlt"

        # Altersgruppen prüfen
        age_groups = data.get("age_groups", [])
        if not isinstance(age_groups, list) or len(age_groups) == 0:
            return False, "Mindestens eine Altersgruppe muss definiert sein"

        for group in age_groups:
            if "min_age" not in group or "max_age" not in group or "price" not in group:
                return False, "Altersgruppen müssen 'min_age', 'max_age' und 'price' enthalten"

        # Datumsformat prüfen
        try:
            datetime.strptime(data["valid_from"], "%Y-%m-%d")
            datetime.strptime(data["valid_until"], "%Y-%m-%d")
        except ValueError:
            return False, "Datumsfelder müssen im Format YYYY-MM-DD vorliegen"

        return True, None

    @staticmethod
    def export_ruleset_to_yaml(ruleset) -> str:
        """
        Exportiert ein Ruleset-Objekt zurück in YAML-Format

        Args:
            ruleset: Ruleset-Objekt aus der Datenbank

        Returns:
            YAML-String
        """
        data = {
            "name": ruleset.name,
            "type": ruleset.ruleset_type,
            "description": ruleset.description,
            "valid_from": ruleset.valid_from.strftime("%Y-%m-%d"),
            "valid_until": ruleset.valid_until.strftime("%Y-%m-%d"),
            "age_groups": ruleset.age_groups,
        }

        # Optionale Felder nur hinzufügen wenn vorhanden
        if ruleset.role_discounts:
            data["role_discounts"] = ruleset.role_discounts

        if ruleset.family_discount:
            data["family_discount"] = ruleset.family_discount

        return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)

    @staticmethod
    def create_example_yaml() -> str:
        """Erstellt ein Beispiel-YAML für ein Regelwerk"""
        example = {
            "name": "Kinderfreizeit 2024",
            "type": "kinder",
            "valid_from": "2024-01-01",
            "valid_until": "2024-12-31",
            "age_groups": [
                {"min_age": 6, "max_age": 9, "price": 140.00},
                {"min_age": 10, "max_age": 12, "price": 150.00}
            ],
            "role_discounts": {
                "betreuer": {
                    "discount_percent": 50,
                    "max_count": 10
                },
                "kueche": {
                    "discount_percent": 100,
                    "max_count": 2
                }
            },
            "family_discount": {
                "enabled": True,
                "second_child_percent": 10,
                "third_plus_child_percent": 20
            }
        }
        return yaml.dump(example, allow_unicode=True, default_flow_style=False, sort_keys=False)
