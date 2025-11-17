"""Expenses (Ausgaben) Router"""
import logging
from pathlib import Path
from fastapi import APIRouter, Request, Depends, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
from datetime import date, datetime
from typing import Optional
from pydantic import ValidationError

from app.database import get_db
from app.models import Expense, Event, Participant
from app.dependencies import get_current_event_id
from app.utils.error_handler import handle_db_exception
from app.utils.flash import flash
from app.utils.file_upload import save_receipt_file, delete_receipt_file
from app.utils.datetime_utils import utcnow
from app.schemas import ExpenseCreateSchema, ExpenseUpdateSchema
from app.templates_config import templates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/", response_class=HTMLResponse)
async def list_expenses(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    event_id_param: Optional[int] = None,
    category: Optional[str] = None,
    search: Optional[str] = ""
):
    """Liste aller Ausgaben mit Filter und Suche"""
    query = db.query(Expense).filter(Expense.event_id == event_id)

    if event_id_param:
        query = query.filter(Expense.event_id == event_id_param)
    if category:
        query = query.filter(Expense.category == category)

    # Volltextsuche
    if search and search.strip():
        search_filter = f"%{search}%"
        query = query.filter(
            (Expense.title.ilike(search_filter)) |
            (Expense.description.ilike(search_filter)) |
            (Expense.paid_by.ilike(search_filter)) |
            (Expense.receipt_number.ilike(search_filter))
        )

    expenses = query.order_by(Expense.expense_date.desc()).all()

    # Kategorien für Filter
    categories = db.query(Expense.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]

    return templates.TemplateResponse(
        "expenses/list.html",
        {
            "request": request,
            "title": "Ausgaben",
            "expenses": expenses,
            "categories": categories,
            "search": search,
            "selected_category": category
        }
    )


