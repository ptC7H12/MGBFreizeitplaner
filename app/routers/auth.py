"""Auth Router - Freizeit-Auswahl und -Erstellung"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.database import get_db
from app.models.event import Event
from app.templates_config import templates

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request, db: Session = Depends(get_db), error: str = None):
    """Landing Page für Freizeit-Auswahl oder -Erstellung"""
    # Alle aktiven Freizeiten laden
    events = db.query(Event).filter(Event.is_active == True).order_by(Event.start_date.desc()).all()

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
    # Event suchen
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.is_active == True
    ).first()

    if not event:
        return RedirectResponse(
            url="/auth/?error=invalid_event",
            status_code=303
        )

    # Event-ID in Session speichern
    request.session["event_id"] = event.id
    request.session["event_name"] = event.name

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

        return RedirectResponse(url="/dashboard", status_code=303)

    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url="/auth/?error=create_failed",
            status_code=303
        )


@router.get("/logout")
async def logout(request: Request):
    """Logout - Entfernt Event aus Session"""
    request.session.clear()
    return RedirectResponse(url="/auth/", status_code=303)


@router.get("/switch", response_class=HTMLResponse)
async def switch_event_page(request: Request):
    """Seite zum Wechseln der Freizeit"""
    return RedirectResponse(url="/auth/logout", status_code=303)
