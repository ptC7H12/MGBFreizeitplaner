"""Tasks Router - Offene Aufgaben"""
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, date, timedelta

from app.database import get_db
from app.models import Participant, Payment, Expense, Event, Task, Income, Role
from app.dependencies import get_current_event_id
from app.utils.flash import flash
from app.templates_config import templates

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_completed_tasks(db: Session, event_id: int) -> dict:
    """Holt alle erledigten Tasks für ein Event als Set"""
    completed = db.query(Task).filter(
        Task.event_id == event_id,
        Task.is_completed == True
    ).all()

    # Erstelle ein Set von (task_type, reference_id) Tupeln für schnelle Lookups
    completed_set = {(task.task_type, task.reference_id) for task in completed}
    return completed_set


def is_task_completed(completed_tasks: set, task_type: str, reference_id: int) -> bool:
    """Prüft, ob eine Aufgabe bereits erledigt wurde"""
    return (task_type, reference_id) in completed_tasks


@router.get("/", response_class=HTMLResponse)
async def list_tasks(request: Request, db: Session = Depends(get_db), event_id: int = Depends(get_current_event_id)):
    """Liste aller offenen Aufgaben"""

    # Hole Event-Details für Fälligkeitsdatum
    event = db.query(Event).filter(Event.id == event_id).first()

    # Hole bereits erledigte Tasks
    completed_tasks = get_completed_tasks(db, event_id)

    tasks = {
        "bildung_teilhabe": [],
        "expense_reimbursement": [],
        "outstanding_payments": [],
        "manual_price_override": [],
        "overdue_payments": [],
        "income_subsidy_mismatch": [],
        "role_count_exceeded": []
    }

    # 1. Bildung & Teilhabe IDs vorhanden (müssen beantragt werden)
    participants_with_but = db.query(Participant).filter(
        Participant.event_id == event_id,
        Participant.bildung_teilhabe_id.isnot(None),
        Participant.is_active == True
    ).all()

    for participant in participants_with_but:
        if not is_task_completed(completed_tasks, "bildung_teilhabe", participant.id):
            tasks["bildung_teilhabe"].append({
                "id": participant.id,
                "title": f"{participant.full_name}",
                "description": f"BuT-Nummer: {participant.bildung_teilhabe_id}",
                "link": f"/participants/{participant.id}",
                "task_type": "bildung_teilhabe"
            })

    # 2. Rückzahlung von Ausgaben (nicht erstattete Ausgaben)
    unreimbursed_expenses = db.query(Expense).filter(
        Expense.event_id == event_id,
        Expense.is_settled == False,
        Expense.paid_by.isnot(None)
    ).all()

    for expense in unreimbursed_expenses:
        if not is_task_completed(completed_tasks, "expense_reimbursement", expense.id):
            tasks["expense_reimbursement"].append({
                "id": expense.id,
                "title": f"{expense.title}",
                "description": f"{expense.amount:.2f}€ - Bezahlt von: {expense.paid_by}",
                "link": f"/expenses/{expense.id}",
                "task_type": "expense_reimbursement",
                "amount": expense.amount
            })

    # 3. Offene Zahlungseingänge (Teilnehmer mit ausstehenden Zahlungen)
    participants_with_payments = db.query(
        Participant.id,
        Participant.first_name,
        Participant.last_name,
        Participant.calculated_price,
        Participant.manual_price_override,
        func.coalesce(func.sum(Payment.amount), 0).label("total_paid")
    ).outerjoin(
        Payment, Payment.participant_id == Participant.id
    ).filter(
        Participant.event_id == event_id,
        Participant.is_active == True
    ).group_by(
        Participant.id
    ).all()

    for participant in participants_with_payments:
        final_price = participant.manual_price_override if participant.manual_price_override is not None else participant.calculated_price
        outstanding = final_price - participant.total_paid

        if outstanding > 0.01:  # Nur wenn mehr als 1 Cent ausstehend
            if not is_task_completed(completed_tasks, "outstanding_payment", participant.id):
                tasks["outstanding_payments"].append({
                    "id": participant.id,
                    "title": f"{participant.first_name} {participant.last_name}",
                    "description": f"Ausstehend: {outstanding:.2f}€ (von {final_price:.2f}€)",
                    "link": f"/participants/{participant.id}",
                    "task_type": "outstanding_payment",
                    "amount": outstanding
                })

    # 7. Manuelle Preisanpassungen prüfen
    participants_with_override = db.query(Participant).filter(
        Participant.event_id == event_id,
        Participant.manual_price_override.isnot(None),
        Participant.is_active == True
    ).all()

    for participant in participants_with_override:
        if not is_task_completed(completed_tasks, "manual_price_override", participant.id):
            tasks["manual_price_override"].append({
                "id": participant.id,
                "title": f"{participant.full_name}",
                "description": f"Manueller Preis: {participant.manual_price_override:.2f}€ (statt {participant.calculated_price:.2f}€)",
                "link": f"/participants/{participant.id}",
                "task_type": "manual_price_override"
            })

    # 9. Überfällige Zahlungen (Event hat bereits begonnen oder Frist überschritten)
    if event and event.start_date:
        # Annahme: Zahlungen sollten 14 Tage vor Event-Start eingegangen sein
        payment_deadline = event.start_date - timedelta(days=14)

        if date.today() >= payment_deadline:
            # Verwende die bereits gesammelten ausstehenden Zahlungen
            for task in tasks["outstanding_payments"]:
                if not is_task_completed(completed_tasks, "overdue_payment", task["id"]):
                    tasks["overdue_payments"].append({
                        **task,
                        "task_type": "overdue_payment",
                        "description": f"{task['description']} - ÜBERFÄLLIG!"
                    })

    # 10. Zuschuss-Validierung (prüfe ob Einnahmen mit Rabatten übereinstimmen)
    # Hole alle Einnahmen mit Rollenverknüpfung
    role_incomes = db.query(
        Role.id,
        Role.display_name,
        func.sum(Income.amount).label("total_income")
    ).join(
        Income, Income.role_id == Role.id
    ).filter(
        Role.event_id == event_id,
        Income.event_id == event_id
    ).group_by(Role.id).all()

    for role_income in role_incomes:
        role_id = role_income.id
        role_name = role_income.display_name
        total_subsidy = role_income.total_income

        # Berechne erwartete Rabatte für alle Teilnehmer mit dieser Rolle
        participants_with_role = db.query(Participant).filter(
            Participant.event_id == event_id,
            Participant.role_id == role_id,
            Participant.is_active == True
        ).all()

        expected_discounts = 0.0
        for participant in participants_with_role:
            if participant.calculated_price and participant.base_price:
                # Rabatt = Basispreis - berechneter Preis (enthält alle Rabatte)
                # Wir müssen den Rollenrabatt isolieren
                # Da alle Rabatte vom Basispreis berechnet werden, müssen wir anders vorgehen

                # Hole das Regelwerk für diesen Event
                from app.models import Ruleset
                ruleset = db.query(Ruleset).filter(
                    Ruleset.event_id == event_id,
                    Ruleset.is_active == True
                ).first()

                if ruleset and ruleset.data:
                    role_discounts = ruleset.data.get("role_discounts", {})
                    role_name_lower = participant.role.name.lower() if participant.role else ""

                    if role_name_lower in role_discounts:
                        discount_percent = role_discounts[role_name_lower].get("discount_percent", 0)
                        role_discount_amount = participant.base_price * (discount_percent / 100)
                        expected_discounts += role_discount_amount

        # Berechne Differenz
        difference = total_subsidy - expected_discounts

        # Wenn Differenz signifikant (mehr als 1€), erstelle Task
        if abs(difference) > 1.0:
            if not is_task_completed(completed_tasks, "income_subsidy_mismatch", role_id):
                status = "zu viel" if difference > 0 else "zu wenig"
                tasks["income_subsidy_mismatch"].append({
                    "id": role_id,
                    "title": f"Zuschuss-Differenz: {role_name}",
                    "description": f"Zuschuss: {total_subsidy:.2f}€ | Rabatte: {expected_discounts:.2f}€ | Differenz: {abs(difference):.2f}€ ({status})",
                    "link": f"/incomes",
                    "task_type": "income_subsidy_mismatch",
                    "difference": difference,
                    "total_subsidy": total_subsidy,
                    "expected_discounts": expected_discounts
                })

    # 11. Rollenüberschreitungen (zu viele Teilnehmer einer Rolle zugewiesen)
    from app.models import Ruleset
    ruleset = db.query(Ruleset).filter(
        Ruleset.event_id == event_id,
        Ruleset.is_active == True
    ).first()

    if ruleset and ruleset.role_discounts:
        # Durchlaufe alle Rollen mit max_count im Regelwerk
        for role_name_lower, role_config in ruleset.role_discounts.items():
            max_count = role_config.get("max_count")

            if max_count is not None:
                # Finde die entsprechende Rolle in der Datenbank
                role = db.query(Role).filter(
                    Role.event_id == event_id,
                    Role.name == role_name_lower
                ).first()

                if role:
                    # Zähle aktive Teilnehmer mit dieser Rolle
                    current_count = db.query(Participant).filter(
                        Participant.event_id == event_id,
                        Participant.role_id == role.id,
                        Participant.is_active == True
                    ).count()

                    # Wenn die Anzahl das Maximum überschreitet
                    if current_count > max_count:
                        if not is_task_completed(completed_tasks, "role_count_exceeded", role.id):
                            excess_count = current_count - max_count
                            tasks["role_count_exceeded"].append({
                                "id": role.id,
                                "title": f"Zu viele {role.display_name} zugewiesen",
                                "description": f"Aktuell: {current_count} | Maximum: {max_count} | Überschreitung: {excess_count}",
                                "link": f"/participants?role_id={role.id}",
                                "task_type": "role_count_exceeded",
                                "current_count": current_count,
                                "max_count": max_count,
                                "excess_count": excess_count
                            })

    # Zähle Gesamtaufgaben
    total_tasks = sum(len(task_list) for task_list in tasks.values())

    return templates.TemplateResponse(
        "tasks/list.html",
        {
            "request": request,
            "title": "Offene Aufgaben",
            "tasks": tasks,
            "total_tasks": total_tasks,
            "event": event
        }
    )


