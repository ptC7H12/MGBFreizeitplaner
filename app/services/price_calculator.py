"""Preisberechnungs-Service"""
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import date

logger = logging.getLogger(__name__)


class PriceCalculator:
    """Service für die Berechnung von Teilnehmerpreisen"""

    @staticmethod
    def calculate_participant_price(
        age: int,
        role_name: Optional[str],  # Rolle ist optional
        ruleset_data: Dict[str, Any],
        family_children_count: int = 1
    ) -> float:
        """
        Berechnet den Preis für einen Teilnehmer basierend auf Regelwerk

        Args:
            age: Alter des Teilnehmers
            role_name: Optional Name der Rolle (z.B. "betreuer", "kind"). None = keine Rolle
            ruleset_data: Regelwerk-Daten (age_groups, role_discounts, etc.)
            family_children_count: Position in der Familie (1=erstes Kind, 2=zweites, etc.)

        Returns:
            Berechneter Preis in Euro
        """
        # Basispreis aus Altersgruppen ermitteln
        base_price = PriceCalculator._get_base_price_by_age(age, ruleset_data.get("age_groups", []))

        # Rollenrabatt ermitteln (nur wenn Rolle vorhanden)
        role_discount_percent = 0.0
        if role_name:
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
        """
        Ermittelt den Basispreis basierend auf dem Alter.

        Args:
            age: Alter des Teilnehmers
            age_groups: Liste der Altersgruppen mit base_price

        Returns:
            Basispreis für die Altersgruppe
        """
        for group in age_groups:
            min_age = group.get("min_age", 0)
            max_age = group.get("max_age", 999)
            if min_age <= age <= max_age:
                # Neues Format: base_price direkt aus age_group
                if "base_price" in group:
                    return float(group.get("base_price", 0))
                # Legacy Format: price als Fallback
                return float(group.get("price", 0))
        return 0.0

    @staticmethod
    def _get_role_discount(role_name: Optional[str], role_discounts: dict) -> float:
        """
        Ermittelt den Rollenrabatt in Prozent.

        Args:
            role_name: Optional Name der Rolle
            role_discounts: Dictionary mit Rollenrabatten

        Returns:
            Rabatt in Prozent (0.0 wenn keine Rolle oder kein Rabatt)
        """
        if not role_name:
            return 0.0

        role_name_lower = role_name.lower()
        if role_name_lower in role_discounts:
            return float(role_discounts[role_name_lower].get("discount_percent", 0))
        return 0.0

    @staticmethod
    def _get_family_discount(child_position: int, family_discount_config: dict) -> float:
        """
        Ermittelt den Familienrabatt in Prozent

        Unterstützt Rabatte für:
        - Erstes Kind (first_child_percent, optional, Standard: 0%)
        - Zweites Kind (second_child_percent)
        - Drittes und weitere Kinder (third_plus_child_percent)
        """
        if not family_discount_config.get("enabled", False):
            return 0.0

        if child_position == 1:
            # Erstes Kind: Rabatt optional (Standard: 0%)
            return float(family_discount_config.get("first_child_percent", 0))
        elif child_position == 2:
            return float(family_discount_config.get("second_child_percent", 0))
        else:  # 3. Kind und weitere
            return float(family_discount_config.get("third_plus_child_percent", 0))

    @staticmethod
    def calculate_participant_price_with_breakdown(
        age: int,
        role_name: str,
        role_display_name: str,
        ruleset_data: Dict[str, Any],
        family_children_count: int = 1,
        discount_percent: float = 0.0,
        discount_reason: Optional[str] = None,
        manual_price_override: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Berechnet den Preis mit detaillierter Aufschlüsselung

        Args:
            age: Alter des Teilnehmers
            role_name: Name der Rolle (z.B. "betreuer", "kind")
            role_display_name: Anzeigename der Rolle (z.B. "Betreuer", "Kind")
            ruleset_data: Regelwerk-Daten (age_groups, role_discounts, etc.)
            family_children_count: Position in der Familie (1=erstes Kind, 2=zweites, etc.)
            discount_percent: Zusätzlicher manueller Rabatt in Prozent
            discount_reason: Grund für den manuellen Rabatt
            manual_price_override: Manuell gesetzter Preis (überschreibt Berechnung)

        Returns:
            Dictionary mit detaillierter Preisaufschlüsselung
        """
        breakdown = {
            'base_price': 0.0,
            'role_discount_percent': 0.0,
            'role_discount_amount': 0.0,
            'price_after_role_discount': 0.0,
            'family_discount_percent': 0.0,
            'family_discount_amount': 0.0,
            'price_after_family_discount': 0.0,
            'manual_discount_percent': discount_percent,
            'manual_discount_amount': 0.0,
            'manual_price_override': manual_price_override,
            'final_price': 0.0,
            'has_discounts': False,
            'discount_reasons': []
        }

        # Wenn manueller Preis gesetzt ist, überschreibt dieser alles
        if manual_price_override is not None:
            breakdown['final_price'] = manual_price_override
            breakdown['has_discounts'] = True
            breakdown['discount_reasons'].append(f"Manueller Preis: {manual_price_override:.2f} €")
            if discount_reason:
                breakdown['discount_reasons'].append(f"Grund: {discount_reason}")
            return breakdown

        # Basispreis ermitteln
        breakdown['base_price'] = PriceCalculator._get_base_price_by_age(
            age, ruleset_data.get("age_groups", [])
        )

        # Rollenrabatt ermitteln (vom Basispreis!)
        breakdown['role_discount_percent'] = PriceCalculator._get_role_discount(
            role_name, ruleset_data.get("role_discounts", {})
        )
        breakdown['role_discount_amount'] = breakdown['base_price'] * (breakdown['role_discount_percent'] / 100)

        if breakdown['role_discount_percent'] > 0:
            breakdown['has_discounts'] = True
            breakdown['discount_reasons'].append(
                f"Rollenrabatt ({role_display_name}): {breakdown['role_discount_percent']:.0f}%"
            )

        # Familienrabatt ermitteln (vom Basispreis, NICHT gestapelt!)
        breakdown['family_discount_percent'] = PriceCalculator._get_family_discount(
            family_children_count, ruleset_data.get("family_discount", {})
        )
        breakdown['family_discount_amount'] = breakdown['base_price'] * (
            breakdown['family_discount_percent'] / 100
        )

        if breakdown['family_discount_percent'] > 0:
            breakdown['has_discounts'] = True
            breakdown['discount_reasons'].append(
                f"Familienrabatt ({family_children_count}. Kind): {breakdown['family_discount_percent']:.0f}%"
            )

        # Preis nach automatischen Rabatten (für Display-Zwecke)
        breakdown['price_after_role_discount'] = breakdown['base_price'] - breakdown['role_discount_amount']
        breakdown['price_after_family_discount'] = breakdown['base_price'] - breakdown['role_discount_amount'] - breakdown['family_discount_amount']

        # Manueller Rabatt (zusätzlich, vom bereits reduzierten Preis)
        if discount_percent > 0:
            breakdown['manual_discount_amount'] = breakdown['price_after_family_discount'] * (
                discount_percent / 100
            )
            breakdown['has_discounts'] = True
            reason = f"Zusätzlicher Rabatt: {discount_percent:.0f}%"
            if discount_reason:
                reason += f" ({discount_reason})"
            breakdown['discount_reasons'].append(reason)

        # Endpreis berechnen
        breakdown['final_price'] = round(
            breakdown['price_after_family_discount'] - breakdown['manual_discount_amount'],
            2
        )

        return breakdown
