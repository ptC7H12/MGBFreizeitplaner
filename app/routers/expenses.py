"""Expenses (Ausgaben) Router"""
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
from app.models import Expense, Event
from app.dependencies import get_current_event_id
from app.utils.error_handler import handle_db_exception
from app.utils.flash import flash
from app.schemas import ExpenseCreateSchema, ExpenseUpdateSchema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expenses", tags=["expenses"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse)
async def list_expenses(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    event_id_param: Optional[int] = None,
    category: Optional[str] = None
):
    """Liste aller Ausgaben mit Filter"""
    query = db.query(Expense).filter(Expense.event_id == event_id)

    if event_id_param:
        query = query.filter(Expense.event_id == event_id_param)
    if category:
        query = query.filter(Expense.category == category)

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
            "categories": categories
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

    return templates.TemplateResponse(
        "expenses/create.html",
        {
            "request": request,
            "title": "Neue Ausgabe",
            "event": event,
            "preselected_event_id": event_id
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

        # Datum parsen (bereits validiert durch Pydantic)
        expense_date_obj = datetime.strptime(expense_data.expense_date, "%Y-%m-%d").date()

        # Neue Ausgabe erstellen
        expense = Expense(
            title=expense_data.title,
            description=expense_data.description,
            amount=expense_data.amount,
            expense_date=expense_date_obj,
            category=expense_data.category,
            receipt_number=expense_data.receipt_number,
            paid_by=expense_data.paid_by,
            notes=expense_data.notes,
            event_id=event_id
        )

        db.add(expense)
        db.commit()
        db.refresh(expense)

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
async def edit_expense_form(request: Request, expense_id: int, db: Session = Depends(get_db)):
    """Formular zum Bearbeiten einer Ausgabe"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        return RedirectResponse(url="/expenses", status_code=303)

    event = db.query(Event).filter(Event.id == expense.event_id).first()

    return templates.TemplateResponse(
        "expenses/edit.html",
        {
            "request": request,
            "title": f"Ausgabe bearbeiten: {expense.title}",
            "expense": expense,
            "event": event
        }
    )


@router.post("/{expense_id}/edit", response_class=HTMLResponse)
async def update_expense(
    request: Request,
    expense_id: int,
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    amount: float = Form(...),
    expense_date: str = Form(...),
    category: Optional[str] = Form(None),
    receipt_number: Optional[str] = Form(None),
    paid_by: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    """Aktualisiert eine Ausgabe"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

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

        # Datum parsen (bereits validiert durch Pydantic)
        expense_date_obj = datetime.strptime(expense_data.expense_date, "%Y-%m-%d").date()

        # Ausgabe aktualisieren
        expense.title = expense_data.title
        expense.description = expense_data.description
        expense.amount = expense_data.amount
        expense.expense_date = expense_date_obj
        expense.category = expense_data.category
        expense.receipt_number = expense_data.receipt_number
        expense.paid_by = expense_data.paid_by
        expense.notes = expense_data.notes

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


@router.post("/{expense_id}/delete")
async def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Löscht eine Ausgabe"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Ausgabe nicht gefunden")

    try:
        expense_title = expense.title
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
