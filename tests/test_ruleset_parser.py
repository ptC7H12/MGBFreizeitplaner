"""Tests für RulesetParser Service"""
import pytest
import yaml
from pathlib import Path
from tempfile import NamedTemporaryFile

from app.services.ruleset_parser import RulesetParser


@pytest.fixture
def valid_ruleset_dict():
    """Gültiges Regelwerk als Dictionary"""
    return {
        "name": "Standard-Regelwerk 2024",
        "type": "standard",
        "valid_from": "2024-01-01",
        "valid_until": "2024-12-31",
        "age_groups": [
            {"name": "Kinder 6-11", "min_age": 6, "max_age": 11, "price": 150.0},
            {"name": "Jugendliche 12-17", "min_age": 12, "max_age": 17, "price": 180.0}
        ],
        "role_discounts": {
            "betreuer": {"discount_percent": 100, "description": "Kostenlos"}
        },
        "family_discount": {
            "enabled": True,
            "second_child_percent": 10,
            "third_plus_child_percent": 20
        }
    }


@pytest.fixture
def valid_ruleset_yaml():
    """Gültiges Regelwerk als YAML-String"""
    return """
name: Standard-Regelwerk 2024
type: standard
valid_from: "2024-01-01"
valid_until: "2024-12-31"
age_groups:
  - name: Kinder 6-11
    min_age: 6
    max_age: 11
    price: 150.0
  - name: Jugendliche 12-17
    min_age: 12
    max_age: 17
    price: 180.0
role_discounts:
  betreuer:
    discount_percent: 100
    description: Kostenlos
family_discount:
  enabled: true
  second_child_percent: 10
  third_plus_child_percent: 20
"""


