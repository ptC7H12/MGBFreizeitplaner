"""Role Management Service"""
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models import Role, Event

logger = logging.getLogger(__name__)


class RoleManager:
    """Service zur Verwaltung von Rollen und automatischer Erstellung aus Rulesets"""

    # Standard-Farben für Rollen
    ROLE_COLORS = {
        "kind": "#3B82F6",  # Blau
        "jugendlicher": "#8B5CF6",  # Lila
        "betreuer": "#10B981",  # Grün
        "kueche": "#F59E0B",  # Orange
        "kuechenpersonal": "#F59E0B",  # Orange
        "leitung": "#EF4444",  # Rot
        "freizeitleitung": "#EF4444",  # Rot
        "techniker": "#06B6D4",  # Cyan
        "helfer": "#84CC16",  # Lime
        "fahrer": "#F43F5E",  # Rose
        "default": "#6B7280"  # Grau
    }

    # Standard-Display-Namen für bekannte Rollen
    ROLE_DISPLAY_NAMES = {
        "kind": "Kind",
        "jugendlicher": "Jugendlicher",
        "betreuer": "Betreuer",
        "kueche": "Küchenpersonal",
        "kuechenpersonal": "Küchenpersonal",
        "leitung": "Freizeitleitung",
        "freizeitleitung": "Freizeitleitung",
        "techniker": "Techniker",
        "helfer": "Helfer",
        "fahrer": "Fahrer"
    }

    @staticmethod
    def create_roles_from_ruleset(db: Session, event_id: int, role_discounts: Optional[Dict]) -> List[Role]:
        """
        Erstellt automatisch Rollen aus den role_discounts eines Rulesets

        Args:
            db: Datenbank-Session
            event_id: ID des Events
            role_discounts: Dict mit role_discounts aus dem Ruleset

        Returns:
            Liste der erstellten/gefundenen Rollen
        """
        if not role_discounts:
            return []

        created_roles = []
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return []

        for role_name in role_discounts.keys():
            # Prüfen ob Rolle bereits existiert
            existing_role = db.query(Role).filter(
                Role.name == role_name.lower(),
                Role.event_id == event_id
            ).first()

            if existing_role:
                created_roles.append(existing_role)
                continue

            # Neue Rolle erstellen
            display_name = RoleManager._get_display_name(role_name)
            color = RoleManager._get_role_color(role_name)

            new_role = Role(
                name=role_name.lower(),
                display_name=display_name,
                description=f"Automatisch erstellt aus Regelwerk",
                color=color,
                is_active=True,
                event_id=event_id
            )
            db.add(new_role)
            created_roles.append(new_role)

        db.commit()
        return created_roles

    @staticmethod
    def ensure_standard_roles(db: Session, event_id: int) -> List[Role]:
        """
        Stellt sicher, dass Standard-Rollen (Kind, Jugendlicher) für ein Event existieren

        Args:
            db: Datenbank-Session
            event_id: ID des Events

        Returns:
            Liste der Standard-Rollen
        """
        standard_roles = ["kind", "jugendlicher"]
        roles = []

        for role_name in standard_roles:
            existing_role = db.query(Role).filter(
                Role.name == role_name,
                Role.event_id == event_id
            ).first()

            if not existing_role:
                new_role = Role(
                    name=role_name,
                    display_name=RoleManager._get_display_name(role_name),
                    description="Standard-Rolle",
                    color=RoleManager._get_role_color(role_name),
                    is_active=True,
                    event_id=event_id
                )
                db.add(new_role)
                roles.append(new_role)
            else:
                roles.append(existing_role)

        db.commit()
        return roles

    @staticmethod
    def _get_display_name(role_name: str) -> str:
        """Ermittelt den Display-Namen für eine Rolle"""
        role_name_lower = role_name.lower()

        # Bekannte Rolle?
        if role_name_lower in RoleManager.ROLE_DISPLAY_NAMES:
            return RoleManager.ROLE_DISPLAY_NAMES[role_name_lower]

        # Ansonsten: Ersten Buchstaben groß schreiben
        return role_name.capitalize()

    @staticmethod
    def _get_role_color(role_name: str) -> str:
        """Ermittelt die Farbe für eine Rolle"""
        role_name_lower = role_name.lower()
        return RoleManager.ROLE_COLORS.get(role_name_lower, RoleManager.ROLE_COLORS["default"])
