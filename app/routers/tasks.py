"""Tasks Router - Offene Aufgaben"""
import logging
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, date, timedelta

from app.database import get_db
from app.models import Participant, Payment, Expense, Event, Task, Income, Role
from app.dependencies import get_current_event_id
from app.utils.flash import flash
from app.utils.datetime_utils import utcnow
from app.templates_config import templates

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_completed_tasks(db: Session, event_id: int) -> set:
    """
    Holt alle erledigten Tasks für ein Event als Set.

    Args:
        db: Datenbank-Session
        event_id: Event-ID für die Tasks

    Returns:
        Set von (task_type, reference_id) Tupeln für schnelle Lookups
    """
    completed = db.query(Task).filter(
        Task.event_id == event_id,
        Task.is_completed == True
    ).all()

    # Erstelle ein Set von (task_type, reference_id) Tupeln für schnelle Lookups
    completed_set = {(task.task_type, task.reference_id) for task in completed}
    return completed_set


def is_task_completed(completed_tasks: set, task_type: str, reference_id: int) -> bool:
    """
    Prüft, ob eine Aufgabe bereits erledigt wurde.

    Args:
        completed_tasks: Set von (task_type, reference_id) Tupeln
        task_type: Typ der Aufgabe (z.B. "bildung_teilhabe")
        reference_id: ID der referenzierten Entität

    Returns:
        True wenn die Aufgabe erledigt ist, sonst False
    """
    return (task_type, reference_id) in completed_tasks


