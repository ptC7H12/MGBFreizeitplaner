"""Participants (Teilnehmer) Router"""
import logging
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
from datetime import date, datetime
from typing import Optional
from pydantic import ValidationError

from app.config import settings
from app.database import get_db
from app.models import Participant, Role, Event, Family, Ruleset
from app.services.price_calculator import PriceCalculator
from app.dependencies import get_current_event_id
from app.utils.error_handler import handle_db_exception
from app.utils.flash import flash
from app.schemas import ParticipantCreateSchema, ParticipantUpdateSchema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/participants", tags=["participants"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


def _calculate_price_for_participant(
    db: Session,
    event_id: int,
    role_id: int,
    birth_date: date,
    family_id: Optional[int]
) -> float:
    """
    Hilfsfunktion zur Berechnung des Teilnehmerpreises

    Args:
        db: Datenbank-Session
        event_id: ID der Veranstaltung
        role_id: ID der Rolle
        birth_date: Geburtsdatum des Teilnehmers
        family_id: Optional ID der Familie

    Returns:
        Berechneter Preis in Euro
    """
    # Event und Rolle laden
    event = db.query(Event).filter(Event.id == event_id).first()
    role = db.query(Role).filter(Role.id == role_id).first()

    if not event or not role:
        return 0.0

    # Aktives Regelwerk für das Event finden
    ruleset = db.query(Ruleset).filter(
        Ruleset.is_active == True,
        Ruleset.valid_from <= event.start_date,
        Ruleset.valid_until >= event.start_date
    ).first()

    if not ruleset:
        return 0.0

    # Alter zum Event-Start berechnen
    age = event.start_date.year - birth_date.year
    if (event.start_date.month, event.start_date.day) < (birth_date.month, birth_date.day):
        age -= 1

    # Position in Familie ermitteln (für Familienrabatt)
    family_children_count = 1
    if family_id:
        # Anzahl der Kinder in der Familie zählen (nach Geburtsdatum sortiert)
        siblings = db.query(Participant).filter(
            Participant.family_id == family_id,
            Participant.is_active == True
        ).order_by(Participant.birth_date).all()

        # Position des neuen Kindes bestimmen
        family_children_count = len(siblings) + 1

    # Preis berechnen
    calculated_price = PriceCalculator.calculate_participant_price(
        age=age,
        role_name=role.name.lower(),
        ruleset_data={
            "age_groups": ruleset.age_groups,
            "role_discounts": ruleset.role_discounts,
            "family_discount": ruleset.family_discount
        },
        family_children_count=family_children_count
    )

    return calculated_price


