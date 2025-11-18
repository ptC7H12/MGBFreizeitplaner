"""Payments (Zahlungen) Router"""
import logging
import zipfile
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
from datetime import date, datetime
from typing import Optional
from io import BytesIO
from pydantic import ValidationError

from app.database import get_db
from app.models import Payment, Participant, Family
from app.dependencies import get_current_event_id
from app.services.invoice_generator import InvoiceGenerator
from app.utils.error_handler import handle_db_exception
from app.utils.flash import flash
from app.schemas import PaymentCreateSchema, PaymentUpdateSchema
from app.templates_config import templates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/", response_class=HTMLResponse)
async def list_payments(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    participant_id: Optional[int] = None,
    family_id: Optional[int] = None
):
    """Liste aller Zahlungen mit Filter"""
    query = db.query(Payment).filter(Payment.event_id == event_id)

    if participant_id:
        query = query.filter(Payment.participant_id == participant_id)
    if family_id:
        query = query.filter(Payment.family_id == family_id)

    payments = query.order_by(Payment.payment_date.desc()).all()

    # Erwartete Einnahme berechnen (Summe aller final_price der Teilnehmer)
    # Konvertiere zu float um Decimal/float Typ-Konflikte zu vermeiden
    participants = db.query(Participant).filter(Participant.event_id == event_id).all()
    expected_income = float(sum((p.final_price for p in participants), 0))

    return templates.TemplateResponse(
        "payments/list.html",
        {
            "request": request,
            "title": "Zahlungseingänge",
            "payments": payments,
            "expected_income": expected_income
        }
    )


