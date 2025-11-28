"""Dashboard Router"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract
from datetime import date, timedelta

from app.database import get_db
from app.models import Participant, Payment, Expense, Event, Family, Role, Income, Ruleset
from app.dependencies import get_current_event_id
from app.templates_config import templates
from app.services.price_calculator import PriceCalculator
from app.routers.cash_status import calculate_expected_subsidies, calculate_base_prices_sum

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db), event_id: int = Depends(get_current_event_id)):
    """Hauptdashboard mit Statistiken"""

    # Statistiken sammeln (gefiltert nach event_id)
    total_participants = db.query(func.count(Participant.id)).filter(Participant.event_id == event_id).scalar() or 0
    total_families = db.query(func.count(Family.id)).filter(Family.event_id == event_id).scalar() or 0

    # Finanzielle Übersicht (gefiltert nach event_id)
    # Einnahmen - Konvertiere Decimal zu float um Typ-Konflikte zu vermeiden

    # Basispreise ohne Rabatte berechnen
    base_prices_sum = calculate_base_prices_sum(db, event_id)

    # Zahlungseingänge mit Rabatten und manuellen Preisen (was Teilnehmer tatsächlich zahlen sollen)
    # Verwende final_price (berücksichtigt manual_price_override UND calculated_price)
    participants = db.query(Participant).filter(
        Participant.event_id == event_id,
        Participant.is_active == True
    ).all()
    soll_zahlungseingaenge = float(sum((p.final_price for p in participants), 0))

    # Erwartete Zuschüsse berechnen (rollenbasiert + Familienrabatt)
    # WICHTIG: Diese Berechnung muss identisch sein mit der Summe im Zuschüsse-Tab!
    soll_sonstige_einnahmen = calculate_expected_subsidies(db, event_id)

    # Gesamteinnahmen (Soll) = Zahlungseingänge + Sonstige Einnahmen (Zuschüsse)
    soll_einnahmen_gesamt = soll_zahlungseingaenge + soll_sonstige_einnahmen

    ist_zahlungseingaenge = float(db.query(func.sum(Payment.amount)).filter(Payment.event_id == event_id).scalar() or 0)
    # Sonstige Einnahmen (z.B. erhaltene Zuschüsse, Spenden)
    # Aus Income-Tabelle abfragen
    ist_sonstige_einnahmen = float(db.query(func.sum(Income.amount)).filter(Income.event_id == event_id).scalar() or 0)
    ist_einnahmen_gesamt = ist_zahlungseingaenge + ist_sonstige_einnahmen

    # Ausgaben
    soll_ausgaben_gesamt = float(db.query(func.sum(Expense.amount)).filter(Expense.event_id == event_id).scalar() or 0)
    ausgaben_beglichen = float(db.query(func.sum(Expense.amount)).filter(
        Expense.event_id == event_id,
        Expense.is_settled == True
    ).scalar() or 0)

    # Saldo: Soll-Einnahmen - Soll-Ausgaben (korrigiert!)
    saldo_gesamt = soll_einnahmen_gesamt - soll_ausgaben_gesamt

    # Offene Beträge
    offene_zahlungseingaenge = soll_zahlungseingaenge - ist_zahlungseingaenge
    offene_ausgaben = soll_ausgaben_gesamt - ausgaben_beglichen

    # Zahlungsquoten
    zahlungsquote_eingaenge = (ist_zahlungseingaenge / soll_zahlungseingaenge * 100) if soll_zahlungseingaenge > 0 else 0.0
    zahlungsquote_ausgaben = (ausgaben_beglichen / soll_ausgaben_gesamt * 100) if soll_ausgaben_gesamt > 0 else 0.0

    stats = {
        "total_participants": total_participants,
        "total_families": total_families,
        # Einnahmen
        "soll_zahlungseingaenge": soll_zahlungseingaenge,
        "soll_sonstige_einnahmen": soll_sonstige_einnahmen,
        "soll_einnahmen_gesamt": soll_einnahmen_gesamt,
        "ist_zahlungseingaenge": ist_zahlungseingaenge,
        "ist_sonstige_einnahmen": ist_sonstige_einnahmen,
        "ist_einnahmen_gesamt": ist_einnahmen_gesamt,
        # Ausgaben
        "soll_ausgaben_gesamt": soll_ausgaben_gesamt,
        "ausgaben_beglichen": ausgaben_beglichen,
        "offene_ausgaben": offene_ausgaben,
        # Saldo & Offene Beträge
        "saldo_gesamt": saldo_gesamt,
        "offene_zahlungseingaenge": offene_zahlungseingaenge,
        # Zahlungsquoten
        "zahlungsquote_eingaenge": zahlungsquote_eingaenge,
        "zahlungsquote_ausgaben": zahlungsquote_ausgaben,
        # Legacy (für Kompatibilität) - Ziel = Basispreis ohne Rabatte
        "total_revenue_target": base_prices_sum,
        "total_payments": ist_zahlungseingaenge,
        "total_expenses": soll_ausgaben_gesamt,
        "outstanding": offene_zahlungseingaenge,
        "balance": saldo_gesamt
    }

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "Dashboard", "stats": stats}
    )


@router.get("/api/age-distribution", response_class=JSONResponse)
async def get_age_distribution(db: Session = Depends(get_db), event_id: int = Depends(get_current_event_id)):
    """API: Altersverteilung der Teilnehmer"""
    participants = db.query(Participant).options(
        joinedload(Participant.event)
    ).filter(
        Participant.event_id == event_id,
        Participant.is_active == True
    ).all()

    # Altersgruppen definieren
    age_groups = {
        "0-5": 0,
        "6-11": 0,
        "12-17": 0,
        "18-25": 0,
        "26-40": 0,
        "41+": 0
    }

    for p in participants:
        age = p.age_at_event
        if age <= 5:
            age_groups["0-5"] += 1
        elif age <= 11:
            age_groups["6-11"] += 1
        elif age <= 17:
            age_groups["12-17"] += 1
        elif age <= 25:
            age_groups["18-25"] += 1
        elif age <= 40:
            age_groups["26-40"] += 1
        else:
            age_groups["41+"] += 1

    return {
        "labels": list(age_groups.keys()),
        "data": list(age_groups.values())
    }


@router.get("/api/payment-timeline", response_class=JSONResponse)
async def get_payment_timeline(db: Session = Depends(get_db), event_id: int = Depends(get_current_event_id)):
    """API: Zahlungsverlauf über Zeit"""
    # Gruppiere Zahlungen nach Datum
    payments_by_date = db.query(
        func.date(Payment.payment_date).label('date'),
        func.sum(Payment.amount).label('total')
    ).filter(
        Payment.event_id == event_id
    ).group_by(
        func.date(Payment.payment_date)
    ).order_by('date').all()

    # Erstelle kumulative Summen
    dates = []
    amounts = []
    cumulative = 0.0

    for payment_date, amount in payments_by_date:
        dates.append(str(payment_date))
        cumulative += float(amount)
        amounts.append(round(cumulative, 2))

    return {
        "labels": dates,
        "data": amounts
    }


@router.get("/api/role-distribution", response_class=JSONResponse)
async def get_role_distribution(db: Session = Depends(get_db), event_id: int = Depends(get_current_event_id)):
    """API: Verteilung nach Rollen"""
    # Gruppiere Teilnehmer nach Rollen
    role_counts = db.query(
        Role.display_name,
        func.count(Participant.id).label('count')
    ).join(
        Participant, Participant.role_id == Role.id
    ).filter(
        Participant.event_id == event_id,
        Participant.is_active == True
    ).group_by(
        Role.display_name
    ).all()

    return {
        "labels": [role for role, _ in role_counts],
        "data": [count for _, count in role_counts]
    }


@router.get("/api/expense-categories", response_class=JSONResponse)
async def get_expense_categories(db: Session = Depends(get_db), event_id: int = Depends(get_current_event_id)):
    """API: Ausgaben nach Kategorien"""
    # Gruppiere Ausgaben nach Kategorie
    expenses_by_category = db.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.event_id == event_id
    ).group_by(
        Expense.category
    ).all()

    return {
        "labels": [cat or "Ohne Kategorie" for cat, _ in expenses_by_category],
        "data": [float(total) for _, total in expenses_by_category]
    }


@router.get("/api/payment-methods", response_class=JSONResponse)
async def get_payment_methods(db: Session = Depends(get_db), event_id: int = Depends(get_current_event_id)):
    """API: Zahlungsmethoden-Verteilung"""
    # Gruppiere Zahlungen nach Methode
    payments_by_method = db.query(
        Payment.payment_method,
        func.sum(Payment.amount).label('total')
    ).filter(
        Payment.event_id == event_id
    ).group_by(
        Payment.payment_method
    ).all()

    return {
        "labels": [method or "Unbekannt" for method, _ in payments_by_method],
        "data": [float(total) for _, total in payments_by_method]
    }
