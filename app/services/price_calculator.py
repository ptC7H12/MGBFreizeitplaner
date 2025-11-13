"""Preisberechnungs-Service"""
from typing import Optional, Dict, Any
from datetime import date


class PriceCalculator:
    """Service für die Berechnung von Teilnehmerpreisen"""

    @staticmethod
    def calculate_participant_price(
        age: int,
        role_name: str,
        ruleset_data: Dict[str, Any],
        family_children_count: int = 1
    ) -> float:
        """
        Berechnet den Preis für einen Teilnehmer basierend auf Regelwerk

        Args:
            age: Alter des Teilnehmers
            role_name: Name der Rolle (z.B. "betreuer", "kind")
            ruleset_data: Regelwerk-Daten (age_groups, role_discounts, etc.)
            family_children_count: Position in der Familie (1=erstes Kind, 2=zweites, etc.)

        Returns:
            Berechneter Preis in Euro
        """
        # Basispreis aus Altersgruppen ermitteln
        base_price = PriceCalculator._get_base_price_by_age(age, ruleset_data.get("age_groups", []))

        # Rollenrabatt ermitteln
        role_discount_percent = PriceCalculator._get_role_discount(
            role_name, ruleset_data.get("role_discounts", {})
        )

        # Familienrabatt ermitteln
        family_discount_percent = PriceCalculator._get_family_discount(
            family_children_count, ruleset_data.get("family_discount", {})
        )

        # Alle Rabatte vom Basispreis berechnen (nicht gestapelt!)
        role_discount_amount = base_price * (role_discount_percent / 100)
        family_discount_amount = base_price * (family_discount_percent / 100)

        # Endpreis = Basispreis - Summe aller Rabatte
        final_price = base_price - role_discount_amount - family_discount_amount

        return round(final_price, 2)

    @staticmethod
    def _get_base_price_by_age(age: int, age_groups: list) -> float:
        """Ermittelt den Basispreis basierend auf dem Alter"""
        for group in age_groups:
            min_age = group.get("min_age", 0)
            max_age = group.get("max_age", 999)
            if min_age <= age <= max_age:
                return float(group.get("price", 0))
        return 0.0

    @staticmethod
    def _get_role_discount(role_name: str, role_discounts: dict) -> float:
        """Ermittelt den Rollenrabatt in Prozent"""
        role_name_lower = role_name.lower()
        if role_name_lower in role_discounts:
            return float(role_discounts[role_name_lower].get("discount_percent", 0))
        return 0.0

    @staticmethod
    def _get_family_discount(child_position: int, family_discount_config: dict) -> float:
        """Ermittelt den Familienrabatt in Prozent"""
        if not family_discount_config.get("enabled", False):
            return 0.0

        if child_position == 1:
            return 0.0  # Erstes Kind: kein Rabatt
        elif child_position == 2:
            return float(family_discount_config.get("second_child_percent", 0))
        else:  # 3. Kind und weitere
            return float(family_discount_config.get("third_plus_child_percent", 0))
