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

    # === SOLL-Werte (Zu erwartende Werte) ===

    # Erwartete Einnahmen durch Teilnehmer
    participants = db.query(Participant).filter(
        Participant.event_id == event_id,
        Participant.is_active == True
    ).all()
    expected_income_participants = sum(p.final_price for p in participants)

    # Sonstige Einnahmen (Zuschüsse/Förderungen)
    other_income = db.query(func.sum(Income.amount)).filter(
        Income.event_id == event_id
    ).scalar() or 0.0

    # Alle Ausgaben (gesamt)
    total_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.event_id == event_id
    ).scalar() or 0.0

    # Erwarteter Saldo
    expected_balance = expected_income_participants + other_income - total_expenses

    # === IST-Werte (Getätigte Zahlungen) ===

    # Tatsächliche Einnahmen durch Teilnehmer-Zahlungen
    actual_income_participants = db.query(func.sum(Payment.amount)).filter(
        Payment.event_id == event_id
    ).scalar() or 0.0

    # Sonstige Einnahmen (gleich wie Soll, da diese direkt gebucht werden)
    actual_other_income = other_income

    # Beglichene Ausgaben
    settled_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.event_id == event_id,
        Expense.is_settled == True
    ).scalar() or 0.0

    # Aktueller Saldo
    actual_balance = actual_income_participants + actual_other_income - settled_expenses

    # === DIFFERENZEN ===

    # Ausstehende Einnahmen (Teilnehmer)
    outstanding_income_participants = expected_income_participants - actual_income_participants

    # Ausstehende sonstige Einnahmen (immer 0, da direkt gebucht)
    outstanding_other_income = 0.0

    # Noch zu begleichende Ausgaben
    open_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.event_id == event_id,
        Expense.is_settled == False
    ).scalar() or 0.0

    # Differenz Saldo
    balance_difference = expected_balance - actual_balance

    # Status-Badge berechnen (basierend auf aktuellem Saldo)
    if actual_balance < 0:
        status = {"text": "Kritisch", "color": "red"}
    elif actual_balance < 500:
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
            # SOLL-Werte
            "expected_income_participants": expected_income_participants,
            "expected_other_income": other_income,
            "expected_expenses": total_expenses,
            "expected_balance": expected_balance,
            # IST-Werte
            "actual_income_participants": actual_income_participants,
            "actual_other_income": actual_other_income,
            "actual_expenses": settled_expenses,
            "actual_balance": actual_balance,
            # DIFFERENZEN
            "outstanding_income_participants": outstanding_income_participants,
            "outstanding_other_income": outstanding_other_income,
            "outstanding_expenses": open_expenses,
            "balance_difference": balance_difference,
            # Status und Kategorien
            "status": status,
            "categories": categories
        }
    )