@router.get("/create", response_class=HTMLResponse)
async def create_payment_form(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    participant_id: Optional[int] = None,
    family_id: Optional[int] = None
):
    """Formular zum Erstellen einer neuen Zahlung"""
    participants = db.query(Participant).filter(Participant.event_id == event_id, Participant.is_active == True).all()
    families = db.query(Family).filter(Family.event_id == event_id).all()

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
    event_id: int = Depends(get_current_event_id),
    amount: float = Form(...),
    payment_date: str = Form(...),
    payment_method: Optional[str] = Form(None),
    reference: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    participant_id: Optional[str] = Form(None),
    family_id: Optional[str] = Form(None)
):
    """Erstellt eine neue Zahlung"""
    try:
        # Validierung: Nur Teilnehmer ODER Familie, nicht beides
        if participant_id and family_id:
            flash(request, "Eine Zahlung kann entweder einem Teilnehmer oder einer Familie zugeordnet werden, nicht beides", "error")
            return RedirectResponse(url="/payments/create?error=double_assignment", status_code=303)

        # Pydantic-Validierung
        payment_data = PaymentCreateSchema(
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference=reference,
            notes=notes,
            participant_id=participant_id,
            family_id=family_id
        )

        # Neue Zahlung erstellen
        # payment_date ist bereits ein date-Objekt durch Pydantic-Validierung
        payment = Payment(
            event_id=event_id,
            amount=payment_data.amount,
            payment_date=payment_data.payment_date,
            payment_method=payment_data.payment_method,
            reference=payment_data.reference,
            notes=payment_data.notes,
            participant_id=payment_data.participant_id,
            family_id=payment_data.family_id
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        flash(request, f"Zahlung über {payment_data.amount}€ wurde erfolgreich erfasst", "success")

        # Redirect zurück zur Quelle (Teilnehmer oder Familie)
        if payment_data.participant_id:
            return RedirectResponse(url=f"/participants/{payment_data.participant_id}", status_code=303)
        elif payment_data.family_id:
            return RedirectResponse(url=f"/families/{payment_data.family_id}", status_code=303)
        else:
            return RedirectResponse(url="/payments", status_code=303)

    except ValidationError as e:
        # Pydantic-Validierungsfehler
        logger.warning(f"Validation error creating payment: {e}", exc_info=True)
        first_error = e.errors()[0]
        field_name = first_error['loc'][0] if first_error['loc'] else 'Unbekannt'
        error_msg = first_error['msg']
        flash(request, f"Validierungsfehler ({field_name}): {error_msg}", "error")
        return RedirectResponse(url="/payments/create?error=validation", status_code=303)

    except ValueError as e:
        logger.warning(f"Invalid input for payment creation: {e}", exc_info=True)
        flash(request, f"Ungültige Eingabe: {str(e)}", "error")
        return RedirectResponse(url="/payments/create?error=invalid_input", status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error creating payment: {e}", exc_info=True)
        flash(request, "Zahlung konnte nicht erstellt werden (Datenbankfehler)", "error")
        return RedirectResponse(url="/payments/create?error=db_integrity", status_code=303)

    except DataError as e:
        db.rollback()
        logger.error(f"Invalid data creating payment: {e}", exc_info=True)
        flash(request, "Ungültige Daten eingegeben", "error")
        return RedirectResponse(url="/payments/create?error=invalid_data", status_code=303)

    except Exception as e:
        return handle_db_exception(e, "/payments/create", "Creating payment", db, request)


@router.get("/{payment_id}/edit", response_class=HTMLResponse)
async def edit_payment_form(
    payment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Formular zum Bearbeiten einer Zahlung"""
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.event_id == event_id).first()

    if not payment:
        flash(request, "Zahlung nicht gefunden", "error")
        return RedirectResponse(url="/payments", status_code=303)

    # Teilnehmer und Familien für Dropdown laden
    participants = db.query(Participant).filter(Participant.event_id == event_id).order_by(Participant.first_name, Participant.last_name).all()
    families = db.query(Family).filter(Family.event_id == event_id).order_by(Family.name).all()

    return templates.TemplateResponse(
        "payments/edit.html",
        {
            "request": request,
            "title": "Zahlung bearbeiten",
            "payment": payment,
            "participants": participants,
            "families": families
        }
    )


@router.post("/{payment_id}/edit", response_class=HTMLResponse)
async def update_payment(
    payment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    amount: float = Form(...),
    payment_date: str = Form(...),
    payment_method: Optional[str] = Form(None),
    reference: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    participant_id: Optional[str] = Form(None),
    family_id: Optional[str] = Form(None)
):
    """Aktualisiert eine Zahlung"""
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.event_id == event_id).first()

    if not payment:
        flash(request, "Zahlung nicht gefunden", "error")
        return RedirectResponse(url="/payments", status_code=303)

    try:
        # Validierung: Nur Teilnehmer ODER Familie, nicht beides
        if participant_id and family_id:
            flash(request, "Eine Zahlung kann entweder einem Teilnehmer oder einer Familie zugeordnet werden, nicht beides", "error")
            return RedirectResponse(url=f"/payments/{payment_id}/edit?error=double_assignment", status_code=303)

        # Pydantic-Validierung
        payment_data = PaymentUpdateSchema(
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference=reference,
            notes=notes,
            participant_id=participant_id,
            family_id=family_id
        )

        # Zahlung aktualisieren
        payment.amount = payment_data.amount
        payment.payment_date = payment_data.payment_date
        payment.payment_method = payment_data.payment_method
        payment.reference = payment_data.reference
        payment.notes = payment_data.notes
        payment.participant_id = payment_data.participant_id
        payment.family_id = payment_data.family_id

        db.commit()
        db.refresh(payment)

        logger.info(f"Payment updated: ID {payment_id}, Amount: {payment.amount}€")
        flash(request, "Zahlung erfolgreich aktualisiert", "success")
        return RedirectResponse(url="/payments", status_code=303)

    except ValidationError as e:
        db.rollback()
        logger.warning(f"Validation error updating payment: {e}", exc_info=True)
        flash(request, f"Validierungsfehler: {e}", "error")
        return RedirectResponse(url=f"/payments/{payment_id}/edit?error=validation", status_code=303)

    except ValueError as e:
        db.rollback()
        logger.warning(f"Invalid input for payment update: {e}", exc_info=True)
        flash(request, f"Ungültige Eingabe: {str(e)}", "error")
        return RedirectResponse(url=f"/payments/{payment_id}/edit?error=invalid_input", status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error updating payment: {e}", exc_info=True)
        flash(request, "Zahlung konnte nicht aktualisiert werden (Datenbankfehler)", "error")
        return RedirectResponse(url=f"/payments/{payment_id}/edit?error=db_integrity", status_code=303)

    except DataError as e:
        db.rollback()
        logger.error(f"Invalid data updating payment: {e}", exc_info=True)
        flash(request, "Ungültige Daten eingegeben", "error")
        return RedirectResponse(url=f"/payments/{payment_id}/edit?error=invalid_data", status_code=303)

    except Exception as e:
        return handle_db_exception(e, f"/payments/{payment_id}/edit", "Updating payment", db, request)


@router.post("/{payment_id}/delete")
async def delete_payment(
    request: Request,
    payment_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Löscht eine Zahlung"""
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.event_id == event_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Zahlung nicht gefunden")

    try:
        payment_amount = payment.amount

        db.delete(payment)
        db.commit()
        logger.info(f"Payment deleted: {payment_amount}€ (ID: {payment_id})")

        # Redirect zur Zahlungsliste
        return RedirectResponse(url="/payments", status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Cannot delete payment due to integrity constraint: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Zahlung kann nicht gelöscht werden, da noch Verknüpfungen existieren")

    except Exception as e:
        db.rollback()
        logger.exception(f"Error deleting payment: {e}")
        raise HTTPException(status_code=500, detail="Fehler beim Löschen")


@router.get("/invoice/participant/{participant_id}", response_class=Response)
async def generate_participant_invoice(participant_id: int, db: Session = Depends(get_db)):
    """Generiert eine PDF-Rechnung für einen Teilnehmer oder seine Familie"""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Teilnehmer nicht gefunden")

    # Wenn Teilnehmer zu einer Familie gehört, Familienrechnung generieren
    if participant.family_id:
        family = db.query(Family).filter(Family.id == participant.family_id).first()
        if family:
            generator = InvoiceGenerator(db)
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

    # Andernfalls Einzelrechnung generieren
    generator = InvoiceGenerator(db)
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
    generator = InvoiceGenerator(db)
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


@router.get("/invoice/bulk", response_class=Response)
async def generate_bulk_invoices(db: Session = Depends(get_db), event_id: int = Depends(get_current_event_id)):
    """Generiert alle Rechnungen als ZIP: erst Familien, dann Einzelpersonen ohne Familie"""
    generator = InvoiceGenerator(db)

    # ZIP im Speicher erstellen
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 1. Alle Familienrechnungen
        families = db.query(Family).filter(Family.event_id == event_id).order_by(Family.name).all()

        for family in families:
            # Nur Familien mit Teilnehmern
            if len(family.participants) > 0:
                try:
                    pdf_bytes = generator.generate_family_invoice(family)
                    filename = f"Familien/Sammelrechnung_{family.name.replace(' ', '_').replace('/', '_')}.pdf"
                    zip_file.writestr(filename, pdf_bytes)
                except Exception as e:
                    logger.error(f"Error generating invoice for family {family.id}: {e}")

        # 2. Alle Einzelpersonen OHNE Familie
        participants_without_family = db.query(Participant).filter(
            Participant.event_id == event_id,
            Participant.family_id == None,
            Participant.is_active == True
        ).order_by(Participant.last_name, Participant.first_name).all()

        for participant in participants_without_family:
            try:
                pdf_bytes = generator.generate_participant_invoice(participant)
                filename = f"Einzelpersonen/Rechnung_{participant.last_name}_{participant.first_name}.pdf"
                zip_file.writestr(filename, pdf_bytes)
            except Exception as e:
                logger.error(f"Error generating invoice for participant {participant.id}: {e}")

    # ZIP zurücksetzen und zurückgeben
    zip_buffer.seek(0)

    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=Alle_Rechnungen.zip"
        }
    )
