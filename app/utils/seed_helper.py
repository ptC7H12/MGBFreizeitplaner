"""Helper für das Erstellen von Demo-Daten beim ersten Start"""
from datetime import date
from pathlib import Path
from sqlalchemy.orm import Session

from app.models import Event, Family, Participant, Role, Ruleset, Payment, Expense, Income, Setting
from app.services.ruleset_parser import RulesetParser


def create_demo_data(db: Session):
    """
    Erstellt Demo-Daten beim ersten Start der Anwendung
    Diese Funktion wird nur ausgeführt, wenn keine Events vorhanden sind
    """
    # 1. Event erstellen
    event = Event(
        name="Sommerfreizeit 2024",
        description="Kinderfreizeit im Sommer 2024",
        event_type="kinder",
        start_date=date(2024, 7, 15),
        end_date=date(2024, 7, 28),
        location="Freizeitheim Waldblick",
        code=Event.generate_code(),
        is_active=True
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # 2. Einstellungen erstellen
    setting = Setting(
        event_id=event.id,
        organization_name="Jugendverband Beispielstadt e.V.",
        organization_address="Musterstraße 123\n12345 Beispielstadt\nDeutschland",
        bank_account_holder="Jugendverband Beispielstadt e.V.",
        bank_iban="DE89370400440532013000",
        bank_bic="COBADEFFXXX",
        invoice_subject_prefix="Teilnahmegebühr",
        invoice_footer_text="Vielen Dank für Ihre Teilnahme! Bei Fragen erreichen Sie uns unter info@jugendverband-beispielstadt.de"
    )
    db.add(setting)
    db.commit()

    # 3. Rollen erstellen
    roles_data = [
        {"name": "kind", "display_name": "Kind", "color": "#3B82F6"},
        {"name": "jugendlicher", "display_name": "Jugendlicher", "color": "#8B5CF6"},
        {"name": "betreuer", "display_name": "Betreuer", "color": "#10B981"},
        {"name": "kueche", "display_name": "Küchenpersonal", "color": "#F59E0B"},
        {"name": "leitung", "display_name": "Freizeitleitung", "color": "#EF4444"},
    ]

    roles = {}
    for role_data in roles_data:
        role = Role(
            name=role_data["name"],
            display_name=role_data["display_name"],
            color=role_data["color"],
            event_id=event.id
        )
        db.add(role)
        roles[role_data["name"]] = role
    db.commit()

    # 4. Regelwerk importieren
    yaml_file = Path("rulesets/examples/kinder_2024.yaml")
    if yaml_file.exists():
        try:
            parser = RulesetParser()
            data = parser.parse_yaml_file(yaml_file)

            ruleset = Ruleset(
                name=data["name"],
                ruleset_type=data["type"],
                valid_from=date.fromisoformat(data["valid_from"]),
                valid_until=date.fromisoformat(data["valid_until"]),
                age_groups=data["age_groups"],
                role_discounts=data.get("role_discounts"),
                family_discount=data.get("family_discount"),
                source_file=str(yaml_file),
                event_id=event.id,
                is_active=True
            )
            db.add(ruleset)
            db.commit()
        except Exception:
            # Falls Regelwerk-Import fehlschlägt, trotzdem fortfahren
            pass

    # 5. Beispiel-Familien und Teilnehmer erstellen
    # Familie Müller
    family_mueller = Family(
        name="Müller",
        contact_person="Anna Müller",
        email="anna.mueller@example.com",
        phone="0123-456789",
        event_id=event.id
    )
    db.add(family_mueller)
    db.commit()

    participants_mueller = [
        Participant(
            first_name="Max",
            last_name="Müller",
            birth_date=date(2012, 5, 15),
            role=roles["kind"],
            family=family_mueller,
            event=event,
            calculated_price=150.00
        ),
        Participant(
            first_name="Lisa",
            last_name="Müller",
            birth_date=date(2014, 8, 22),
            role=roles["kind"],
            family=family_mueller,
            event=event,
            calculated_price=140.00
        )
    ]
    for p in participants_mueller:
        db.add(p)
    db.commit()

    # Familie Schmidt
    family_schmidt = Family(
        name="Schmidt",
        contact_person="Peter Schmidt",
        email="peter.schmidt@example.com",
        phone="0987-654321",
        event_id=event.id
    )
    db.add(family_schmidt)
    db.commit()

    participant_schmidt = Participant(
        first_name="Tom",
        last_name="Schmidt",
        birth_date=date(2011, 3, 10),
        role=roles["kind"],
        family=family_schmidt,
        event=event,
        calculated_price=150.00
    )
    db.add(participant_schmidt)
    db.commit()

    # Einzelperson - Betreuer
    betreuer = Participant(
        first_name="Sarah",
        last_name="Meyer",
        birth_date=date(1995, 11, 5),
        email="sarah.meyer@example.com",
        phone="0555-123456",
        role=roles["betreuer"],
        event=event,
        calculated_price=75.00
    )
    db.add(betreuer)
    db.commit()

    # 6. Beispiel-Zahlungen
    payments = [
        Payment(
            amount=200.00,
            payment_date=date(2024, 5, 15),
            payment_method="Überweisung",
            reference="Anzahlung Sommerfreizeit",
            family_id=family_mueller.id,
            event_id=event.id
        ),
        Payment(
            amount=150.00,
            payment_date=date(2024, 5, 20),
            payment_method="Überweisung",
            reference="Freizeit Tom Schmidt",
            family_id=family_schmidt.id,
            event_id=event.id
        ),
        Payment(
            amount=75.00,
            payment_date=date(2024, 6, 5),
            payment_method="Überweisung",
            reference=f"Teilnahmegebühr {betreuer.full_name}",
            participant_id=betreuer.id,
            event_id=event.id
        )
    ]
    for payment in payments:
        db.add(payment)
    db.commit()

    # 7. Beispiel-Ausgaben
    expenses = [
        Expense(
            title="Verpflegung Supermarkt",
            description="Lebensmitteleinkauf für die erste Woche",
            amount=450.00,
            expense_date=date(2024, 7, 10),
            category="Verpflegung",
            paid_by="Anna Müller",
            is_settled=True,
            event_id=event.id
        ),
        Expense(
            title="Bastelmaterial",
            description="Bastelutensilien und Kreativmaterial",
            amount=85.50,
            expense_date=date(2024, 7, 5),
            category="Material",
            paid_by="Peter Schmidt",
            is_settled=False,
            event_id=event.id
        )
    ]
    for expense in expenses:
        db.add(expense)
    db.commit()

    # 8. Beispiel-Einnahmen
    incomes = [
        Income(
            title="Zuschuss Jugendamt",
            description="Förderung für Kinder- und Jugendarbeit",
            amount=500.00,
            date=date(2024, 6, 1),
            category="Zuschuss",
            source="Jugendamt Stadt Beispielstadt",
            role_id=roles["kind"].id,
            event_id=event.id
        ),
        Income(
            title="Spende Förderverein",
            description="Spende des Fördervereins für Freizeitaktivitäten",
            amount=250.00,
            date=date(2024, 5, 15),
            category="Spende",
            source="Förderverein Jugendarbeit e.V.",
            event_id=event.id
        )
    ]
    for income in incomes:
        db.add(income)
    db.commit()