@pytest.mark.unit
class TestRulesetParser:
    """Unit-Tests für RulesetParser"""

    def test_parse_yaml_string(self, valid_ruleset_yaml):
        """Test: YAML-String parsen"""
        data = RulesetParser.parse_yaml_string(valid_ruleset_yaml)

        assert data["name"] == "Standard-Regelwerk 2024"
        assert data["type"] == "standard"
        assert len(data["age_groups"]) == 2
        assert data["age_groups"][0]["price"] == 150.0

    def test_parse_yaml_file(self, valid_ruleset_yaml):
        """Test: YAML-Datei parsen"""
        # Temporäre Datei erstellen
        with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write(valid_ruleset_yaml)
            temp_path = Path(f.name)

        try:
            data = RulesetParser.parse_yaml_file(temp_path)

            assert data["name"] == "Standard-Regelwerk 2024"
            assert len(data["age_groups"]) == 2
        finally:
            temp_path.unlink()  # Datei löschen

    def test_parse_yaml_file_not_found(self):
        """Test: Nicht existierende Datei"""
        with pytest.raises(FileNotFoundError):
            RulesetParser.parse_yaml_file(Path("/non/existent/file.yaml"))

    def test_parse_invalid_yaml(self):
        """Test: Ungültiges YAML"""
        invalid_yaml = """
name: Test
invalid: [yaml: structure
"""
        with pytest.raises(yaml.YAMLError):
            RulesetParser.parse_yaml_string(invalid_yaml)

    def test_validate_valid_ruleset(self, valid_ruleset_dict):
        """Test: Validierung eines gültigen Regelwerks"""
        is_valid, error = RulesetParser.validate_ruleset(valid_ruleset_dict)

        assert is_valid == True
        assert error is None

    def test_validate_missing_name(self, valid_ruleset_dict):
        """Test: Fehlendes Pflichtfeld 'name'"""
        del valid_ruleset_dict["name"]

        is_valid, error = RulesetParser.validate_ruleset(valid_ruleset_dict)

        assert is_valid == False
        assert "Pflichtfeld 'name' fehlt" in error

    def test_validate_missing_type(self, valid_ruleset_dict):
        """Test: Fehlendes Pflichtfeld 'type'"""
        del valid_ruleset_dict["type"]

        is_valid, error = RulesetParser.validate_ruleset(valid_ruleset_dict)

        assert is_valid == False
        assert "Pflichtfeld 'type' fehlt" in error

    def test_validate_missing_valid_from(self, valid_ruleset_dict):
        """Test: Fehlendes Pflichtfeld 'valid_from'"""
        del valid_ruleset_dict["valid_from"]

        is_valid, error = RulesetParser.validate_ruleset(valid_ruleset_dict)

        assert is_valid == False
        assert "Pflichtfeld 'valid_from' fehlt" in error

    def test_validate_missing_age_groups(self, valid_ruleset_dict):
        """Test: Fehlende Altersgruppen"""
        del valid_ruleset_dict["age_groups"]

        is_valid, error = RulesetParser.validate_ruleset(valid_ruleset_dict)

        assert is_valid == False
        assert "Pflichtfeld 'age_groups' fehlt" in error

    def test_validate_empty_age_groups(self, valid_ruleset_dict):
        """Test: Leere Altersgruppen-Liste"""
        valid_ruleset_dict["age_groups"] = []

        is_valid, error = RulesetParser.validate_ruleset(valid_ruleset_dict)

        assert is_valid == False
        assert "Mindestens eine Altersgruppe muss definiert sein" in error

    def test_validate_age_group_missing_fields(self, valid_ruleset_dict):
        """Test: Altersgruppe mit fehlenden Feldern"""
        valid_ruleset_dict["age_groups"][0] = {
            "name": "Kinder",
            "min_age": 6
            # max_age und price fehlen
        }

        is_valid, error = RulesetParser.validate_ruleset(valid_ruleset_dict)

        assert is_valid == False
        assert "Altersgruppen müssen 'min_age', 'max_age' und 'price' enthalten" in error

    def test_validate_invalid_date_format(self, valid_ruleset_dict):
        """Test: Ungültiges Datumsformat"""
        valid_ruleset_dict["valid_from"] = "01.01.2024"  # Deutsches Format

        is_valid, error = RulesetParser.validate_ruleset(valid_ruleset_dict)

        assert is_valid == False
        assert "Datumsfelder müssen im Format YYYY-MM-DD vorliegen" in error

    def test_validate_age_groups_not_list(self, valid_ruleset_dict):
        """Test: age_groups ist kein Array"""
        valid_ruleset_dict["age_groups"] = "not a list"

        is_valid, error = RulesetParser.validate_ruleset(valid_ruleset_dict)

        assert is_valid == False
        assert "Mindestens eine Altersgruppe muss definiert sein" in error

    def test_export_ruleset_to_yaml(self):
        """Test: Ruleset zu YAML exportieren"""
        # Mock Ruleset-Objekt
        class MockRuleset:
            name = "Test-Regelwerk"
            ruleset_type = "standard"
            valid_from = "2024-01-01"
            valid_until = "2024-12-31"
            age_groups = [
                {"name": "Kinder", "min_age": 6, "max_age": 11, "price": 150.0}
            ]
            role_discounts = {
                "betreuer": {"discount_percent": 100}
            }
            family_discount = {
                "enabled": True,
                "second_child_percent": 10
            }
            description = "Test-Beschreibung"

        ruleset = MockRuleset()
        yaml_string = RulesetParser.export_ruleset_to_yaml(ruleset)

        # YAML-String parsen
        data = yaml.safe_load(yaml_string)

        assert data["name"] == "Test-Regelwerk"
        assert data["type"] == "standard"
        assert len(data["age_groups"]) == 1
        assert data["age_groups"][0]["price"] == 150.0

    def test_roundtrip_yaml_conversion(self, valid_ruleset_yaml):
        """Test: YAML -> Dict -> YAML Roundtrip"""
        # YAML zu Dict
        data1 = RulesetParser.parse_yaml_string(valid_ruleset_yaml)

        # Validierung
        is_valid, error = RulesetParser.validate_ruleset(data1)
        assert is_valid == True

        # Dict zu YAML (Mock Ruleset)
        class MockRuleset:
            def __init__(self, data):
                self.name = data["name"]
                self.ruleset_type = data["type"]
                self.valid_from = data["valid_from"]
                self.valid_until = data["valid_until"]
                self.age_groups = data["age_groups"]
                self.role_discounts = data.get("role_discounts", {})
                self.family_discount = data.get("family_discount", {})
                self.description = data.get("description", "")

        ruleset = MockRuleset(data1)
        yaml_string2 = RulesetParser.export_ruleset_to_yaml(ruleset)

        # Zurück zu Dict
        data2 = RulesetParser.parse_yaml_string(yaml_string2)

        # Vergleiche kritische Felder
        assert data1["name"] == data2["name"]
        assert data1["type"] == data2["type"]
        assert len(data1["age_groups"]) == len(data2["age_groups"])
        assert data1["age_groups"][0]["price"] == data2["age_groups"][0]["price"]

    def test_parse_yaml_with_unicode(self):
        """Test: YAML mit Unicode-Zeichen"""
        yaml_string = """
name: Regelwerk für Kinderfreizeit 2024 🎉
type: standard
valid_from: "2024-01-01"
valid_until: "2024-12-31"
age_groups:
  - name: Kinder 6-11 ✨
    min_age: 6
    max_age: 11
    price: 150.0
description: "Enthält Sonderzeichen: äöüßÄÖÜ"
"""
        data = RulesetParser.parse_yaml_string(yaml_string)

        assert "🎉" in data["name"]
        assert "✨" in data["age_groups"][0]["name"]
        assert "äöüß" in data["description"]

    def test_parse_yaml_with_comments(self):
        """Test: YAML mit Kommentaren"""
        yaml_string = """
# Dies ist ein Kommentar
name: Test-Regelwerk  # Inline-Kommentar
type: standard
valid_from: "2024-01-01"
valid_until: "2024-12-31"
# Altersgruppen-Definition
age_groups:
  - name: Kinder
    min_age: 6  # Minimales Alter
    max_age: 11  # Maximales Alter
    price: 150.0
"""
        data = RulesetParser.parse_yaml_string(yaml_string)

        # Kommentare sollten ignoriert werden
        assert data["name"] == "Test-Regelwerk"
        assert data["age_groups"][0]["min_age"] == 6
