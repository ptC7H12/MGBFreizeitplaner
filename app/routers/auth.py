"""Auth Router - Freizeit-Auswahl und -Erstellung"""
import logging
import httpx
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional

from app.database import get_db
from app.models.event import Event
from app.models.ruleset import Ruleset
from app.models.setting import Setting
from app.services.ruleset_parser import RulesetParser
from app.services.role_manager import RoleManager
from app.templates_config import templates
from app.utils.flash import flash

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


def _get_ruleset_filename_for_event_type(event_type: str, year: int) -> Optional[str]:
    """
    Generiert den erwarteten Dateinamen für ein Ruleset basierend auf Event-Typ und Jahr.

    Args:
        event_type: Event-Typ (z.B. "familienfreizeit", "kinderfreizeit")
        year: Jahr des Events (z.B. 2024)

    Returns:
        Dateiname (z.B. "Familienfreizeiten_2024.yaml") oder None bei unbekanntem Typ
    """
    # Mapping: event_type → Dateinamen-Präfix
    type_mapping = {
        "familienfreizeit": "Familienfreizeiten",
        "kinderfreizeit": "Kinderfreizeiten",
        "jugendfreizeit": "Jugendfreizeiten",
        "teeniefreizeit": "Teeniefreizeiten"
    }

    prefix = type_mapping.get(event_type.lower())
    if not prefix:
        return None

    return f"{prefix}_{year}.yaml"


async def _try_import_ruleset_from_github(
    db: Session,
    event_id: int,
    event_type: str,
    start_date: date,
    request: Request
) -> bool:
    """
    Versucht ein passendes Ruleset aus dem GitHub-Repository zu importieren.

    Args:
        db: Datenbank-Session
        event_id: ID des erstellten Events
        event_type: Event-Typ
        start_date: Startdatum des Events
        request: Request-Objekt für Flash-Messages

    Returns:
        True wenn erfolgreich importiert, sonst False
    """
    try:
        # Jahr aus Startdatum extrahieren
        year = start_date.year

        # Erwarteten Dateinamen generieren
        filename = _get_ruleset_filename_for_event_type(event_type, year)
        if not filename:
            logger.debug(f"No ruleset filename mapping for event type '{event_type}'")
            return False

        # Standard-GitHub-Repo aus Settings laden
        setting = db.query(Setting).filter(Setting.event_id == event_id).first()
        if not setting or not setting.default_github_repo:
            logger.debug("No default GitHub repo configured")
            return False

        base_url = setting.default_github_repo

        # GitHub Raw URL konstruieren
        # Von: https://github.com/ptC7H12/MGBFreizeitplaner/tree/main/rulesets/valid/
        # Zu: https://raw.githubusercontent.com/ptC7H12/MGBFreizeitplaner/main/rulesets/valid/Familienfreizeiten_2024.yaml
        raw_url = base_url.replace("github.com", "raw.githubusercontent.com").replace("/tree/", "/") + filename

        logger.info(f"Attempting to import ruleset from: {raw_url}")

        # Datei von GitHub herunterladen
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(raw_url)

            if response.status_code != 200:
                logger.info(f"Ruleset file not found on GitHub (HTTP {response.status_code})")
                return False

            yaml_content = response.text

        # YAML parsen
        parser = RulesetParser()
        data = parser.parse_yaml_string(yaml_content)

        # Validieren
        is_valid, error_msg = parser.validate_ruleset(data)
        if not is_valid:
            logger.warning(f"Invalid ruleset from GitHub: {error_msg}")
            flash(request, f"Gefundenes Regelwerk ist ungültig: {error_msg}", "warning")
            return False

        # Alle bestehenden Rulesets für dieses Event deaktivieren
        # (sollte normalerweise keine geben, aber sicherheitshalber)
        existing_rulesets = db.query(Ruleset).filter(
            Ruleset.event_id == event_id,
            Ruleset.is_active == True
        ).all()
        for existing_ruleset in existing_rulesets:
            existing_ruleset.is_active = False

        # Regelwerk in Datenbank speichern
        ruleset = Ruleset(
            name=data["name"],
            ruleset_type=data["type"],
            description=data.get("description"),
            valid_from=datetime.strptime(data["valid_from"], "%Y-%m-%d").date(),
            valid_until=datetime.strptime(data["valid_until"], "%Y-%m-%d").date(),
            age_groups=data["age_groups"],
            role_discounts=data.get("role_discounts"),
            family_discount=data.get("family_discount"),
            source_file=raw_url,
            event_id=event_id,
            is_active=True  # Automatisch aktivieren
        )

        db.add(ruleset)
        db.commit()
        db.refresh(ruleset)

        # Rollen aus Ruleset erstellen
        if data.get("role_discounts"):
            RoleManager.create_roles_from_ruleset(db, event_id, data.get("role_discounts"))
            logger.info(f"Created {len(data.get('role_discounts'))} roles from ruleset")

        logger.info(f"Successfully imported and activated ruleset '{data['name']}' for event {event_id}")
        flash(request, f"Regelwerk '{data['name']}' automatisch importiert und aktiviert!", "success")
        return True

    except httpx.HTTPError as e:
        logger.error(f"HTTP error while fetching ruleset from GitHub: {e}")
        return False
    except Exception as e:
        logger.error(f"Error importing ruleset from GitHub: {e}", exc_info=True)
        return False


