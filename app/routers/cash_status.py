"""Cash Status Router - Kassenstand-Übersicht"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Payment, Expense, Income, Participant
from app.dependencies import get_current_event_id
from app.templates_config import templates

router = APIRouter(prefix="/cash-status", tags=["cash_status"])


@router.get("/", response_class=HTMLResponse)
async def cash_status(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Zeigt den aktuellen Kassenstand mit detaillierter Aufschlüsselung"""

    # 1. Einnahmen durch Zahlungen
    total_payments = db.query(func.sum(Payment.amount)).filter(
        Payment.event_id == event_id
    ).scalar() or 0.0

    # 2. Zuschüsse/Einnahmen (Incomes)
    total_incomes = db.query(func.sum(Income.amount)).filter(
        Income.event_id == event_id
    ).scalar() or 0.0

    # 3. Beglichene Ausgaben
    settled_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.event_id == event_id,
        Expense.is_settled == True
    ).scalar() or 0.0

    # 4. Offene Ausgaben
    open_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.event_id == event_id,
        Expense.is_settled == False
    ).scalar() or 0.0

    # 5. Vorgestreckte Beträge (nicht erstattete Ausgaben)
    unreimbursed_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.event_id == event_id,
        Expense.is_reimbursed == False,
        Expense.paid_by.isnot(None)
    ).scalar() or 0.0

    # 6. Erwartete Einnahme durch Teilnehmer
    participants = db.query(Participant).filter(
        Participant.event_id == event_id,
        Participant.is_active == True
    ).all()
    expected_income = sum(p.final_price for p in participants)

    # 7. Noch zu erwartende Zahlungen
    outstanding_payments = expected_income - total_payments

    # 8. Netto-Kassenstand (aktuell verfügbar)
    net_balance = total_payments + total_incomes - settled_expenses

    # 9. Brutto-Kassenstand (theoretischer Endstand)
    total_expenses_all = settled_expenses + open_expenses
    gross_balance = expected_income + total_incomes - total_expenses_all

    # Status-Badge berechnen
    if net_balance < 0:
        status = {"text": "Kritisch", "color": "red"}
    elif net_balance < 500:
        status = {"text": "Knapp", "color": "yellow"}
    else:
        status = {"text": "Gesund", "color": "green"}

    # Ausgaben nach Kategorie
    expenses_by_category = db.query(
        Expense.category,
        func.sum(Expense.amount).label("total"),
        func.count(Expense.id).label("count")
    ).filter(
        Expense.event_id == event_id
    ).group_by(Expense.category).all()

    # Kategorien aufbereiten
    categories = []
    for cat, total, count in expenses_by_category:
        categories.append({
            "name": cat if cat else "Sonstige",
            "total": total,
            "count": count
        })

    # Nach Betrag sortieren
    categories.sort(key=lambda x: x["total"], reverse=True)

    return templates.TemplateResponse(
        "cash_status/overview.html",
        {
            "request": request,
            "title": "Kassenstand",
            "total_payments": total_payments,
            "total_incomes": total_incomes,
            "settled_expenses": settled_expenses,
            "open_expenses": open_expenses,
            "unreimbursed_expenses": unreimbursed_expenses,
            "expected_income": expected_income,
            "outstanding_payments": outstanding_payments,
            "net_balance": net_balance,
            "gross_balance": gross_balance,
            "status": status,
            "categories": categories
        }
    )
