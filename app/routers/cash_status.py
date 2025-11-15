"""Cash Status Router - Kassenstand-Übersicht"""
import logging
from datetime import date, datetime
from io import BytesIO, StringIO
from typing import Optional
import csv

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, union_all, literal
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from app.database import get_db
from app.models import Payment, Expense, Income, Participant, Family
from app.dependencies import get_current_event_id
from app.templates_config import templates

logger = logging.getLogger(__name__)

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


@router.get("/history", response_class=HTMLResponse)
async def transaction_history(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    date_from: Optional[str] = Query(None, description="Startdatum (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Enddatum (YYYY-MM-DD)"),
    transaction_type: Optional[str] = Query(None, description="Transaktionstyp (payment/income/expense)"),
    min_amount: Optional[float] = Query(None, description="Minimalbetrag"),
    max_amount: Optional[float] = Query(None, description="Maximalbetrag"),
    search: Optional[str] = Query(None, description="Suchbegriff"),
):
    """
    Zeigt die vollständige Transaktionshistorie mit allen Ein- und Ausgängen
    """
    logger.info(f"Loading transaction history for event {event_id} with filters")

    # === Query für Zahlungseingänge (Payments) ===
    payments_query = db.query(
        Payment.id.label('id'),
        literal('payment').label('type'),
        Payment.amount.label('amount'),
        Payment.payment_date.label('transaction_date'),
        Payment.payment_method.label('method'),
        Payment.reference.label('reference'),
        Payment.notes.label('description'),
        Participant.first_name.label('participant_first_name'),
        Participant.last_name.label('participant_last_name'),
        Family.name.label('family_name'),
        Payment.created_at.label('created_at')
    ).outerjoin(
        Participant, Payment.participant_id == Participant.id
    ).outerjoin(
        Family, Payment.family_id == Family.id
    ).filter(
        Payment.event_id == event_id
    )

    # === Query für sonstige Einnahmen (Incomes) ===
    incomes_query = db.query(
        Income.id.label('id'),
        literal('income').label('type'),
        Income.amount.label('amount'),
        Income.date.label('transaction_date'),
        literal(None).label('method'),
        Income.name.label('reference'),
        Income.description.label('description'),
        literal(None).label('participant_first_name'),
        literal(None).label('participant_last_name'),
        literal(None).label('family_name'),
        literal(None).label('created_at')
    ).filter(
        Income.event_id == event_id
    )

    # === Query für Ausgaben (Expenses) ===
    expenses_query = db.query(
        Expense.id.label('id'),
        literal('expense').label('type'),
        (Expense.amount * -1).label('amount'),  # Negativ für Ausgaben
        Expense.expense_date.label('transaction_date'),
        Expense.category.label('method'),
        Expense.title.label('reference'),
        Expense.description.label('description'),
        literal(None).label('participant_first_name'),
        literal(None).label('participant_last_name'),
        literal(None).label('family_name'),
        Expense.created_at.label('created_at')
    ).filter(
        Expense.event_id == event_id
    )

    # === Filter anwenden ===

    # Datumsfilter
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
            payments_query = payments_query.filter(Payment.payment_date >= date_from_obj)
            incomes_query = incomes_query.filter(Income.date >= date_from_obj)
            expenses_query = expenses_query.filter(Expense.expense_date >= date_from_obj)
        except ValueError:
            logger.warning(f"Invalid date_from format: {date_from}")

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
            payments_query = payments_query.filter(Payment.payment_date <= date_to_obj)
            incomes_query = incomes_query.filter(Income.date <= date_to_obj)
            expenses_query = expenses_query.filter(Expense.expense_date <= date_to_obj)
        except ValueError:
            logger.warning(f"Invalid date_to format: {date_to}")

    # Betragsfilter
    if min_amount is not None:
        payments_query = payments_query.filter(Payment.amount >= min_amount)
        incomes_query = incomes_query.filter(Income.amount >= min_amount)
        expenses_query = expenses_query.filter(Expense.amount >= min_amount)

    if max_amount is not None:
        payments_query = payments_query.filter(Payment.amount <= max_amount)
        incomes_query = incomes_query.filter(Income.amount <= max_amount)
        expenses_query = expenses_query.filter(Expense.amount <= max_amount)

    # Typ-Filter
    queries_to_union = []
    if not transaction_type or transaction_type == 'payment':
        queries_to_union.append(payments_query)
    if not transaction_type or transaction_type == 'income':
        queries_to_union.append(incomes_query)
    if not transaction_type or transaction_type == 'expense':
        queries_to_union.append(expenses_query)

    # Union aller Queries
    if queries_to_union:
        combined_query = union_all(*queries_to_union)
        transactions = db.execute(combined_query).fetchall()
    else:
        transactions = []

    # In Liste von Dictionaries umwandeln für einfachere Verarbeitung
    transactions_list = []
    for t in transactions:
        transaction_dict = {
            'id': t.id,
            'type': t.type,
            'amount': t.amount,
            'transaction_date': t.transaction_date,
            'method': t.method,
            'reference': t.reference,
            'description': t.description,
            'participant_name': f"{t.participant_first_name} {t.participant_last_name}" if t.participant_first_name else None,
            'family_name': t.family_name,
            'created_at': t.created_at
        }
        transactions_list.append(transaction_dict)

    # Suchfilter (auf Liste anwenden)
    if search:
        search_lower = search.lower()
        transactions_list = [
            t for t in transactions_list
            if (t['reference'] and search_lower in t['reference'].lower()) or
               (t['description'] and search_lower in t['description'].lower()) or
               (t['participant_name'] and search_lower in t['participant_name'].lower()) or
               (t['family_name'] and search_lower in t['family_name'].lower())
        ]

    # Nach Datum sortieren (neueste zuerst)
    transactions_list.sort(key=lambda x: x['transaction_date'], reverse=True)

    # Summen berechnen
    total_income = sum(t['amount'] for t in transactions_list if t['amount'] > 0)
    total_expenses = sum(abs(t['amount']) for t in transactions_list if t['amount'] < 0)
    net_total = total_income - total_expenses

    # Laufenden Saldo berechnen (chronologisch)
    transactions_with_balance = []
    running_balance = 0.0
    for t in reversed(transactions_list):  # Chronologisch
        running_balance += t['amount']
        t['running_balance'] = running_balance
        transactions_with_balance.append(t)

    transactions_with_balance.reverse()  # Wieder zurück zu neueste zuerst

    logger.info(f"Loaded {len(transactions_with_balance)} transactions")

    return templates.TemplateResponse(
        "cash_status/overview.html",
        {
            "request": request,
            "title": "Kassenstand - Historie",
            "show_history": True,
            "transactions": transactions_with_balance,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_total": net_total,
            # Filter-Werte
            "filter_date_from": date_from,
            "filter_date_to": date_to,
            "filter_type": transaction_type,
            "filter_min_amount": min_amount,
            "filter_max_amount": max_amount,
            "filter_search": search,
        }
    )