@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request, db: Session = Depends(get_db), error: str = None):
    """Landing Page für Freizeit-Auswahl oder -Erstellung"""
    logger.info("Loading landing page")

    # Alle aktiven Freizeiten laden (neueste zuerst)
    events = db.query(Event).filter(Event.is_active == True).order_by(Event.created_at.desc()).all()
    logger.debug(f"Found {len(events)} active events")

    return templates.TemplateResponse(
        "auth/landing.html",
        {
            "request": request,
            "title": "Willkommen",
            "error": error,
            "events": events
        }
    )


@router.post("/select", response_class=HTMLResponse)
async def select_event(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Form(...)
):
    """Wählt eine Freizeit aus"""
    logger.info(f"Attempting to select event {event_id}")

    # Event suchen
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.is_active == True
    ).first()

    if not event:
        logger.warning(f"Event {event_id} not found or inactive")
        flash(request, "Event nicht gefunden oder inaktiv", "error")
        return RedirectResponse(url="/auth/", status_code=303)

    # Event-ID in Session speichern
    request.session["event_id"] = event.id
    request.session["event_name"] = event.name
    logger.info(f"Successfully selected event {event_id} ('{event.name}')")
    flash(request, f"Event '{event.name}' erfolgreich ausgewählt", "success")

    return RedirectResponse(url="/dashboard", status_code=303)


@router.post("/create", response_class=HTMLResponse)
async def create_event(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    event_type: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    location: str = Form(None),
    description: str = Form(None)
):
    """Erstellt eine neue Freizeit"""
    logger.info(f"Attempting to create new event: name='{name}', type={event_type}")

    try:
        # Datum parsen
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Neue Freizeit erstellen (ohne Code für lokalen Betrieb)
        event = Event(
            name=name,
            event_type=event_type,
            start_date=start_date_obj,
            end_date=end_date_obj,
            location=location if location else None,
            description=description if description else None,
            code=None,  # Kein Code für lokalen Betrieb
            is_active=True
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        # Setting-Eintrag für das Event erstellen (falls noch nicht vorhanden)
        setting = db.query(Setting).filter(Setting.event_id == event.id).first()
        if not setting:
            setting = Setting(event_id=event.id)
            db.add(setting)
            db.commit()
            db.refresh(setting)
            logger.info(f"Created default settings for event {event.id}")

        # Versuche passendes Ruleset von GitHub zu importieren
        await _try_import_ruleset_from_github(db, event.id, event_type, start_date_obj, request)

        # Event-ID in Session speichern
        request.session["event_id"] = event.id
        request.session["event_name"] = event.name

        logger.info(f"Successfully created event {event.id} ('{event.name}') from {start_date} to {end_date}")
        flash(request, f"Event '{event.name}' erfolgreich erstellt!", "success")
        return RedirectResponse(url="/dashboard", status_code=303)

    except Exception as e:
        logger.error(f"Failed to create event '{name}': {e}", exc_info=True)
        db.rollback()
        flash(request, f"Event konnte nicht erstellt werden: {str(e)}", "error")
        return RedirectResponse(url="/auth/", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    """Logout - Entfernt Event aus Session"""
    event_id = request.session.get("event_id")
    event_name = request.session.get("event_name")

    request.session.clear()
    logger.info(f"User logged out from event {event_id} ('{event_name}')")

    return RedirectResponse(url="/auth/", status_code=303)


@router.get("/switch", response_class=HTMLResponse)
async def switch_event_page(request: Request):
    """Seite zum Wechseln der Freizeit"""
    return RedirectResponse(url="/auth/logout", status_code=303)


@router.post("/delete", response_class=HTMLResponse)
async def delete_event(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Form(...)
):
    """Löscht eine Freizeit"""
    logger.info(f"Attempting to delete event {event_id}")

    # Event suchen
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        logger.warning(f"Event {event_id} not found for deletion")
        flash(request, "Event nicht gefunden", "error")
        return RedirectResponse(url="/auth/", status_code=303)

    event_name = event.name

    # Prüfen ob das Event aktuell in der Session ist
    current_event_id = request.session.get("event_id")
    if current_event_id == event_id:
        # Session löschen wenn das aktuelle Event gelöscht wird
        request.session.clear()
        logger.debug(f"Cleared session as deleted event was currently active")

    # Event löschen (Cascade löscht alle zugehörigen Daten)
    db.delete(event)
    db.commit()

    logger.info(f"Successfully deleted event {event_id} ('{event_name}')")
    flash(request, f"Event '{event_name}' wurde gelöscht", "info")
    return RedirectResponse(url="/auth/", status_code=303)
