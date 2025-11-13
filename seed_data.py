"""Seed-Script für Beispieldaten"""
from datetime import date, datetime
from pathlib import Path

from app.database import SessionLocal, init_db
from app.models import Event, Family, Participant, Role, Ruleset, Payment, Expense
from app.services.ruleset_parser import RulesetParser
from app.services.role_manager import RoleManager


def seed_roles(db, event):
    """Erstellt Standard-Rollen für ein Event"""
    roles = [
        {"name": "kind", "display_name": "Kind", "color": "#3B82F6", "event_id": event.id},
        {"name": "jugendlicher", "display_name": "Jugendlicher", "color": "#8B5CF6", "event_id": event.id},
        {"name": "betreuer", "display_name": "Betreuer", "color": "#10B981", "event_id": event.id},
        {"name": "kueche", "display_name": "Küchenpersonal", "color": "#F59E0B", "event_id": event.id},
        {"name": "leitung", "display_name": "Freizeitleitung", "color": "#EF4444", "event_id": event.id},
    ]

    for role_data in roles:
        existing = db.query(Role).filter(
            Role.name == role_data["name"],
            Role.event_id == event.id
        ).first()
        if not existing:
            role = Role(**role_data)
            db.add(role)
            print(f"✓ Rolle erstellt: {role.display_name}")

    db.commit()


def seed_event(db):
    """Erstellt ein Beispiel-Event"""
    event = db.query(Event).filter(Event.name == "Sommerfreizeit 2024").first()
    if not event:
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
        print(f"✓ Event erstellt: {event.name} (Code: {event.code})")
    return event


def seed_ruleset(db, event):
    """Importiert ein Beispiel-Regelwerk"""
    ruleset = db.query(Ruleset).filter(Ruleset.name == "Kinderfreizeit 2024").first()
    if not ruleset:
        yaml_file = Path("rulesets/examples/kinder_2024.yaml")
        if yaml_file.exists():
            parser = RulesetParser()
            data = parser.parse_yaml_file(yaml_file)

            ruleset = Ruleset(
                name=data["name"],
                ruleset_type=data["type"],
                valid_from=datetime.strptime(data["valid_from"], "%Y-%m-%d").date(),
                valid_until=datetime.strptime(data["valid_until"], "%Y-%m-%d").date(),
                age_groups=data["age_groups"],
                role_discounts=data.get("role_discounts"),
                family_discount=data.get("family_discount"),
                source_file=str(yaml_file),
                event_id=event.id
            )
            db.add(ruleset)
            db.commit()
            print(f"✓ Regelwerk erstellt: {ruleset.name}")
        else:
            print("⚠ Regelwerk-Datei nicht gefunden")
    return ruleset


def seed_families_and_participants(db, event, ruleset):
    """Erstellt Beispiel-Familien und Teilnehmer"""
    # Rollen abrufen (event-spezifisch)
    role_kind = db.query(Role).filter(Role.name == "kind", Role.event_id == event.id).first()
    role_betreuer = db.query(Role).filter(Role.name == "betreuer", Role.event_id == event.id).first()
    role_kueche = db.query(Role).filter(Role.name == "kueche", Role.event_id == event.id).first()

    # Familie 1: Familie Müller
    family1 = db.query(Family).filter(Family.name == "Müller", Family.event_id == event.id).first()
    if not family1:
        family1 = Family(
            name="Müller",
            contact_person="Anna Müller",
            email="anna.mueller@example.com",
            phone="0123-456789",
            event_id=event.id
        )
        db.add(family1)
        db.commit()
        print(f"✓ Familie erstellt: Familie {family1.name}")

        # Kinder der Familie Müller
        participants = [
            {
                "first_name": "Max",
                "last_name": "Müller",
                "birth_date": date(2012, 5, 15),
                "role": role_kind,
                "family": family1,
                "calculated_price": 150.00
            },
            {
                "first_name": "Lisa",
                "last_name": "Müller",
                "birth_date": date(2014, 8, 22),
                "role": role_kind,
                "family": family1,
                "calculated_price": 140.00
            }
        ]

        for p_data in participants:
            p = Participant(
                first_name=p_data["first_name"],
                last_name=p_data["last_name"],
                birth_date=p_data["birth_date"],
                role=p_data["role"],
                family=p_data["family"],
                event=event,
                calculated_price=p_data["calculated_price"]
            )
            db.add(p)
            print(f"  ✓ Teilnehmer erstellt: {p.full_name}")

        db.commit()

    # Familie 2: Familie Schmidt
    family2 = db.query(Family).filter(Family.name == "Schmidt", Family.event_id == event.id).first()
    if not family2:
        family2 = Family(
            name="Schmidt",
            contact_person="Peter Schmidt",
            email="peter.schmidt@example.com",
            phone="0987-654321",
            event_id=event.id
        )
        db.add(family2)
        db.commit()
        print(f"✓ Familie erstellt: Familie {family2.name}")

        # Kinder der Familie Schmidt
        p = Participant(
            first_name="Tom",
            last_name="Schmidt",
            birth_date=date(2011, 3, 10),
            role=role_kind,
            family=family2,
            event=event,
            calculated_price=150.00
        )
        db.add(p)
        print(f"  ✓ Teilnehmer erstellt: {p.full_name}")
        db.commit()

    # Betreuer (ohne Familie)
    betreuer = db.query(Participant).filter(
        Participant.first_name == "Sarah",
        Participant.last_name == "Meyer"
    ).first()
    if not betreuer:
        betreuer = Participant(
            first_name="Sarah",
            last_name="Meyer",
            birth_date=date(1995, 11, 5),
            email="sarah.meyer@example.com",
            phone="0555-123456",
            role=role_betreuer,
            event=event,
            calculated_price=75.00  # 50% Rabatt
        )
        db.add(betreuer)
        db.commit()
        print(f"✓ Betreuer erstellt: {betreuer.full_name}")


