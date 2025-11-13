"""Expenses (Ausgaben) Router"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional

from app.config import settings
from app.database import get_db
from app.models import Expense, Event

router = APIRouter(prefix="/expenses", tags=["expenses"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse)
async def list_expenses(
    request: Request,
    db: Session = Depends(get_db),
    event_id: Optional[int] = None,
    category: Optional[str] = None
):
    """Liste aller Ausgaben mit Filter"""
    query = db.query(Expense)

    if event_id:
        query = query.filter(Expense.event_id == event_id)
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
    event_id: Optional[int] = None
):
    """Formular zum Erstellen einer neuen Ausgabe"""
    events = db.query(Event).all()

    return templates.TemplateResponse(
        "expenses/create.html",
        {
            "request": request,
            "title": "Neue Ausgabe",
            "events": events,
            "preselected_event_id": event_id
        }
    )


@router.post("/create", response_class=HTMLResponse)
async def create_expense(
    request: Request,
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    amount: float = Form(...),
    expense_date: str = Form(...),
    category: Optional[str] = Form(None),
    receipt_number: Optional[str] = Form(None),
    paid_by: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    event_id: int = Form(...)
):
    """Erstellt eine neue Ausgabe"""
    try:
        # Datum parsen
        expense_date_obj = datetime.strptime(expense_date, "%Y-%m-%d").date()

        # Neue Ausgabe erstellen
        expense = Expense(
            title=title,
            description=description if description else None,
            amount=amount,
            expense_date=expense_date_obj,
            category=category if category else None,
            receipt_number=receipt_number if receipt_number else None,
            paid_by=paid_by if paid_by else None,
            notes=notes if notes else None,
            event_id=event_id
        )

        db.add(expense)
        db.commit()
        db.refresh(expense)

        return RedirectResponse(url="/expenses", status_code=303)

    except Exception as e:
        db.rollback()
        return RedirectResponse(url="/expenses/create?error=1", status_code=303)


@router.get("/{expense_id}/edit", response_class=HTMLResponse)
async def edit_expense_form(request: Request, expense_id: int, db: Session = Depends(get_db)):
    """Formular zum Bearbeiten einer Ausgabe"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        return RedirectResponse(url="/expenses", status_code=303)

    events = db.query(Event).all()

    return templates.TemplateResponse(
        "expenses/edit.html",
        {
            "request": request,
            "title": f"Ausgabe bearbeiten: {expense.title}",
            "expense": expense,
            "events": events
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
    event_id: int = Form(...)
):
    """Aktualisiert eine Ausgabe"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        return RedirectResponse(url="/expenses", status_code=303)

    try:
        # Datum parsen
        expense_date_obj = datetime.strptime(expense_date, "%Y-%m-%d").date()

        # Ausgabe aktualisieren
        expense.title = title
        expense.description = description if description else None
        expense.amount = amount
        expense.expense_date = expense_date_obj
        expense.category = category if category else None
        expense.receipt_number = receipt_number if receipt_number else None
        expense.paid_by = paid_by if paid_by else None
        expense.notes = notes if notes else None
        expense.event_id = event_id

        db.commit()

        return RedirectResponse(url="/expenses", status_code=303)

    except Exception as e:
        db.rollback()
        return RedirectResponse(url=f"/expenses/{expense_id}/edit?error=1", status_code=303)


@router.post("/{expense_id}/delete")
async def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Löscht eine Ausgabe"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Ausgabe nicht gefunden")

    try:
        db.delete(expense)
        db.commit()
        return RedirectResponse(url="/expenses", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Löschen")
