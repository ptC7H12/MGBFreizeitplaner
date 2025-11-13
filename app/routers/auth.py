"""Auth Router - Freizeit-Auswahl und -Erstellung"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.config import settings
from app.database import get_db
from app.models.event import Event

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request, error: str = None):
    """Landing Page für Freizeit-Auswahl oder -Erstellung"""
    return templates.TemplateResponse(
        "auth/landing.html",
        {
            "request": request,
            "title": "Willkommen",
            "error": error
        }
    )


@router.post("/select", response_class=HTMLResponse)
async def select_event(
    request: Request,
    db: Session = Depends(get_db),
    code: str = Form(...)
):
    """Wählt eine Freizeit anhand des Codes aus"""
    # Code normalisieren (Uppercase, Leerzeichen entfernen)
    code = code.strip().upper()

    # Event suchen
    event = db.query(Event).filter(
        Event.code == code,
        Event.is_active == True
    ).first()

    if not event:
        return RedirectResponse(
            url="/auth/?error=invalid_code",
            status_code=303
        )

    # Event-ID in Session speichern
    request.session["event_id"] = event.id
    request.session["event_name"] = event.name
    request.session["event_code"] = event.code

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
    description: str = Form(None),
    custom_code: str = Form(None)
):
    """Erstellt eine neue Freizeit"""
    try:
        # Datum parsen
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Code generieren oder verwenden
        if custom_code:
            code = custom_code.strip().upper()
            # Prüfen ob Code bereits existiert
            existing = db.query(Event).filter(Event.code == code).first()
            if existing:
                return RedirectResponse(
                    url="/auth/?error=code_exists",
                    status_code=303
                )
        else:
            # Eindeutigen Code generieren
            while True:
                code = Event.generate_code()
                existing = db.query(Event).filter(Event.code == code).first()
                if not existing:
                    break

        # Neue Freizeit erstellen
        event = Event(
            name=name,
            event_type=event_type,
            start_date=start_date_obj,
            end_date=end_date_obj,
            location=location if location else None,
            description=description if description else None,
            code=code,
            is_active=True
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        # Event-ID in Session speichern
        request.session["event_id"] = event.id
        request.session["event_name"] = event.name
        request.session["event_code"] = event.code

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