@router.post("/complete")
async def complete_task(
    request: Request,
    task_type: str = Form(...),
    reference_id: int = Form(...),
    note: str = Form(None),
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Markiert eine Aufgabe als erledigt"""

    # Prüfe, ob Task bereits existiert
    existing_task = db.query(Task).filter(
        Task.event_id == event_id,
        Task.task_type == task_type,
        Task.reference_id == reference_id
    ).first()

    if existing_task:
        # Aktualisiere bestehenden Task
        existing_task.is_completed = True
        existing_task.completed_at = datetime.utcnow()
        if note:
            existing_task.completion_note = note
    else:
        # Erstelle neuen Task
        new_task = Task(
            task_type=task_type,
            reference_id=reference_id,
            is_completed=True,
            completion_note=note,
            event_id=event_id
        )
        db.add(new_task)

    # Spezielle Behandlung für expense_reimbursement
    if task_type == "expense_reimbursement":
        expense = db.query(Expense).filter(Expense.id == reference_id).first()
        if expense:
            expense.is_settled = True

    db.commit()
    flash(request, "Aufgabe wurde als erledigt markiert", "success")

    return RedirectResponse(url="/tasks", status_code=303)


@router.post("/uncomplete")
async def uncomplete_task(
    request: Request,
    task_type: str = Form(...),
    reference_id: int = Form(...),
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Markiert eine Aufgabe als nicht erledigt (macht Completion rückgängig)"""

    # Finde und lösche den Task
    task = db.query(Task).filter(
        Task.event_id == event_id,
        Task.task_type == task_type,
        Task.reference_id == reference_id
    ).first()

    if task:
        db.delete(task)

        # Spezielle Behandlung für expense_reimbursement
        if task_type == "expense_reimbursement":
            expense = db.query(Expense).filter(Expense.id == reference_id).first()
            if expense:
                expense.is_settled = False

        db.commit()
        flash(request, "Aufgabe wurde wieder als offen markiert", "info")

    return RedirectResponse(url="/tasks", status_code=303)
