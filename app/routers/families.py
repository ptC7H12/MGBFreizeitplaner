"""Families (Familien) Router"""
import logging
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, DataError
from typing import Optional
from pydantic import ValidationError

from app.database import get_db
from app.models import Family, Participant
from app.dependencies import get_current_event_id
from app.utils.error_handler import handle_db_exception
from app.utils.flash import flash
from app.schemas import FamilyCreateSchema, FamilyUpdateSchema
from app.templates_config import templates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/families", tags=["families"])


@router.get("/", response_class=HTMLResponse)
async def list_families(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Liste aller Familien"""
    # Eager Loading um N+1 Query Problem zu vermeiden
    families = db.query(Family)\
        .filter(Family.event_id == event_id)\
        .options(
            joinedload(Family.participants),
            joinedload(Family.payments)
        )\
        .order_by(Family.name)\
        .all()

    # Für jede Familie: Anzahl Teilnehmer und Gesamtpreis berechnen
    family_data = []
    for family in families:
        total_price = sum(p.final_price for p in family.participants)
        total_paid = sum(payment.amount for payment in family.payments)

        family_data.append({
            "family": family,
            "participant_count": len(family.participants),
            "total_price": total_price,
            "total_paid": total_paid,
            "outstanding": total_price - total_paid
        })

    return templates.TemplateResponse(
        "families/list.html",
        {"request": request, "title": "Familien", "family_data": family_data}
    )


@router.get("/create", response_class=HTMLResponse)
async def create_family_form(request: Request, db: Session = Depends(get_db)):
    """Formular zum Erstellen einer neuen Familie"""
    return templates.TemplateResponse(
        "families/create.html",
        {
            "request": request,
            "title": "Neue Familie"
        }
    )


@router.post("/create", response_class=HTMLResponse)
async def create_family(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    name: str = Form(...),
    contact_person: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    notes: Optional[str] = Form(None)
):
    """Erstellt eine neue Familie"""
    try:
        # Pydantic-Validierung
        family_data = FamilyCreateSchema(
            name=name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            address=address,
            notes=notes
        )

        family = Family(
            name=family_data.name,
            contact_person=family_data.contact_person,
            email=family_data.email,
            phone=family_data.phone,
            address=family_data.address,
            notes=family_data.notes,
            event_id=event_id  # Aus Session!
        )

        db.add(family)
        db.commit()
        db.refresh(family)

        flash(request, f"Familie {family.name} wurde erfolgreich erstellt", "success")
        return RedirectResponse(url=f"/families/{family.id}", status_code=303)

    except ValidationError as e:
        # Pydantic-Validierungsfehler
        logger.warning(f"Validation error creating family: {e}", exc_info=True)
        first_error = e.errors()[0]
        field_name = first_error['loc'][0] if first_error['loc'] else 'Unbekannt'
        error_msg = first_error['msg']
        flash(request, f"Validierungsfehler ({field_name}): {error_msg}", "error")
        return RedirectResponse(url="/families/create?error=validation", status_code=303)

    except ValueError as e:
        logger.warning(f"Invalid input for family creation: {e}", exc_info=True)
        flash(request, f"Ungültige Eingabe: {str(e)}", "error")
        return RedirectResponse(url="/families/create?error=invalid_input", status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error creating family: {e}", exc_info=True)
        flash(request, "Familie konnte nicht erstellt werden (Datenbankfehler)", "error")
        return RedirectResponse(url="/families/create?error=db_integrity", status_code=303)

    except DataError as e:
        db.rollback()
        logger.error(f"Invalid data creating family: {e}", exc_info=True)
        flash(request, "Ungültige Daten eingegeben", "error")
        return RedirectResponse(url="/families/create?error=invalid_data", status_code=303)

    except Exception as e:
        return handle_db_exception(e, "/families/create", "Creating family", db, request)


@router.get("/{family_id}", response_class=HTMLResponse)
async def view_family(
    request: Request,
    family_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Detailansicht einer Familie"""
    family = db.query(Family).filter(
        Family.id == family_id,
        Family.event_id == event_id
    ).first()

    if not family:
        return RedirectResponse(url="/families", status_code=303)

    # Finanzielle Übersicht
    total_price = sum(p.final_price for p in family.participants)
    total_paid = sum(payment.amount for payment in family.payments)

    return templates.TemplateResponse(
        "families/detail.html",
        {
            "request": request,
            "title": f"Familie {family.name}",
            "family": family,
            "total_price": total_price,
            "total_paid": total_paid,
            "outstanding": total_price - total_paid
        }
    )


@router.get("/{family_id}/edit", response_class=HTMLResponse)
async def edit_family_form(
    request: Request,
    family_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Formular zum Bearbeiten einer Familie"""
    family = db.query(Family).filter(
        Family.id == family_id,
        Family.event_id == event_id
    ).first()

    if not family:
        return RedirectResponse(url="/families", status_code=303)

    return templates.TemplateResponse(
        "families/edit.html",
        {
            "request": request,
            "title": f"{family.name} bearbeiten",
            "family": family
        }
    )


@router.post("/{family_id}/edit", response_class=HTMLResponse)
async def update_family(
    request: Request,
    family_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    name: str = Form(...),
    contact_person: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    notes: Optional[str] = Form(None)
):
    """Aktualisiert eine Familie"""
    family = db.query(Family).filter(
        Family.id == family_id,
        Family.event_id == event_id
    ).first()

    if not family:
        return RedirectResponse(url="/families", status_code=303)

    try:
        # Pydantic-Validierung
        family_data = FamilyUpdateSchema(
            name=name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            address=address,
            notes=notes
        )

        family.name = family_data.name
        family.contact_person = family_data.contact_person
        family.email = family_data.email
        family.phone = family_data.phone
        family.address = family_data.address
        family.notes = family_data.notes

        db.commit()

        flash(request, f"Familie {family.name} wurde erfolgreich aktualisiert", "success")
        return RedirectResponse(url=f"/families/{family_id}", status_code=303)

    except ValidationError as e:
        # Pydantic-Validierungsfehler
        logger.warning(f"Validation error updating family: {e}", exc_info=True)
        first_error = e.errors()[0]
        field_name = first_error['loc'][0] if first_error['loc'] else 'Unbekannt'
        error_msg = first_error['msg']
        flash(request, f"Validierungsfehler ({field_name}): {error_msg}", "error")
        return RedirectResponse(url=f"/families/{family_id}/edit?error=validation", status_code=303)

    except ValueError as e:
        logger.warning(f"Invalid input for family update: {e}", exc_info=True)
        flash(request, f"Ungültige Eingabe: {str(e)}", "error")
        return RedirectResponse(url=f"/families/{family_id}/edit?error=invalid_input", status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error updating family: {e}", exc_info=True)
        flash(request, "Familie konnte nicht aktualisiert werden (Datenbankfehler)", "error")
        return RedirectResponse(url=f"/families/{family_id}/edit?error=db_integrity", status_code=303)

    except DataError as e:
        db.rollback()
        logger.error(f"Invalid data updating family: {e}", exc_info=True)
        flash(request, "Ungültige Daten eingegeben", "error")
        return RedirectResponse(url=f"/families/{family_id}/edit?error=invalid_data", status_code=303)

    except Exception as e:
        return handle_db_exception(e, f"/families/{family_id}/edit", "Updating family", db, request)


@router.post("/{family_id}/delete")
async def delete_family(
    family_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Löscht eine Familie"""
    family = db.query(Family).filter(
        Family.id == family_id,
        Family.event_id == event_id
    ).first()

    if not family:
        raise HTTPException(status_code=404, detail="Familie nicht gefunden")

    # Prüfen, ob noch Teilnehmer zugeordnet sind
    if len(family.participants) > 0:
        raise HTTPException(
            status_code=400,
            detail="Familie kann nicht gelöscht werden, solange noch Teilnehmer zugeordnet sind"
        )

    try:
        family_name = family.name
        db.delete(family)
        db.commit()
        logger.info(f"Family deleted: {family_name} (ID: {family_id})")
        return RedirectResponse(url="/families", status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Cannot delete family due to integrity constraint: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Familie kann nicht gelöscht werden, da noch Zahlungen oder andere Verknüpfungen existieren")

    except Exception as e:
        db.rollback()
        logger.exception(f"Error deleting family: {e}")
        raise HTTPException(status_code=500, detail="Fehler beim Löschen")