@router.get("/", response_class=HTMLResponse)
async def list_participants(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    search: Optional[str] = None,
    role_id: Optional[int] = None,
    family_id: Optional[int] = None
):
    """Liste aller Teilnehmer mit Such- und Filterfunktionen"""
    query = db.query(Participant).filter(Participant.event_id == event_id)

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

    # Für Filter-Dropdown (auch nach event_id gefiltert)
    roles = db.query(Role).filter(Role.is_active == True).all()
    families = db.query(Family).filter(Family.event_id == event_id).order_by(Family.name).all()

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
async def create_participant_form(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Formular zum Erstellen eines neuen Teilnehmers"""
    roles = db.query(Role).filter(Role.is_active == True).all()
    event = db.query(Event).filter(Event.id == event_id).first()
    families = db.query(Family).filter(Family.event_id == event_id).order_by(Family.name).all()

    return templates.TemplateResponse(
        "participants/create.html",
        {
            "request": request,
            "title": "Neuer Teilnehmer",
            "roles": roles,
            "event": event,
            "families": families
        }
    )


@router.post("/create", response_class=HTMLResponse)
async def create_participant(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
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
    role_id: int = Form(...),
    family_id: Optional[int] = Form(None)
):
    """Erstellt einen neuen Teilnehmer"""
    try:
        # Pydantic-Validierung
        participant_data = ParticipantCreateSchema(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            gender=gender,
            email=email,
            phone=phone,
            address=address,
            bildung_teilhabe_id=bildung_teilhabe_id,
            allergies=allergies,
            medical_notes=medical_notes,
            notes=notes,
            discount_percent=discount_percent,
            discount_reason=discount_reason,
            manual_price_override=manual_price_override,
            role_id=role_id,
            family_id=family_id
        )

        # Datum parsen (bereits validiert durch Pydantic)
        birth_date_obj = datetime.strptime(participant_data.birth_date, "%Y-%m-%d").date()

        # Automatische Preisberechnung
        calculated_price = _calculate_price_for_participant(
            db=db,
            event_id=event_id,
            role_id=participant_data.role_id,
            birth_date=birth_date_obj,
            family_id=participant_data.family_id
        )

        # Neuen Teilnehmer erstellen
        participant = Participant(
            first_name=participant_data.first_name,
            last_name=participant_data.last_name,
            birth_date=birth_date_obj,
            gender=participant_data.gender,
            email=participant_data.email,
            phone=participant_data.phone,
            address=participant_data.address,
            bildung_teilhabe_id=participant_data.bildung_teilhabe_id,
            allergies=participant_data.allergies,
            medical_notes=participant_data.medical_notes,
            notes=participant_data.notes,
            discount_percent=participant_data.discount_percent,
            discount_reason=participant_data.discount_reason,
            manual_price_override=participant_data.manual_price_override,
            event_id=event_id,  # Aus Session, nicht aus Formular!
            role_id=participant_data.role_id,
            family_id=participant_data.family_id,
            calculated_price=calculated_price
        )

        db.add(participant)
        db.commit()
        db.refresh(participant)

        flash(request, f"Teilnehmer {participant.full_name} wurde erfolgreich erstellt", "success")
        return RedirectResponse(url=f"/participants/{participant.id}", status_code=303)

    except ValidationError as e:
        # Pydantic-Validierungsfehler
        logger.warning(f"Validation error creating participant: {e}", exc_info=True)
        # Ersten Fehler extrahieren für benutzerfreundliche Nachricht
        first_error = e.errors()[0]
        field_name = first_error['loc'][0] if first_error['loc'] else 'Unbekannt'
        error_msg = first_error['msg']
        flash(request, f"Validierungsfehler ({field_name}): {error_msg}", "error")
        return RedirectResponse(url="/participants/create?error=validation", status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error creating participant: {e}", exc_info=True)
        flash(request, "Teilnehmer konnte nicht erstellt werden (Datenbankfehler)", "error")
        return RedirectResponse(url="/participants/create?error=db_integrity", status_code=303)

    except DataError as e:
        db.rollback()
        logger.error(f"Invalid data creating participant: {e}", exc_info=True)
        flash(request, "Ungültige Daten eingegeben", "error")
        return RedirectResponse(url="/participants/create?error=invalid_data", status_code=303)

    except Exception as e:
        return handle_db_exception(e, "/participants/create", "Creating participant", db, request)


@router.post("/calculate-price", response_class=HTMLResponse)
async def calculate_price_preview(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    birth_date: str = Form(...),
    role_id: int = Form(...),
    family_id: Optional[int] = Form(None)
):
    """
    HTMX-Endpunkt für Live-Preis-Vorschau
    Berechnet den Preis basierend auf Geburtsdatum, Event, Rolle und Familie
    """
    try:
        # Datum parsen
        birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()

        # Preis berechnen
        calculated_price = _calculate_price_for_participant(
            db=db,
            event_id=event_id,
            role_id=role_id,
            birth_date=birth_date_obj,
            family_id=family_id
        )

        # Event und Rolle laden für Detailinfo
        event = db.query(Event).filter(Event.id == event_id).first()
        role = db.query(Role).filter(Role.id == role_id).first()

        # Alter berechnen
        age = None
        if event:
            age = event.start_date.year - birth_date_obj.year
            if (event.start_date.month, event.start_date.day) < (birth_date_obj.month, birth_date_obj.day):
                age -= 1

        # HTML-Fragment zurückgeben
        return templates.TemplateResponse(
            "participants/_price_preview.html",
            {
                "request": request,
                "calculated_price": calculated_price,
                "age": age,
                "event_name": event.name if event else None,
                "role_name": role.name if role else None
            }
        )

    except ValueError as e:
        logger.warning(f"Invalid date input for price calculation: {e}", exc_info=True)
        return HTMLResponse(content=f'<div class="text-sm text-red-500">Ungültiges Datum</div>')

    except Exception as e:
        logger.error(f"Error calculating price preview: {e}", exc_info=True)
        return HTMLResponse(content=f'<div class="text-sm text-gray-500">Preis wird berechnet...</div>')


@router.get("/{participant_id}", response_class=HTMLResponse)
async def view_participant(
    request: Request,
    participant_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Detailansicht eines Teilnehmers"""
    participant = db.query(Participant).filter(
        Participant.id == participant_id,
        Participant.event_id == event_id
    ).first()

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
async def edit_participant_form(
    request: Request,
    participant_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Formular zum Bearbeiten eines Teilnehmers"""
    participant = db.query(Participant).filter(
        Participant.id == participant_id,
        Participant.event_id == event_id
    ).first()

    if not participant:
        return RedirectResponse(url="/participants", status_code=303)

    roles = db.query(Role).filter(Role.is_active == True).all()
    event = db.query(Event).filter(Event.id == event_id).first()
    families = db.query(Family).filter(Family.event_id == event_id).order_by(Family.name).all()

    return templates.TemplateResponse(
        "participants/edit.html",
        {
            "request": request,
            "title": f"{participant.full_name} bearbeiten",
            "participant": participant,
            "roles": roles,
            "event": event,
            "families": families
        }
    )


@router.post("/{participant_id}/edit", response_class=HTMLResponse)
async def update_participant(
    request: Request,
    participant_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
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
    role_id: int = Form(...),
    family_id: Optional[int] = Form(None)
):
    """Aktualisiert einen Teilnehmer"""
    participant = db.query(Participant).filter(
        Participant.id == participant_id,
        Participant.event_id == event_id
    ).first()

    if not participant:
        return RedirectResponse(url="/participants", status_code=303)

    try:
        # Pydantic-Validierung
        participant_data = ParticipantUpdateSchema(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            gender=gender,
            email=email,
            phone=phone,
            address=address,
            bildung_teilhabe_id=bildung_teilhabe_id,
            allergies=allergies,
            medical_notes=medical_notes,
            notes=notes,
            discount_percent=discount_percent,
            discount_reason=discount_reason,
            manual_price_override=manual_price_override,
            role_id=role_id,
            family_id=family_id
        )

        # Datum parsen (bereits validiert durch Pydantic)
        birth_date_obj = datetime.strptime(participant_data.birth_date, "%Y-%m-%d").date()

        # Preis neu berechnen (wenn sich relevante Daten geändert haben)
        calculated_price = _calculate_price_for_participant(
            db=db,
            event_id=event_id,
            role_id=participant_data.role_id,
            birth_date=birth_date_obj,
            family_id=participant_data.family_id
        )

        # Teilnehmer aktualisieren
        participant.first_name = participant_data.first_name
        participant.last_name = participant_data.last_name
        participant.birth_date = birth_date_obj
        participant.gender = participant_data.gender
        participant.email = participant_data.email
        participant.phone = participant_data.phone
        participant.address = participant_data.address
        participant.bildung_teilhabe_id = participant_data.bildung_teilhabe_id
        participant.allergies = participant_data.allergies
        participant.medical_notes = participant_data.medical_notes
        participant.notes = participant_data.notes
        participant.discount_percent = participant_data.discount_percent
        participant.discount_reason = participant_data.discount_reason
        participant.manual_price_override = participant_data.manual_price_override
        # event_id bleibt unverändert (Sicherheit!)
        participant.role_id = participant_data.role_id
        participant.family_id = participant_data.family_id
        participant.calculated_price = calculated_price

        db.commit()

        flash(request, f"Teilnehmer {participant.full_name} wurde erfolgreich aktualisiert", "success")
        return RedirectResponse(url=f"/participants/{participant_id}", status_code=303)

    except ValidationError as e:
        # Pydantic-Validierungsfehler
        logger.warning(f"Validation error updating participant: {e}", exc_info=True)
        first_error = e.errors()[0]
        field_name = first_error['loc'][0] if first_error['loc'] else 'Unbekannt'
        error_msg = first_error['msg']
        flash(request, f"Validierungsfehler ({field_name}): {error_msg}", "error")
        return RedirectResponse(url=f"/participants/{participant_id}/edit?error=validation", status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error updating participant: {e}", exc_info=True)
        flash(request, "Teilnehmer konnte nicht aktualisiert werden (Datenbankfehler)", "error")
        return RedirectResponse(url=f"/participants/{participant_id}/edit?error=db_integrity", status_code=303)

    except DataError as e:
        db.rollback()
        logger.error(f"Invalid data updating participant: {e}", exc_info=True)
        flash(request, "Ungültige Daten eingegeben", "error")
        return RedirectResponse(url=f"/participants/{participant_id}/edit?error=invalid_data", status_code=303)

    except Exception as e:
        return handle_db_exception(e, f"/participants/{participant_id}/edit", "Updating participant", db, request)


@router.post("/{participant_id}/delete")
async def delete_participant(
    participant_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Löscht einen Teilnehmer"""
    participant = db.query(Participant).filter(
        Participant.id == participant_id,
        Participant.event_id == event_id
    ).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Teilnehmer nicht gefunden")

    try:
        participant_name = participant.full_name
        db.delete(participant)
        db.commit()
        logger.info(f"Participant deleted: {participant_name} (ID: {participant_id})")
        # Note: Flash-Message kann hier nicht gesetzt werden, da Request fehlt
        return RedirectResponse(url="/participants", status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Cannot delete participant due to integrity constraint: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Teilnehmer kann nicht gelöscht werden, da noch Zahlungen oder andere Verknüpfungen existieren")

    except Exception as e:
        db.rollback()
        logger.exception(f"Error deleting participant: {e}")
        raise HTTPException(status_code=500, detail="Fehler beim Löschen")
