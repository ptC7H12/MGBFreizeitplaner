"""Payments (Zahlungen) Router"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional
from io import BytesIO

from app.config import settings
from app.database import get_db
from app.models import Payment, Participant, Family
from app.services.invoice_generator import InvoiceGenerator

router = APIRouter(prefix="/payments", tags=["payments"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse)
async def list_payments(
    request: Request,
    db: Session = Depends(get_db),
    participant_id: Optional[int] = None,
    family_id: Optional[int] = None
):
    """Liste aller Zahlungen mit Filter"""
    query = db.query(Payment)

    if participant_id:
        query = query.filter(Payment.participant_id == participant_id)
    if family_id:
        query = query.filter(Payment.family_id == family_id)

    payments = query.order_by(Payment.payment_date.desc()).all()

    return templates.TemplateResponse(
        "payments/list.html",
        {
            "request": request,
            "title": "Zahlungen",
            "payments": payments
        }
    )


@router.get("/create", response_class=HTMLResponse)
async def create_payment_form(
    request: Request,
    db: Session = Depends(get_db),
    participant_id: Optional[int] = None,
    family_id: Optional[int] = None
):
    """Formular zum Erstellen einer neuen Zahlung"""
    participants = db.query(Participant).filter(Participant.is_active == True).all()
    families = db.query(Family).all()

    return templates.TemplateResponse(
        "payments/create.html",
        {
            "request": request,
            "title": "Neue Zahlung",
            "participants": participants,
            "families": families,
            "preselected_participant_id": participant_id,
            "preselected_family_id": family_id
        }
    )


@router.post("/create", response_class=HTMLResponse)
async def create_payment(
    request: Request,
    db: Session = Depends(get_db),
    amount: float = Form(...),
    payment_date: str = Form(...),
    payment_method: Optional[str] = Form(None),
    reference: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    participant_id: Optional[int] = Form(None),
    family_id: Optional[int] = Form(None)
):
    """Erstellt eine neue Zahlung"""
    try:
        # Datum parsen
        payment_date_obj = datetime.strptime(payment_date, "%Y-%m-%d").date()

        # Validierung: Entweder Teilnehmer oder Familie
        if not participant_id and not family_id:
            return RedirectResponse(url="/payments/create?error=no_target", status_code=303)

        # Neue Zahlung erstellen
        payment = Payment(
            amount=amount,
            payment_date=payment_date_obj,
            payment_method=payment_method if payment_method else None,
            reference=reference if reference else None,
            notes=notes if notes else None,
            participant_id=participant_id if participant_id else None,
            family_id=family_id if family_id else None
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        # Redirect zurück zur Quelle (Teilnehmer oder Familie)
        if participant_id:
            return RedirectResponse(url=f"/participants/{participant_id}", status_code=303)
        elif family_id:
            return RedirectResponse(url=f"/families/{family_id}", status_code=303)
        else:
            return RedirectResponse(url="/payments", status_code=303)

    except Exception as e:
        db.rollback()
        return RedirectResponse(url="/payments/create?error=1", status_code=303)


@router.post("/{payment_id}/delete")
async def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    """Löscht eine Zahlung"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Zahlung nicht gefunden")

    try:
        participant_id = payment.participant_id
        family_id = payment.family_id

        db.delete(payment)
        db.commit()

        # Redirect zurück zur Quelle
        if participant_id:
            return RedirectResponse(url=f"/participants/{participant_id}", status_code=303)
        elif family_id:
            return RedirectResponse(url=f"/families/{family_id}", status_code=303)
        else:
            return RedirectResponse(url="/payments", status_code=303)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Löschen")


@router.get("/invoice/participant/{participant_id}", response_class=Response)
async def generate_participant_invoice(participant_id: int, db: Session = Depends(get_db)):
    """Generiert eine PDF-Rechnung für einen Teilnehmer"""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Teilnehmer nicht gefunden")

    # PDF generieren
    generator = InvoiceGenerator()
    pdf_bytes = generator.generate_participant_invoice(participant)

    # PDF als Download zurückgeben
    filename = f"Rechnung_{participant.last_name}_{participant.first_name}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/invoice/family/{family_id}", response_class=Response)
async def generate_family_invoice(family_id: int, db: Session = Depends(get_db)):
    """Generiert eine Sammelrechnung für eine Familie"""
    family = db.query(Family).filter(Family.id == family_id).first()

    if not family:
        raise HTTPException(status_code=404, detail="Familie nicht gefunden")

    # PDF generieren
    generator = InvoiceGenerator()
    pdf_bytes = generator.generate_family_invoice(family)

    # PDF als Download zurückgeben
    filename = f"Sammelrechnung_{family.name.replace(' ', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