@router.get("/history/export/excel")
async def export_history_excel(
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
):
    """Exportiert die Transaktionshistorie als Excel-Datei"""
    logger.info(f"Exporting transaction history to Excel for event {event_id}")

    # Transaktionen mit denselben Filtern wie in der Historie laden
    # (Wiederverwendung der Logik aus transaction_history)

    # === Queries aufbauen ===
    payments_query = db.query(
        Payment.id.label('id'),
        literal('Zahlungseingang').label('type'),
        Payment.amount.label('amount'),
        Payment.payment_date.label('transaction_date'),
        Payment.payment_method.label('method'),
        Payment.reference.label('reference'),
        Payment.notes.label('description'),
        Participant.first_name.label('participant_first_name'),
        Participant.last_name.label('participant_last_name'),
        Family.name.label('family_name')
    ).outerjoin(
        Participant, Payment.participant_id == Participant.id
    ).outerjoin(
        Family, Payment.family_id == Family.id
    ).filter(
        Payment.event_id == event_id
    )

    incomes_query = db.query(
        Income.id.label('id'),
        literal('Sonstige Einnahme').label('type'),
        Income.amount.label('amount'),
        Income.date.label('transaction_date'),
        literal(None).label('method'),
        Income.name.label('reference'),
        Income.description.label('description'),
        literal(None).label('participant_first_name'),
        literal(None).label('participant_last_name'),
        literal(None).label('family_name')
    ).filter(
        Income.event_id == event_id
    )

    expenses_query = db.query(
        Expense.id.label('id'),
        literal('Ausgabe').label('type'),
        (Expense.amount * -1).label('amount'),
        Expense.expense_date.label('transaction_date'),
        Expense.category.label('method'),
        Expense.title.label('reference'),
        Expense.description.label('description'),
        literal(None).label('participant_first_name'),
        literal(None).label('participant_last_name'),
        literal(None).label('family_name')
    ).filter(
        Expense.event_id == event_id
    )

    # Filter anwenden
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
            payments_query = payments_query.filter(Payment.payment_date >= date_from_obj)
            incomes_query = incomes_query.filter(Income.date >= date_from_obj)
            expenses_query = expenses_query.filter(Expense.expense_date >= date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
            payments_query = payments_query.filter(Payment.payment_date <= date_to_obj)
            incomes_query = incomes_query.filter(Income.date <= date_to_obj)
            expenses_query = expenses_query.filter(Expense.expense_date <= date_to_obj)
        except ValueError:
            pass

    if min_amount is not None:
        payments_query = payments_query.filter(Payment.amount >= min_amount)
        incomes_query = incomes_query.filter(Income.amount >= min_amount)
        expenses_query = expenses_query.filter(Expense.amount >= min_amount)

    if max_amount is not None:
        payments_query = payments_query.filter(Payment.amount <= max_amount)
        incomes_query = incomes_query.filter(Income.amount <= max_amount)
        expenses_query = expenses_query.filter(Expense.amount <= max_amount)

    # Union
    queries_to_union = []
    if not transaction_type or transaction_type == 'payment':
        queries_to_union.append(payments_query)
    if not transaction_type or transaction_type == 'income':
        queries_to_union.append(incomes_query)
    if not transaction_type or transaction_type == 'expense':
        queries_to_union.append(expenses_query)

    if queries_to_union:
        combined_query = union_all(*queries_to_union)
        transactions = db.execute(combined_query).fetchall()
    else:
        transactions = []

    # In Liste umwandeln
    transactions_list = []
    for t in transactions:
        transaction_dict = {
            'type': t.type,
            'transaction_date': t.transaction_date,
            'amount': t.amount,
            'method': t.method,
            'reference': t.reference,
            'description': t.description,
            'participant_name': f"{t.participant_first_name} {t.participant_last_name}" if t.participant_first_name else None,
            'family_name': t.family_name,
        }
        transactions_list.append(transaction_dict)

    # Suchfilter
    if search:
        search_lower = search.lower()
        transactions_list = [
            t for t in transactions_list
            if (t['reference'] and search_lower in t['reference'].lower()) or
               (t['description'] and search_lower in t['description'].lower()) or
               (t['participant_name'] and search_lower in t['participant_name'].lower()) or
               (t['family_name'] and search_lower in t['family_name'].lower())
        ]

    # Chronologisch sortieren (älteste zuerst für Excel)
    transactions_list.sort(key=lambda x: x['transaction_date'])

    # Excel erstellen
    wb = Workbook()
    ws = wb.active
    ws.title = "Transaktionshistorie"

    # Header
    headers = [
        "Datum", "Typ", "Betrag (€)", "Einnahme (€)", "Ausgabe (€)",
        "Saldo (€)", "Kategorie/Methode", "Referenz", "Beschreibung",
        "Teilnehmer", "Familie"
    ]

    # Header-Formatierung
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    # Spaltenbreiten
    column_widths = [12, 18, 12, 12, 12, 12, 15, 25, 30, 20, 20]
    for col_num, width in enumerate(column_widths, 1):
        ws.column_dimensions[ws.cell(row=1, column=col_num).column_letter].width = width

    # Daten schreiben
    running_balance = 0.0
    row_num = 2

    for transaction in transactions_list:
        running_balance += transaction['amount']

        ws.cell(row=row_num, column=1, value=transaction['transaction_date'].strftime('%d.%m.%Y'))
        ws.cell(row=row_num, column=2, value=transaction['type'])
        ws.cell(row=row_num, column=3, value=transaction['amount'])
        ws.cell(row=row_num, column=4, value=transaction['amount'] if transaction['amount'] > 0 else 0)
        ws.cell(row=row_num, column=5, value=abs(transaction['amount']) if transaction['amount'] < 0 else 0)
        ws.cell(row=row_num, column=6, value=running_balance)
        ws.cell(row=row_num, column=7, value=transaction['method'] or '')
        ws.cell(row=row_num, column=8, value=transaction['reference'] or '')
        ws.cell(row=row_num, column=9, value=transaction['description'] or '')
        ws.cell(row=row_num, column=10, value=transaction['participant_name'] or '')
        ws.cell(row=row_num, column=11, value=transaction['family_name'] or '')

        # Farbe für Einnahmen/Ausgaben
        if transaction['amount'] > 0:
            ws.cell(row=row_num, column=3).font = Font(color="00B050")  # Grün
        else:
            ws.cell(row=row_num, column=3).font = Font(color="C00000")  # Rot

        row_num += 1

    # Summenzeile
    row_num += 1
    summary_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    summary_font = Font(bold=True)

    ws.cell(row=row_num, column=1, value="GESAMT").font = summary_font
    ws.cell(row=row_num, column=1).fill = summary_fill

    total_income = sum(t['amount'] for t in transactions_list if t['amount'] > 0)
    total_expenses = sum(abs(t['amount']) for t in transactions_list if t['amount'] < 0)

    ws.cell(row=row_num, column=4, value=total_income).font = summary_font
    ws.cell(row=row_num, column=4).fill = summary_fill
    ws.cell(row=row_num, column=5, value=total_expenses).font = summary_font
    ws.cell(row=row_num, column=5).fill = summary_fill
    ws.cell(row=row_num, column=6, value=running_balance).font = summary_font
    ws.cell(row=row_num, column=6).fill = summary_fill

    # Datei als BytesIO zurückgeben
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"Transaktionshistorie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    logger.info(f"Excel export completed: {len(transactions_list)} transactions")

    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/history/export/csv")
async def export_history_csv(
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
):
    """Exportiert die Transaktionshistorie als CSV-Datei"""
    logger.info(f"Exporting transaction history to CSV for event {event_id}")

    # Queries aufbauen (wie bei Excel)
    payments_query = db.query(
        literal('Zahlungseingang').label('type'),
        Payment.payment_date.label('transaction_date'),
        Payment.amount.label('amount'),
        Payment.payment_method.label('method'),
        Payment.reference.label('reference'),
        Payment.notes.label('description'),
        Participant.first_name.label('participant_first_name'),
        Participant.last_name.label('participant_last_name'),
        Family.name.label('family_name')
    ).outerjoin(
        Participant, Payment.participant_id == Participant.id
    ).outerjoin(
        Family, Payment.family_id == Family.id
    ).filter(
        Payment.event_id == event_id
    )

    incomes_query = db.query(
        literal('Sonstige Einnahme').label('type'),
        Income.date.label('transaction_date'),
        Income.amount.label('amount'),
        literal(None).label('method'),
        Income.name.label('reference'),
        Income.description.label('description'),
        literal(None).label('participant_first_name'),
        literal(None).label('participant_last_name'),
        literal(None).label('family_name')
    ).filter(
        Income.event_id == event_id
    )

    expenses_query = db.query(
        literal('Ausgabe').label('type'),
        Expense.expense_date.label('transaction_date'),
        (Expense.amount * -1).label('amount'),
        Expense.category.label('method'),
        Expense.title.label('reference'),
        Expense.description.label('description'),
        literal(None).label('participant_first_name'),
        literal(None).label('participant_last_name'),
        literal(None).label('family_name')
    ).filter(
        Expense.event_id == event_id
    )

    # Filter anwenden
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
            payments_query = payments_query.filter(Payment.payment_date >= date_from_obj)
            incomes_query = incomes_query.filter(Income.date >= date_from_obj)
            expenses_query = expenses_query.filter(Expense.expense_date >= date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
            payments_query = payments_query.filter(Payment.payment_date <= date_to_obj)
            incomes_query = incomes_query.filter(Income.date <= date_to_obj)
            expenses_query = expenses_query.filter(Expense.expense_date <= date_to_obj)
        except ValueError:
            pass

    if min_amount is not None:
        payments_query = payments_query.filter(Payment.amount >= min_amount)
        incomes_query = incomes_query.filter(Income.amount >= min_amount)
        expenses_query = expenses_query.filter(Expense.amount >= min_amount)

    if max_amount is not None:
        payments_query = payments_query.filter(Payment.amount <= max_amount)
        incomes_query = incomes_query.filter(Income.amount <= max_amount)
        expenses_query = expenses_query.filter(Expense.amount <= max_amount)

    # Union
    queries_to_union = []
    if not transaction_type or transaction_type == 'payment':
        queries_to_union.append(payments_query)
    if not transaction_type or transaction_type == 'income':
        queries_to_union.append(incomes_query)
    if not transaction_type or transaction_type == 'expense':
        queries_to_union.append(expenses_query)

    if queries_to_union:
        combined_query = union_all(*queries_to_union)
        transactions = db.execute(combined_query).fetchall()
    else:
        transactions = []

    # In Liste umwandeln
    transactions_list = []
    for t in transactions:
        transaction_dict = {
            'type': t.type,
            'transaction_date': t.transaction_date,
            'amount': t.amount,
            'method': t.method or '',
            'reference': t.reference or '',
            'description': t.description or '',
            'participant_name': f"{t.participant_first_name} {t.participant_last_name}" if t.participant_first_name else '',
            'family_name': t.family_name or '',
        }
        transactions_list.append(transaction_dict)

    # Suchfilter
    if search:
        search_lower = search.lower()
        transactions_list = [
            t for t in transactions_list
            if (search_lower in t['reference'].lower()) or
               (search_lower in t['description'].lower()) or
               (search_lower in t['participant_name'].lower()) or
               (search_lower in t['family_name'].lower())
        ]

    # Chronologisch sortieren
    transactions_list.sort(key=lambda x: x['transaction_date'])

    # CSV erstellen
    output = StringIO()
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)

    # Header
    writer.writerow([
        "Datum", "Typ", "Betrag", "Einnahme", "Ausgabe", "Saldo",
        "Kategorie/Methode", "Referenz", "Beschreibung", "Teilnehmer", "Familie"
    ])

    # Daten
    running_balance = 0.0
    for transaction in transactions_list:
        running_balance += transaction['amount']

        writer.writerow([
            transaction['transaction_date'].strftime('%d.%m.%Y'),
            transaction['type'],
            f"{transaction['amount']:.2f}",
            f"{transaction['amount']:.2f}" if transaction['amount'] > 0 else "0.00",
            f"{abs(transaction['amount']):.2f}" if transaction['amount'] < 0 else "0.00",
            f"{running_balance:.2f}",
            transaction['method'],
            transaction['reference'],
            transaction['description'],
            transaction['participant_name'],
            transaction['family_name']
        ])

    filename = f"Transaktionshistorie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    logger.info(f"CSV export completed: {len(transactions_list)} transactions")

    return Response(
        content=output.getvalue().encode('utf-8-sig'),  # BOM für Excel
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
