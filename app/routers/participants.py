"""Participants (Teilnehmer) Router"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional

from app.config import settings
from app.database import get_db
from app.models import Participant, Role, Event, Family

router = APIRouter(prefix="/participants", tags=["participants"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse)
async def list_participants(
    request: Request,
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    role_id: Optional[int] = None,
    family_id: Optional[int] = None
):
    """Liste aller Teilnehmer mit Such- und Filterfunktionen"""
    query = db.query(Participant)

    # Suchfilter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Participant.first_name.ilike(search_filter)) |
            (Participant.last_name.ilike(search_filter)) |
            (Participant.email.ilike(search_filter))
        )

    # Rollenfilter
    if role_id:
        query = query.filter(Participant.role_id == role_id)

    # Familienfilter
    if family_id:
        query = query.filter(Participant.family_id == family_id)

    participants = query.order_by(Participant.last_name).all()

    # Für Filter-Dropdown
    roles = db.query(Role).filter(Role.is_active == True).all()
    families = db.query(Family).order_by(Family.name).all()

    return templates.TemplateResponse(
        "participants/list.html",
        {
            "request": request,
            "title": "Teilnehmer",
            "participants": participants,
            "roles": roles,
            "families": families,
            "search": search,
            "selected_role_id": role_id,
            "selected_family_id": family_id
        }
    )


@router.get("/create", response_class=HTMLResponse)
async def create_participant_form(request: Request, db: Session = Depends(get_db)):
    """Formular zum Erstellen eines neuen Teilnehmers"""
    roles = db.query(Role).filter(Role.is_active == True).all()
    events = db.query(Event).all()
    families = db.query(Family).order_by(Family.name).all()

    return templates.TemplateResponse(
        "participants/create.html",
        {
            "request": request,
            "title": "Neuer Teilnehmer",
            "roles": roles,
            "events": events,
            "families": families
        }
    )


@router.post("/create", response_class=HTMLResponse)
async def create_participant(
    request: Request,
    db: Session = Depends(get_db),
    first_name: str = Form(...),
    last_name: str = Form(...),
    birth_date: str = Form(...),
    gender: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    bildung_teilhabe_id: Optional[str] = Form(None),
    allergies: Optional[str] = Form(None),
    medical_notes: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    discount_percent: float = Form(0.0),
    discount_reason: Optional[str] = Form(None),
    manual_price_override: Optional[float] = Form(None),
    event_id: int = Form(...),
    role_id: int = Form(...),
    family_id: Optional[int] = Form(None)
):
    """Erstellt einen neuen Teilnehmer"""
    try:
        # Datum parsen
        birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()

        # Neuen Teilnehmer erstellen
        participant = Participant(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date_obj,
            gender=gender,
            email=email if email else None,
            phone=phone if phone else None,
            address=address if address else None,
            bildung_teilhabe_id=bildung_teilhabe_id if bildung_teilhabe_id else None,
            allergies=allergies if allergies else None,
            medical_notes=medical_notes if medical_notes else None,
            notes=notes if notes else None,
            discount_percent=discount_percent,
            discount_reason=discount_reason if discount_reason else None,
            manual_price_override=manual_price_override,
            event_id=event_id,
            role_id=role_id,
            family_id=family_id if family_id else None,
            calculated_price=0.0  # TODO: Automatische Preisberechnung in Phase 4
        )

        db.add(participant)
        db.commit()
        db.refresh(participant)

        return RedirectResponse(url=f"/participants/{participant.id}", status_code=303)

    except Exception as e:
        db.rollback()
        # Fehler anzeigen (TODO: Besseres Error-Handling)
        return RedirectResponse(url="/participants/create?error=1", status_code=303)


@router.get("/{participant_id}", response_class=HTMLResponse)
async def view_participant(request: Request, participant_id: int, db: Session = Depends(get_db)):
    """Detailansicht eines Teilnehmers"""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()

    if not participant:
        return RedirectResponse(url="/participants", status_code=303)

    # Zahlungen des Teilnehmers
    total_paid = sum(payment.amount for payment in participant.payments)

    return templates.TemplateResponse(
        "participants/detail.html",
        {
            "request": request,
            "title": f"{participant.full_name}",
            "participant": participant,
            "total_paid": total_paid,
            "outstanding": participant.final_price - total_paid
        }
    )


@router.get("/{participant_id}/edit", response_class=HTMLResponse)
async def edit_participant_form(request: Request, participant_id: int, db: Session = Depends(get_db)):
    """Formular zum Bearbeiten eines Teilnehmers"""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()

    if not participant:
        return RedirectResponse(url="/participants", status_code=303)

    roles = db.query(Role).filter(Role.is_active == True).all()
    events = db.query(Event).all()
    families = db.query(Family).order_by(Family.name).all()

    return templates.TemplateResponse(
        "participants/edit.html",
        {
            "request": request,
            "title": f"{participant.full_name} bearbeiten",
            "participant": participant,
            "roles": roles,
            "events": events,
            "families": families
        }
    )


@router.post("/{participant_id}/edit", response_class=HTMLResponse)
async def update_participant(
    request: Request,
    participant_id: int,
    db: Session = Depends(get_db),
    first_name: str = Form(...),
    last_name: str = Form(...),
    birth_date: str = Form(...),
    gender: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    bildung_teilhabe_id: Optional[str] = Form(None),
    allergies: Optional[str] = Form(None),
    medical_notes: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    discount_percent: float = Form(0.0),
    discount_reason: Optional[str] = Form(None),
    manual_price_override: Optional[float] = Form(None),
    event_id: int = Form(...),
    role_id: int = Form(...),
    family_id: Optional[int] = Form(None)
):
    """Aktualisiert einen Teilnehmer"""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()

    if not participant:
        return RedirectResponse(url="/participants", status_code=303)

    try:
        # Datum parsen
        birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()

        # Teilnehmer aktualisieren
        participant.first_name = first_name
        participant.last_name = last_name
        participant.birth_date = birth_date_obj
        participant.gender = gender
        participant.email = email if email else None
        participant.phone = phone if phone else None
        participant.address = address if address else None
        participant.bildung_teilhabe_id = bildung_teilhabe_id if bildung_teilhabe_id else None
        participant.allergies = allergies if allergies else None
        participant.medical_notes = medical_notes if medical_notes else None
        participant.notes = notes if notes else None
        participant.discount_percent = discount_percent
        participant.discount_reason = discount_reason if discount_reason else None
        participant.manual_price_override = manual_price_override
        participant.event_id = event_id
        participant.role_id = role_id
        participant.family_id = family_id if family_id else None

        db.commit()

        return RedirectResponse(url=f"/participants/{participant_id}", status_code=303)

    except Exception as e:
        db.rollback()
        return RedirectResponse(url=f"/participants/{participant_id}/edit?error=1", status_code=303)


@router.post("/{participant_id}/delete")
async def delete_participant(participant_id: int, db: Session = Depends(get_db)):
    """Löscht einen Teilnehmer"""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Teilnehmer nicht gefunden")

    try:
        db.delete(participant)
        db.commit()
        return RedirectResponse(url="/participants", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Löschen")
