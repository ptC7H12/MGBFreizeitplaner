"""Families (Familien) Router"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.config import settings
from app.database import get_db
from app.models import Family, Participant
from app.dependencies import get_current_event_id

router = APIRouter(prefix="/families", tags=["families"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse)
async def list_families(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Liste aller Familien"""
    families = db.query(Family).filter(Family.event_id == event_id).order_by(Family.name).all()

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
        family = Family(
            name=name,
            contact_person=contact_person if contact_person else None,
            email=email if email else None,
            phone=phone if phone else None,
            address=address if address else None,
            notes=notes if notes else None,
            event_id=event_id  # Aus Session!
        )

        db.add(family)
        db.commit()
        db.refresh(family)

        return RedirectResponse(url=f"/families/{family.id}", status_code=303)

    except Exception as e:
        db.rollback()
        return RedirectResponse(url="/families/create?error=1", status_code=303)


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
        family.name = name
        family.contact_person = contact_person if contact_person else None
        family.email = email if email else None
        family.phone = phone if phone else None
        family.address = address if address else None
        family.notes = notes if notes else None

        db.commit()

        return RedirectResponse(url=f"/families/{family_id}", status_code=303)

    except Exception as e:
        db.rollback()
        return RedirectResponse(url=f"/families/{family_id}/edit?error=1", status_code=303)


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
        db.delete(family)
        db.commit()
        return RedirectResponse(url="/families", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Löschen")