@router.get("/create", response_class=HTMLResponse)
async def create_expense_form(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Formular zum Erstellen einer neuen Ausgabe"""
    event = db.query(Event).filter(Event.id == event_id).first()

    # Vorhandene Kategorien aus der Datenbank laden (distinct)
    categories_query = db.query(Expense.category).filter(Expense.category.isnot(None)).distinct().all()
    existing_categories = [c[0] for c in categories_query if c[0]]

    # Standard-Kategorien hinzufügen, falls noch nicht vorhanden
    default_categories = ["Unterkunft", "Verpflegung", "Transport", "Aktivitäten", "Material", "Sonstiges"]
    all_categories = list(set(existing_categories + default_categories))
    all_categories.sort()

    # Teilnehmer für "Bezahlt von" Dropdown laden
    participants = db.query(Participant).filter(Participant.event_id == event_id).order_by(Participant.last_name, Participant.first_name).all()
    participant_names = [f"{p.first_name} {p.last_name}" for p in participants]

    return templates.TemplateResponse(
        "expenses/create.html",
        {
            "request": request,
            "title": "Neue Ausgabe",
            "event": event,
            "categories": all_categories,
            "participants": participant_names
        }
    )


@router.post("/create", response_class=HTMLResponse)
async def create_expense(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    amount: float = Form(...),
    expense_date: str = Form(...),
    category: Optional[str] = Form(None),
    receipt_number: Optional[str] = Form(None),
    paid_by: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    receipt_file: Optional[UploadFile] = File(None),
):
    """Erstellt eine neue Ausgabe"""
    try:
        # Pydantic-Validierung
        expense_data = ExpenseCreateSchema(
            title=title,
            description=description,
            amount=amount,
            expense_date=expense_date,
            category=category,
            receipt_number=receipt_number,
            paid_by=paid_by,
            notes=notes
        )

        # Neue Ausgabe erstellen (expense_date ist bereits ein date-Objekt)
        expense = Expense(
            title=expense_data.title,
            description=expense_data.description,
            amount=expense_data.amount,
            expense_date=expense_data.expense_date,
            category=expense_data.category,
            receipt_number=expense_data.receipt_number,
            paid_by=expense_data.paid_by,
            notes=expense_data.notes,
            event_id=event_id
        )

        db.add(expense)
        db.commit()
        db.refresh(expense)

        # Beleg-Upload verarbeiten (falls vorhanden)
        if receipt_file and receipt_file.filename:
            file_path, error = await save_receipt_file(
                receipt_file,
                event_id,
                expense.id,
                "expenses"
            )

            if error:
                logger.warning(f"Failed to upload receipt for expense {expense.id}: {error}")
                flash(request, f"Ausgabe erstellt, aber Beleg-Upload fehlgeschlagen: {error}", "warning")
            else:
                expense.receipt_file_path = file_path
                db.commit()
                logger.info(f"Receipt uploaded for expense {expense.id}: {file_path}")

        flash(request, f"Ausgabe '{expense.title}' über {expense_data.amount}€ wurde erfolgreich erfasst", "success")
        return RedirectResponse(url="/expenses", status_code=303)

    except ValidationError as e:
        # Pydantic-Validierungsfehler
        logger.warning(f"Validation error creating expense: {e}", exc_info=True)
        first_error = e.errors()[0]
        field_name = first_error['loc'][0] if first_error['loc'] else 'Unbekannt'
        error_msg = first_error['msg']
        flash(request, f"Validierungsfehler ({field_name}): {error_msg}", "error")
        return RedirectResponse(url="/expenses/create?error=validation", status_code=303)

    except ValueError as e:
        logger.warning(f"Invalid input for expense creation: {e}", exc_info=True)
        flash(request, f"Ungültige Eingabe: {str(e)}", "error")
        return RedirectResponse(url="/expenses/create?error=invalid_input", status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error creating expense: {e}", exc_info=True)
        flash(request, "Ausgabe konnte nicht erstellt werden (Datenbankfehler)", "error")
        return RedirectResponse(url="/expenses/create?error=db_integrity", status_code=303)

    except DataError as e:
        db.rollback()
        logger.error(f"Invalid data creating expense: {e}", exc_info=True)
        flash(request, "Ungültige Daten eingegeben", "error")
        return RedirectResponse(url="/expenses/create?error=invalid_data", status_code=303)

    except Exception as e:
        return handle_db_exception(e, "/expenses/create", "Creating expense", db, request)


@router.get("/{expense_id}/edit", response_class=HTMLResponse)
async def edit_expense_form(
    request: Request,
    expense_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Formular zum Bearbeiten einer Ausgabe"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.event_id == event_id
    ).first()

    if not expense:
        return RedirectResponse(url="/expenses", status_code=303)

    event = db.query(Event).filter(Event.id == expense.event_id).first()

    # Vorhandene Kategorien aus der Datenbank laden (distinct)
    categories_query = db.query(Expense.category).filter(Expense.category.isnot(None)).distinct().all()
    existing_categories = [c[0] for c in categories_query if c[0]]

    # Standard-Kategorien hinzufügen, falls noch nicht vorhanden
    default_categories = ["Unterkunft", "Verpflegung", "Transport", "Aktivitäten", "Material", "Sonstiges"]
    all_categories = list(set(existing_categories + default_categories))
    all_categories.sort()

    # Teilnehmer für "Bezahlt von" Dropdown laden
    participants = db.query(Participant).filter(Participant.event_id == expense.event_id).order_by(Participant.last_name, Participant.first_name).all()
    participant_names = [f"{p.first_name} {p.last_name}" for p in participants]

    return templates.TemplateResponse(
        "expenses/edit.html",
        {
            "request": request,
            "title": f"Ausgabe bearbeiten: {expense.title}",
            "expense": expense,
            "event": event,
            "categories": all_categories,
            "participants": participant_names
        }
    )


@router.post("/{expense_id}/edit", response_class=HTMLResponse)
async def update_expense(
    request: Request,
    expense_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    amount: float = Form(...),
    expense_date: str = Form(...),
    category: Optional[str] = Form(None),
    receipt_number: Optional[str] = Form(None),
    paid_by: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    receipt_file: Optional[UploadFile] = File(None),
    remove_receipt: Optional[str] = Form(None),
):
    """Aktualisiert eine Ausgabe"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.event_id == event_id
    ).first()

    if not expense:
        return RedirectResponse(url="/expenses", status_code=303)

    try:
        # Pydantic-Validierung
        expense_data = ExpenseUpdateSchema(
            title=title,
            description=description,
            amount=amount,
            expense_date=expense_date,
            category=category,
            receipt_number=receipt_number,
            paid_by=paid_by,
            notes=notes
        )

        # Ausgabe aktualisieren (expense_date ist bereits ein date-Objekt)
        expense.title = expense_data.title
        expense.description = expense_data.description
        expense.amount = expense_data.amount
        expense.expense_date = expense_data.expense_date
        expense.category = expense_data.category
        expense.receipt_number = expense_data.receipt_number
        expense.paid_by = expense_data.paid_by
        expense.notes = expense_data.notes

        # Beleg entfernen, falls gewünscht
        if remove_receipt == "true" and expense.receipt_file_path:
            delete_receipt_file(expense.receipt_file_path)
            expense.receipt_file_path = None
            logger.info(f"Receipt removed from expense {expense_id}")

        # Neuen Beleg hochladen, falls vorhanden
        if receipt_file and receipt_file.filename:
            # Alten Beleg löschen
            if expense.receipt_file_path:
                delete_receipt_file(expense.receipt_file_path)

            # Neuen Beleg speichern
            file_path, error = await save_receipt_file(
                receipt_file,
                expense.event_id,
                expense.id,
                "expenses"
            )

            if error:
                logger.warning(f"Failed to upload receipt for expense {expense.id}: {error}")
                flash(request, f"Ausgabe aktualisiert, aber Beleg-Upload fehlgeschlagen: {error}", "warning")
            else:
                expense.receipt_file_path = file_path
                logger.info(f"Receipt updated for expense {expense.id}: {file_path}")

        db.commit()

        flash(request, f"Ausgabe '{expense.title}' wurde erfolgreich aktualisiert", "success")
        return RedirectResponse(url="/expenses", status_code=303)

    except ValidationError as e:
        # Pydantic-Validierungsfehler
        logger.warning(f"Validation error updating expense: {e}", exc_info=True)
        first_error = e.errors()[0]
        field_name = first_error['loc'][0] if first_error['loc'] else 'Unbekannt'
        error_msg = first_error['msg']
        flash(request, f"Validierungsfehler ({field_name}): {error_msg}", "error")
        return RedirectResponse(url=f"/expenses/{expense_id}/edit?error=validation", status_code=303)

    except ValueError as e:
        logger.warning(f"Invalid input for expense update: {e}", exc_info=True)
        flash(request, f"Ungültige Eingabe: {str(e)}", "error")
        return RedirectResponse(url=f"/expenses/{expense_id}/edit?error=invalid_input", status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error updating expense: {e}", exc_info=True)
        flash(request, "Ausgabe konnte nicht aktualisiert werden (Datenbankfehler)", "error")
        return RedirectResponse(url=f"/expenses/{expense_id}/edit?error=db_integrity", status_code=303)

    except DataError as e:
        db.rollback()
        logger.error(f"Invalid data updating expense: {e}", exc_info=True)
        flash(request, "Ungültige Daten eingegeben", "error")
        return RedirectResponse(url=f"/expenses/{expense_id}/edit?error=invalid_data", status_code=303)

    except Exception as e:
        return handle_db_exception(e, f"/expenses/{expense_id}/edit", "Updating expense", db, request)


@router.post("/{expense_id}/toggle-settled")
async def toggle_settled(expense_id: int, db: Session = Depends(get_db), event_id: int = Depends(get_current_event_id)):
    """
    Toggelt den Beglichen/Erstattet-Status einer Ausgabe.
    - Wenn paid_by leer: normale Kassenausgabe → Beglichen
    - Wenn paid_by ausgefüllt: vorgestreckte Ausgabe → Erstattet
    Synchronisiert automatisch mit Tasks.
    """
    from app.models import Task
    from datetime import datetime

    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Ausgabe nicht gefunden")

    try:
        expense.is_settled = not expense.is_settled

        # Nur bei vorgestreckten Ausgaben (paid_by ist ausgefüllt) Tasks synchronisieren
        if expense.paid_by:
            task = db.query(Task).filter(
                Task.event_id == event_id,
                Task.task_type == "expense_reimbursement",
                Task.reference_id == expense_id
            ).first()

            if expense.is_settled:
                # Ausgabe wurde erstattet → Task als erledigt markieren/erstellen
                if task:
                    task.is_completed = True
                    task.completed_at = utcnow()
                else:
                    new_task = Task(
                        task_type="expense_reimbursement",
                        reference_id=expense_id,
                        is_completed=True,
                        event_id=event_id
                    )
                    db.add(new_task)
            else:
                # Ausgabe wurde als nicht erstattet markiert → Task löschen falls vorhanden
                if task:
                    db.delete(task)

        db.commit()
        return RedirectResponse(url="/expenses", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren: {str(e)}")


@router.get("/{expense_id}/receipt/download")
async def download_expense_receipt(
    expense_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Lädt den Beleg einer Ausgabe herunter"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.event_id == event_id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Ausgabe nicht gefunden")

    if not expense.receipt_file_path:
        raise HTTPException(status_code=404, detail="Kein Beleg vorhanden")

    file_path = Path(expense.receipt_file_path)

    if not file_path.exists():
        logger.error(f"Receipt file not found: {expense.receipt_file_path}")
        raise HTTPException(status_code=404, detail="Beleg-Datei wurde nicht gefunden")

    # MIME-Type basierend auf Dateiendung
    mime_type = "application/octet-stream"
    if file_path.suffix.lower() == '.pdf':
        mime_type = "application/pdf"
    elif file_path.suffix.lower() in ['.jpg', '.jpeg']:
        mime_type = "image/jpeg"
    elif file_path.suffix.lower() == '.png':
        mime_type = "image/png"

    logger.info(f"Downloading receipt for expense {expense_id}: {expense.receipt_file_path}")

    return FileResponse(
        path=file_path,
        media_type=mime_type,
        filename=file_path.name
    )


@router.post("/{expense_id}/delete")
async def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Löscht eine Ausgabe"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.event_id == event_id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Ausgabe nicht gefunden")

    try:
        expense_title = expense.title

        # Beleg löschen, falls vorhanden
        if expense.receipt_file_path:
            delete_receipt_file(expense.receipt_file_path)
            logger.info(f"Receipt deleted for expense {expense_id}")

        db.delete(expense)
        db.commit()
        logger.info(f"Expense deleted: {expense_title} (ID: {expense_id})")
        return RedirectResponse(url="/expenses", status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Cannot delete expense due to integrity constraint: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Ausgabe kann nicht gelöscht werden, da noch Verknüpfungen existieren")

    except Exception as e:
        db.rollback()
        logger.exception(f"Error deleting expense: {e}")
        raise HTTPException(status_code=500, detail="Fehler beim Löschen")
