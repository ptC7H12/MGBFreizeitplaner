"""Tests für PriceCalculator Service"""
import pytest
from app.services.price_calculator import PriceCalculator


@pytest.fixture
def sample_ruleset_data():
    """Beispiel-Regelwerk für Tests"""
    return {
        "age_groups": [
            {"name": "Kinder 6-11", "min_age": 6, "max_age": 11, "price": 150.0},
            {"name": "Jugendliche 12-17", "min_age": 12, "max_age": 17, "price": 180.0},
            {"name": "Erwachsene 18+", "min_age": 18, "max_age": 999, "price": 220.0}
        ],
        "role_discounts": {
            "betreuer": {"discount_percent": 100, "description": "Kostenlos"},
            "kueche": {"discount_percent": 50, "description": "50% Rabatt"}
        },
        "family_discount": {
            "enabled": True,
            "second_child_percent": 10,
            "third_plus_child_percent": 20
        }
    }


@pytest.mark.unit
class TestPriceCalculator:
    """Unit-Tests für PriceCalculator"""

    def test_base_price_for_child(self, sample_ruleset_data):
        """Test: Basispreis für Kind (6-11 Jahre)"""
        price = PriceCalculator.calculate_participant_price(
            age=8,
            role_name="kind",
            ruleset_data=sample_ruleset_data,
            family_children_count=1
        )
        assert price == 150.0

    def test_base_price_for_teenager(self, sample_ruleset_data):
        """Test: Basispreis für Jugendlichen (12-17 Jahre)"""
        price = PriceCalculator.calculate_participant_price(
            age=14,
            role_name="kind",
            ruleset_data=sample_ruleset_data,
            family_children_count=1
        )
        assert price == 180.0

    def test_base_price_for_adult(self, sample_ruleset_data):
        """Test: Basispreis für Erwachsenen (18+ Jahre)"""
        price = PriceCalculator.calculate_participant_price(
            age=25,
            role_name="teilnehmer",
            ruleset_data=sample_ruleset_data,
            family_children_count=1
        )
        assert price == 220.0

    def test_role_discount_betreuer(self, sample_ruleset_data):
        """Test: Rollenrabatt für Betreuer (100%)"""
        price = PriceCalculator.calculate_participant_price(
            age=25,
            role_name="betreuer",
            ruleset_data=sample_ruleset_data,
            family_children_count=1
        )
        # 220 - 100% = 0
        assert price == 0.0

    def test_role_discount_kueche(self, sample_ruleset_data):
        """Test: Rollenrabatt für Küche (50%)"""
        price = PriceCalculator.calculate_participant_price(
            age=25,
            role_name="kueche",
            ruleset_data=sample_ruleset_data,
            family_children_count=1
        )
        # 220 - 50% = 110
        assert price == 110.0

    def test_family_discount_second_child(self, sample_ruleset_data):
        """Test: Familienrabatt für 2. Kind (10%)"""
        price = PriceCalculator.calculate_participant_price(
            age=8,
            role_name="kind",
            ruleset_data=sample_ruleset_data,
            family_children_count=2
        )
        # 150 - 10% = 135
        assert price == 135.0

    def test_family_discount_third_child(self, sample_ruleset_data):
        """Test: Familienrabatt für 3. Kind (20%)"""
        price = PriceCalculator.calculate_participant_price(
            age=8,
            role_name="kind",
            ruleset_data=sample_ruleset_data,
            family_children_count=3
        )
        # 150 - 20% = 120
        assert price == 120.0

    def test_combined_role_and_family_discount(self, sample_ruleset_data):
        """Test: Kombination von Rollen- und Familienrabatt"""
        # WICHTIG: Rabatte werden BEIDE vom Basispreis berechnet (nicht gestapelt)
        price = PriceCalculator.calculate_participant_price(
            age=8,
            role_name="kueche",
            ruleset_data=sample_ruleset_data,
            family_children_count=2
        )
        # Basispreis: 150
        # Rollenrabatt (50%): 75
        # Nach Rollenrabatt: 75
        # Familienrabatt (10% vom Preis nach Rollenrabatt): 7.5
        # Final: 75 - 7.5 = 67.5
        assert price == 67.5

    def test_no_family_discount_for_first_child(self, sample_ruleset_data):
        """Test: Kein Familienrabatt für 1. Kind"""
        price = PriceCalculator.calculate_participant_price(
            age=8,
            role_name="kind",
            ruleset_data=sample_ruleset_data,
            family_children_count=1
        )
        assert price == 150.0

    def test_family_discount_disabled(self, sample_ruleset_data):
        """Test: Familienrabatt deaktiviert"""
        ruleset_data = sample_ruleset_data.copy()
        ruleset_data["family_discount"]["enabled"] = False

        price = PriceCalculator.calculate_participant_price(
            age=8,
            role_name="kind",
            ruleset_data=ruleset_data,
            family_children_count=2
        )
        # Kein Familienrabatt, also Basispreis
        assert price == 150.0

    def test_price_with_breakdown(self, sample_ruleset_data):
        """Test: Preis-Breakdown-Berechnung"""
        breakdown = PriceCalculator.calculate_participant_price_with_breakdown(
            age=14,
            role_name="kind",
            role_display_name="Kind",
            ruleset_data=sample_ruleset_data,
            family_children_count=1,
            discount_percent=0.0,
            discount_reason=None,
            manual_price_override=None
        )

        assert breakdown['base_price'] == 180.0
        assert breakdown['role_discount_percent'] == 0.0
        assert breakdown['family_discount_percent'] == 0.0
        assert breakdown['final_price'] == 180.0
        assert breakdown['has_discounts'] == False

    def test_price_with_breakdown_manual_override(self, sample_ruleset_data):
        """Test: Preis-Breakdown mit manuellem Preis"""
        breakdown = PriceCalculator.calculate_participant_price_with_breakdown(
            age=14,
            role_name="kind",
            role_display_name="Kind",
            ruleset_data=sample_ruleset_data,
            family_children_count=1,
            discount_percent=0.0,
            discount_reason="Sozialrabatt",
            manual_price_override=100.0
        )

        assert breakdown['final_price'] == 100.0
        assert breakdown['manual_price_override'] == 100.0
        assert breakdown['has_discounts'] == True
        assert len(breakdown['discount_reasons']) == 2
        assert "Manueller Preis: 100.00 €" in breakdown['discount_reasons']
        assert "Grund: Sozialrabatt" in breakdown['discount_reasons']

    def test_price_with_breakdown_additional_discount(self, sample_ruleset_data):
        """Test: Preis-Breakdown mit zusätzlichem Rabatt"""
        breakdown = PriceCalculator.calculate_participant_price_with_breakdown(
            age=14,
            role_name="kind",
            role_display_name="Kind",
            ruleset_data=sample_ruleset_data,
            family_children_count=1,
            discount_percent=15.0,
            discount_reason="BuT-Förderung",
            manual_price_override=None
        )

        assert breakdown['base_price'] == 180.0
        assert breakdown['manual_discount_percent'] == 15.0
        # 180 - 15% = 153
        assert breakdown['manual_discount_amount'] == 27.0
        assert breakdown['final_price'] == 153.0
        assert breakdown['has_discounts'] == True
        assert "Zusätzlicher Rabatt: 15%" in str(breakdown['discount_reasons'])

    def test_price_with_breakdown_all_discounts(self, sample_ruleset_data):
        """Test: Preis-Breakdown mit allen Rabatten kombiniert"""
        breakdown = PriceCalculator.calculate_participant_price_with_breakdown(
            age=8,
            role_name="kueche",
            role_display_name="Küche",
            ruleset_data=sample_ruleset_data,
            family_children_count=2,
            discount_percent=5.0,
            discount_reason="Frühbucher",
            manual_price_override=None
        )

        # Basispreis: 150
        assert breakdown['base_price'] == 150.0

        # Rollenrabatt: 50% = 75
        assert breakdown['role_discount_percent'] == 50.0
        assert breakdown['role_discount_amount'] == 75.0
        assert breakdown['price_after_role_discount'] == 75.0

        # Familienrabatt: 10% von 75 = 7.5
        assert breakdown['family_discount_percent'] == 10.0
        assert breakdown['family_discount_amount'] == 7.5
        assert breakdown['price_after_family_discount'] == 67.5

        # Zusätzlicher Rabatt: 5% von 67.5 = 3.375
        assert breakdown['manual_discount_percent'] == 5.0
        assert breakdown['manual_discount_amount'] == pytest.approx(3.375, abs=0.01)

        # Endpreis: 67.5 - 3.375 = 64.125 -> 64.12
        assert breakdown['final_price'] == pytest.approx(64.12, abs=0.01)
        assert breakdown['has_discounts'] == True

    def test_empty_ruleset(self):
        """Test: Leeres Regelwerk"""
        price = PriceCalculator.calculate_participant_price(
            age=14,
            role_name="kind",
            ruleset_data={
                "age_groups": [],
                "role_discounts": {},
                "family_discount": {}
            },
            family_children_count=1
        )
        # Kein Basispreis definiert -> 0
        assert price == 0.0

    def test_age_boundary_conditions(self, sample_ruleset_data):
        """Test: Alters-Grenzwerte"""
        # Genau 11 Jahre (obere Grenze Kinder)
        price_11 = PriceCalculator.calculate_participant_price(
            age=11,
            role_name="kind",
            ruleset_data=sample_ruleset_data,
            family_children_count=1
        )
        assert price_11 == 150.0

        # Genau 12 Jahre (untere Grenze Jugendliche)
        price_12 = PriceCalculator.calculate_participant_price(
            age=12,
            role_name="kind",
            ruleset_data=sample_ruleset_data,
            family_children_count=1
        )
        assert price_12 == 180.0

        # Genau 17 Jahre (obere Grenze Jugendliche)
        price_17 = PriceCalculator.calculate_participant_price(
            age=17,
            role_name="kind",
            ruleset_data=sample_ruleset_data,
            family_children_count=1
        )
        assert price_17 == 180.0

        # Genau 18 Jahre (untere Grenze Erwachsene)
        price_18 = PriceCalculator.calculate_participant_price(
            age=18,
            role_name="teilnehmer",
            ruleset_data=sample_ruleset_data,
            family_children_count=1
        )
        assert price_18 == 220.0