def seed_payments(db, event):
    """Erstellt Beispiel-Zahlungen"""
    # Zahlung für Familie Müller
    family1 = db.query(Family).filter(Family.name == "Müller", Family.event_id == event.id).first()
    if family1:
        payment_exists = db.query(Payment).filter(Payment.family_id == family1.id).first()
        if not payment_exists:
            payments = [
                Payment(
                    amount=200.00,
                    payment_date=date(2024, 6, 1),
                    payment_method="Überweisung",
                    reference="Anzahlung Sommerfreizeit",
                    family_id=family1.id,
                    event_id=event.id
                ),
                Payment(
                    amount=90.00,
                    payment_date=date(2024, 7, 1),
                    payment_method="Bar",
                    reference="Restzahlung",
                    family_id=family1.id,
                    event_id=event.id
                )
            ]
            for payment in payments:
                db.add(payment)
                print(f"✓ Zahlung erstellt: {payment.amount}€ für Familie {family1.name}")
            db.commit()

    # Zahlung für Familie Schmidt
    family2 = db.query(Family).filter(Family.name == "Schmidt", Family.event_id == event.id).first()
    if family2:
        payment_exists = db.query(Payment).filter(Payment.family_id == family2.id).first()
        if not payment_exists:
            payment = Payment(
                amount=150.00,
                payment_date=date(2024, 6, 15),
                payment_method="Überweisung",
                reference="Freizeit Tom Schmidt",
                family_id=family2.id,
                event_id=event.id
            )
            db.add(payment)
            db.commit()
            print(f"✓ Zahlung erstellt: {payment.amount}€ für Familie {family2.name}")


def seed_expenses(db, event):
    """Erstellt Beispiel-Ausgaben"""
    expense_exists = db.query(Expense).filter(Expense.title == "Verpflegung", Expense.event_id == event.id).first()
    if not expense_exists:
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
            ),
            Expense(
                title="Spielgeräte",
                description="Bälle, Frisbees und Outdoorspielzeug",
                amount=120.00,
                expense_date=date(2024, 7, 8),
                category="Material",
                paid_by="Sarah Meyer",
                is_settled=True,
                event_id=event.id
            ),
            Expense(
                title="Getränke",
                description="Wasser und Saftschorlen",
                amount=95.00,
                expense_date=date(2024, 7, 12),
                category="Verpflegung",
                paid_by="Anna Müller",
                is_settled=False,
                event_id=event.id
            ),
            Expense(
                title="Erste-Hilfe Material",
                description="Pflaster, Verbandsmaterial",
                amount=42.30,
                expense_date=date(2024, 7, 3),
                category="Sonstiges",
                paid_by="Sarah Meyer",
                is_settled=True,
                event_id=event.id
            )
        ]

        for exp in expenses:
            db.add(exp)
            status = "✓ beglichen" if exp.is_settled else "⏳ offen"
            print(f"✓ Ausgabe erstellt: {exp.title} ({exp.amount}€) - von {exp.paid_by} {status}")

        db.commit()


def main():
    """Hauptfunktion zum Befüllen der Datenbank"""
    print("🌱 Starte Seed-Prozess...\n")

    # Datenbank initialisieren
    init_db()
    db = SessionLocal()

    try:
        print("📅 Erstelle Event...")
        event = seed_event(db)

        print("\n📝 Erstelle Rollen...")
        seed_roles(db, event)

        print("\n📋 Erstelle Regelwerk...")
        ruleset = seed_ruleset(db, event)

        print("\n👨‍👩‍👧‍👦 Erstelle Familien und Teilnehmer...")
        seed_families_and_participants(db, event, ruleset)

        print("\n💰 Erstelle Zahlungen...")
        seed_payments(db, event)

        print("\n💸 Erstelle Ausgaben...")
        seed_expenses(db, event)

        print("\n✅ Seed-Prozess erfolgreich abgeschlossen!")

    except Exception as e:
        print(f"\n❌ Fehler beim Seeding: {e}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()