@router.get("/", response_class=HTMLResponse)
async def list_tasks(request: Request, db: Session = Depends(get_db), event_id: int = Depends(get_current_event_id)):
    """Liste aller offenen Aufgaben"""
    logger.info(f"Loading tasks list for event {event_id}")

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
        "family_subsidy_mismatch": [],
        "role_count_exceeded": [],
        "birthday_gifts": [],
        "kitchen_team_gift": [],
        "familienfreizeit_non_member_check": []
    }

    # 1. Bildung & Teilhabe IDs vorhanden (müssen beantragt werden)
    participants_with_but = db.query(Participant).filter(
        Participant.event_id == event_id,
        Participant.bildung_teilhabe_id.isnot(None),
        Participant.bildung_teilhabe_id != "",  # Leere Strings ausschließen
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
        final_price = float(participant.manual_price_override if participant.manual_price_override is not None else participant.calculated_price)
        total_paid = float(participant.total_paid)
        outstanding = final_price - total_paid

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
    # Hole das Regelwerk für diesen Event
    from app.models import Ruleset
    from app.services.price_calculator import PriceCalculator

    ruleset = db.query(Ruleset).filter(
        Ruleset.event_id == event_id,
        Ruleset.is_active == True
    ).first()

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
        # Konvertiere zu float um Decimal/float Typ-Konflikte zu vermeiden
        total_subsidy = float(role_income.total_income or 0)

        # Berechne erwartete Rabatte für alle Teilnehmer mit dieser Rolle
        participants_with_role = db.query(Participant).filter(
            Participant.event_id == event_id,
            Participant.role_id == role_id,
            Participant.is_active == True
        ).all()

        expected_discounts = 0.0
        if ruleset and ruleset.age_groups:
            role_discounts = ruleset.role_discounts or {}
            age_groups = ruleset.age_groups or []

            for participant in participants_with_role:
                # Berechne die tatsächlich gewährten Rollenrabatte (egal ob calculated oder manual_price_override)
                if participant.age_at_event is not None:
                    # Berechne Basispreis aus Altersgruppen
                    base_price = PriceCalculator._get_base_price_by_age(participant.age_at_event, age_groups)

                    # Hole Rollenrabatt-Prozentsatz
                    role_name_lower = participant.role.name.lower() if participant.role else ""
                    if role_name_lower in role_discounts:
                        discount_percent = role_discounts[role_name_lower].get("discount_percent", 0)
                        role_discount_amount = base_price * (discount_percent / 100)
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

    # 10b. Kinderzuschuss-Differenz (Familienrabatte vs. Zuschüsse)
    # Prüfe, ob es einen "Kinderzuschuss" Income-Eintrag gibt
    family_subsidy_income = db.query(func.sum(Income.amount)).filter(
        Income.event_id == event_id,
        Income.description.like('%Kinderzuschuss%')
    ).scalar()

    if family_subsidy_income and float(family_subsidy_income) > 0:
        total_family_subsidy = float(family_subsidy_income)

        # Berechne erwartete Familienrabatte für Kinder ohne manuelle Preisüberschreibung
        children_participants = db.query(Participant).filter(
            Participant.event_id == event_id,
            Participant.is_active == True,
            Participant.manual_price_override.is_(None)  # Nur ohne manuelle Preisüberschreibung
        ).all()

        expected_family_discounts = 0.0
        if ruleset and ruleset.family_discount:
            from app.models import Family
            from app.services.price_calculator import PriceCalculator

            family_discount_config = ruleset.family_discount or {}
            age_groups = ruleset.age_groups or []

            # Gruppiere Kinder nach Familie
            families_dict = {}
            for participant in children_participants:
                # Nur Kinder unter 18
                if participant.age_at_event < 18 and participant.family_id:
                    if participant.family_id not in families_dict:
                        families_dict[participant.family_id] = []
                    families_dict[participant.family_id].append(participant)

            # Berechne Familienrabatte
            for family_id, family_participants in families_dict.items():
                # Sortiere nach Geburtsdatum (ältestes zuerst)
                family_participants.sort(key=lambda p: p.birth_date)

                for idx, participant in enumerate(family_participants):
                    child_position = idx + 1  # 1 = ältestes Kind, 2 = zweites, etc.

                    # Berechne Basispreis
                    base_price = PriceCalculator._get_base_price_by_age(participant.age_at_event, age_groups)

                    # Ermittle Familienrabatt-Prozentsatz
                    family_discount_percent = PriceCalculator._get_family_discount(
                        participant.age_at_event,
                        child_position,
                        family_discount_config
                    )

                    if family_discount_percent > 0:
                        family_discount_amount = base_price * (family_discount_percent / 100)
                        expected_family_discounts += family_discount_amount

        # Berechne Differenz
        difference = total_family_subsidy - expected_family_discounts

        # Wenn Differenz signifikant (mehr als 1€), erstelle Task
        if abs(difference) > 1.0:
            if not is_task_completed(completed_tasks, "family_subsidy_mismatch", event_id):
                status = "zu viel" if difference > 0 else "zu wenig"
                tasks["family_subsidy_mismatch"].append({
                    "id": event_id,
                    "title": "Kinderzuschuss-Differenz (Familienrabatte)",
                    "description": f"Zuschuss: {total_family_subsidy:.2f}€ | Familienrabatte: {expected_family_discounts:.2f}€ | Differenz: {abs(difference):.2f}€ ({status})",
                    "link": f"/incomes",
                    "task_type": "family_subsidy_mismatch",
                    "difference": difference,
                    "total_subsidy": total_family_subsidy,
                    "expected_discounts": expected_family_discounts
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

    # 12. Geschenke für Geburtstagskinder während der Freizeit
    if event and event.start_date and event.end_date:
        # Finde alle Teilnehmer, die während der Freizeit Geburtstag haben
        all_participants = db.query(Participant).filter(
            Participant.event_id == event_id,
            Participant.is_active == True,
            Participant.birth_date.isnot(None)
        ).all()

        birthday_children = []
        for participant in all_participants:
            # Prüfe, ob der Geburtstag (Tag und Monat) im Event-Zeitraum liegt
            birth_month = participant.birth_date.month
            birth_day = participant.birth_date.day

            # Erstelle Datumsobjekte für Vergleich (mit Event-Jahr)
            try:
                birthday_this_year = date(event.start_date.year, birth_month, birth_day)

                # Prüfe, ob Geburtstag im Event-Zeitraum liegt
                if event.start_date <= birthday_this_year <= event.end_date:
                    birthday_children.append({
                        "name": participant.full_name,
                        "date": birthday_this_year,
                        "age": participant.age_at_event + 1  # Alter nach Geburtstag
                    })
            except ValueError:
                # Ungültiges Datum (z.B. 29. Februar in Nicht-Schaltjahr)
                continue

        if birthday_children and not is_task_completed(completed_tasks, "birthday_gifts", event_id):
            # Sortiere nach Geburtsdatum
            birthday_children.sort(key=lambda x: x["date"])

            # Erstelle Liste der Namen
            names_list = ", ".join([f"{child['name']} ({child['date'].strftime('%d.%m.')})" for child in birthday_children])

            tasks["birthday_gifts"].append({
                "id": event_id,
                "title": f"Geschenke für {len(birthday_children)} Geburtstagskind(er)",
                "description": f"Geburtstagskinder während der Freizeit: {names_list}",
                "link": f"/participants",
                "task_type": "birthday_gifts",
                "count": len(birthday_children)
            })

    # 13. Geschenk für das Küchenteam
    # Finde Rolle "Küche" (verschiedene mögliche Namen)
    kitchen_role_names = ["kueche", "küche", "kitchen"]
    kitchen_participants = db.query(Participant).join(
        Role, Participant.role_id == Role.id
    ).filter(
        Participant.event_id == event_id,
        Participant.is_active == True,
        Role.name.in_(kitchen_role_names)
    ).all()

    if kitchen_participants and not is_task_completed(completed_tasks, "kitchen_team_gift", event_id):
        # Erstelle Liste der Namen
        names_list = ", ".join([p.full_name for p in kitchen_participants])

        tasks["kitchen_team_gift"].append({
            "id": event_id,
            "title": f"Geschenk für das Küchenteam ({len(kitchen_participants)} Personen)",
            "description": f"Küchenteam-Mitglieder: {names_list}",
            "link": f"/participants?role_id={kitchen_participants[0].role_id if kitchen_participants else ''}",
            "task_type": "kitchen_team_gift",
            "count": len(kitchen_participants)
        })

    # 14. Familienfreizeit: Prüfung ob Kinder von Nicht-Gemeindemitgliedern mitfahren
    if event and event.event_type and event.event_type.lower() == "familienfreizeit":
        if not is_task_completed(completed_tasks, "familienfreizeit_non_member_check", event_id):
            tasks["familienfreizeit_non_member_check"].append({
                "id": event_id,
                "title": "Kinder von Nicht-Gemeindemitgliedern prüfen",
                "description": "Prüfen ob Kinder von nicht-Gemeindemitgliedern mitfahren. Zuschüsse werden nur für Gemeindemitglieder gewährt.",
                "link": f"/participants",
                "task_type": "familienfreizeit_non_member_check"
            })

    # Zähle Gesamtaufgaben
    total_tasks = sum(len(task_list) for task_list in tasks.values())
    logger.info(f"Found {total_tasks} open tasks for event {event_id}")

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
    logger.info(f"Marking task as completed: type={task_type}, reference_id={reference_id}, event_id={event_id}")

    # Prüfe, ob Task bereits existiert
    existing_task = db.query(Task).filter(
        Task.event_id == event_id,
        Task.task_type == task_type,
        Task.reference_id == reference_id
    ).first()

    if existing_task:
        # Aktualisiere bestehenden Task
        existing_task.is_completed = True
        existing_task.completed_at = utcnow()
        if note:
            existing_task.completion_note = note
        logger.debug(f"Updated existing task {existing_task.id}")
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
        logger.debug(f"Created new task for type={task_type}, reference_id={reference_id}")

    # Spezielle Behandlung für expense_reimbursement
    if task_type == "expense_reimbursement":
        expense = db.query(Expense).filter(Expense.id == reference_id).first()
        if expense:
            expense.is_settled = True
            logger.info(f"Marked expense {expense.id} as settled")

    # Spezielle Behandlung für outstanding_payment
    # Wenn Zahlungseingang als erledigt markiert wird, automatisch Payment erstellen
    if task_type == "outstanding_payment":
        participant = db.query(Participant).filter(Participant.id == reference_id).first()
        if participant:
            # Berechne ausstehenden Betrag
            final_price = float(participant.final_price)
            total_paid = float(db.query(func.sum(Payment.amount)).filter(
                Payment.participant_id == participant.id
            ).scalar() or 0)
            outstanding = final_price - total_paid

            if outstanding > 0.01:  # Nur wenn mehr als 1 Cent ausstehend
                # Erstelle automatisch einen Zahlungseingang
                new_payment = Payment(
                    amount=outstanding,
                    payment_date=date.today(),
                    payment_method="Automatisch",
                    reference=f"Aufgabe erledigt: {participant.full_name}",
                    notes=note if note else "Zahlungseingang automatisch aus erledigter Aufgabe erstellt",
                    event_id=event_id,
                    participant_id=participant.id
                )
                db.add(new_payment)
                logger.info(f"Automatically created payment of {outstanding}€ for participant {participant.id}")

    db.commit()
    flash(request, "Aufgabe wurde als erledigt markiert", "success")
    logger.info(f"Task completed successfully: type={task_type}, reference_id={reference_id}")

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
    logger.info(f"Uncompleting task: type={task_type}, reference_id={reference_id}, event_id={event_id}")

    # Finde und lösche den Task
    task = db.query(Task).filter(
        Task.event_id == event_id,
        Task.task_type == task_type,
        Task.reference_id == reference_id
    ).first()

    if task:
        db.delete(task)
        logger.debug(f"Deleted task {task.id}")

        # Spezielle Behandlung für expense_reimbursement
        if task_type == "expense_reimbursement":
            expense = db.query(Expense).filter(Expense.id == reference_id).first()
            if expense:
                expense.is_settled = False
                logger.info(f"Marked expense {expense.id} as not settled")

        db.commit()
        flash(request, "Aufgabe wurde wieder als offen markiert", "info")
        logger.info(f"Task uncompleted successfully: type={task_type}, reference_id={reference_id}")
    else:
        logger.warning(f"Task not found for uncomplete: type={task_type}, reference_id={reference_id}")

    return RedirectResponse(url="/tasks", status_code=303)
