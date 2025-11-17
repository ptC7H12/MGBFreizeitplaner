"""Auth Router - Freizeit-Auswahl und -Erstellung"""
import logging
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.database import get_db
from app.models.event import Event
from app.templates_config import templates

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


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
        return RedirectResponse(
            url="/auth/?error=invalid_event",
            status_code=303
        )

    # Event-ID in Session speichern
    request.session["event_id"] = event.id
    request.session["event_name"] = event.name
    logger.info(f"Successfully selected event {event_id} ('{event.name}')")

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

        # Event-ID in Session speichern
        request.session["event_id"] = event.id
        request.session["event_name"] = event.name

        logger.info(f"Successfully created event {event.id} ('{event.name}') from {start_date} to {end_date}")
        return RedirectResponse(url="/dashboard", status_code=303)

    except Exception as e:
        logger.error(f"Failed to create event '{name}': {e}", exc_info=True)
        db.rollback()
        return RedirectResponse(
            url="/auth/?error=create_failed",
            status_code=303
        )


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
        return RedirectResponse(
            url="/auth/?error=invalid_event",
            status_code=303
        )

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
    return RedirectResponse(url="/auth/", status_code=303)
