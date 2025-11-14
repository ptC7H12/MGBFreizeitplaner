"""Seed-Script für Beispieldaten"""
from datetime import date, datetime
from pathlib import Path

from app.database import SessionLocal, init_db
from app.models import Event, Family, Participant, Role, Ruleset, Payment, Expense, Income, Setting
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


def seed_settings(db, event):
    """Erstellt Einstellungen für das Event (wichtig für Rechnungen und QR-Codes)"""
    setting = db.query(Setting).filter(Setting.event_id == event.id).first()
    if not setting:
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
        print(f"✓ Einstellungen erstellt für Event: {event.name}")
        print(f"  - Organisation: {setting.organization_name}")
        print(f"  - IBAN: {setting.bank_iban}")
    return setting


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

    # Familie 3: Familie Weber (mit verschiedenen Altersgruppen)
    family3 = db.query(Family).filter(Family.name == "Weber", Family.event_id == event.id).first()
    if not family3:
        family3 = Family(
            name="Weber",
            contact_person="Klaus Weber",
            email="klaus.weber@example.com",
            phone="0176-9876543",
            event_id=event.id
        )
        db.add(family3)
        db.commit()
        print(f"✓ Familie erstellt: Familie {family3.name}")

        # Verschiedene Altersgruppen für bessere Chart-Darstellung
        participants_weber = [
            {
                "first_name": "Emma",
                "last_name": "Weber",
                "birth_date": date(2019, 2, 10),  # 5 Jahre (0-5 Gruppe)
                "role": role_kind,
                "family": family3,
                "calculated_price": 120.00
            },
            {
                "first_name": "Noah",
                "last_name": "Weber",
                "birth_date": date(2016, 9, 18),  # 8 Jahre (6-11 Gruppe)
                "role": role_kind,
                "family": family3,
                "calculated_price": 140.00
            },
            {
                "first_name": "Mia",
                "last_name": "Weber",
                "birth_date": date(2009, 6, 25),  # 15 Jahre (12-17 Gruppe)
                "role": role_kind,
                "family": family3,
                "calculated_price": 150.00
            }
        ]

        for p_data in participants_weber:
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

    # Einzelpersonen (ohne Familie) - verschiedene Rollen
    einzelpersonen = [
        {
            "first_name": "Sarah",
            "last_name": "Meyer",
            "birth_date": date(1995, 11, 5),  # 29 Jahre (26-40 Gruppe)
            "email": "sarah.meyer@example.com",
            "phone": "0555-123456",
            "role": role_betreuer,
            "calculated_price": 75.00  # 50% Rabatt
        },
        {
            "first_name": "Michael",
            "last_name": "Fischer",
            "birth_date": date(2003, 4, 15),  # 21 Jahre (18-25 Gruppe)
            "email": "michael.fischer@example.com",
            "phone": "0172-2345678",
            "role": role_betreuer,
            "calculated_price": 75.00
        },
        {
            "first_name": "Julia",
            "last_name": "Becker",
            "birth_date": date(1978, 8, 30),  # 46 Jahre (41+ Gruppe)
            "email": "julia.becker@example.com",
            "phone": "0160-7654321",
            "role": role_kueche,
            "calculated_price": 50.00  # Küchenpersonal Rabatt
        }
    ]

    for ep_data in einzelpersonen:
        existing = db.query(Participant).filter(
            Participant.first_name == ep_data["first_name"],
            Participant.last_name == ep_data["last_name"],
            Participant.event_id == event.id
        ).first()

        if not existing:
            ep = Participant(
                first_name=ep_data["first_name"],
                last_name=ep_data["last_name"],
                birth_date=ep_data["birth_date"],
                email=ep_data.get("email"),
                phone=ep_data.get("phone"),
                role=ep_data["role"],
                event=event,
                calculated_price=ep_data["calculated_price"]
            )
            db.add(ep)
            db.commit()
            print(f"✓ {ep_data['role'].display_name} erstellt: {ep.full_name}")


def seed_payments(db, event):
    """Erstellt Beispiel-Zahlungen (über verschiedene Tage verteilt für Timeline-Chart)"""
    # Zahlung für Familie Müller
    family1 = db.query(Family).filter(Family.name == "Müller", Family.event_id == event.id).first()
    if family1:
        payment_exists = db.query(Payment).filter(Payment.family_id == family1.id).first()
        if not payment_exists:
            payments = [
                Payment(
                    amount=200.00,
                    payment_date=date(2024, 5, 15),
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
                payment_date=date(2024, 5, 20),
                payment_method="Überweisung",
                reference="Freizeit Tom Schmidt",
                family_id=family2.id,
                event_id=event.id
            )
            db.add(payment)
            db.commit()
            print(f"✓ Zahlung erstellt: {payment.amount}€ für Familie {family2.name}")

    # Zahlung für Familie Weber (neu)
    family3 = db.query(Family).filter(Family.name == "Weber", Family.event_id == event.id).first()
    if family3:
        payment_exists = db.query(Payment).filter(Payment.family_id == family3.id).first()
        if not payment_exists:
            payments_weber = [
                Payment(
                    amount=100.00,
                    payment_date=date(2024, 5, 25),
                    payment_method="Überweisung",
                    reference="Anzahlung Weber",
                    family_id=family3.id,
                    event_id=event.id
                ),
                Payment(
                    amount=150.00,
                    payment_date=date(2024, 6, 10),
                    payment_method="Überweisung",
                    reference="2. Rate Weber",
                    family_id=family3.id,
                    event_id=event.id
                ),
                Payment(
                    amount=160.00,
                    payment_date=date(2024, 6, 28),
                    payment_method="Bar",
                    reference="Restzahlung Weber",
                    family_id=family3.id,
                    event_id=event.id
                )
            ]
            for payment in payments_weber:
                db.add(payment)
                print(f"✓ Zahlung erstellt: {payment.amount}€ für Familie {family3.name}")
            db.commit()

    # Einzelzahlungen für Betreuer/Küchenpersonal
    einzelpersonen_zahlungen = [
        {
            "first_name": "Sarah",
            "last_name": "Meyer",
            "amount": 75.00,
            "date": date(2024, 6, 5),
            "method": "Überweisung"
        },
        {
            "first_name": "Michael",
            "last_name": "Fischer",
            "amount": 75.00,
            "date": date(2024, 6, 12),
            "method": "PayPal"
        },
        {
            "first_name": "Julia",
            "last_name": "Becker",
            "amount": 50.00,
            "date": date(2024, 6, 18),
            "method": "Bar"
        }
    ]

    for ez in einzelpersonen_zahlungen:
        participant = db.query(Participant).filter(
            Participant.first_name == ez["first_name"],
            Participant.last_name == ez["last_name"],
            Participant.event_id == event.id
        ).first()

        if participant:
            existing_payment = db.query(Payment).filter(
                Payment.participant_id == participant.id
            ).first()

            if not existing_payment:
                payment = Payment(
                    amount=ez["amount"],
                    payment_date=ez["date"],
                    payment_method=ez["method"],
                    reference=f"Teilnahmegebühr {participant.full_name}",
                    participant_id=participant.id,
                    event_id=event.id
                )
                db.add(payment)
                db.commit()
                print(f"✓ Zahlung erstellt: {payment.amount}€ für {participant.full_name}")


def seed_incomes(db, event):
    """Erstellt Beispiel-Einnahmen"""
    income_exists = db.query(Income).filter(Income.event_id == event.id).first()
    if not income_exists:
        # Rollen für Zuschüsse abrufen
        role_kind = db.query(Role).filter(Role.name == "kind", Role.event_id == event.id).first()
        role_jugendlicher = db.query(Role).filter(Role.name == "jugendlicher", Role.event_id == event.id).first()

        incomes = [
            Income(
                name="Zuschuss Jugendamt",
                description="Förderung für Kinder- und Jugendarbeit (Quelle: Jugendamt Stadt Beispielstadt)",
                amount=500.00,
                date=date(2024, 6, 1),
                role_id=role_kind.id if role_kind else None,
                event_id=event.id
            ),
            Income(
                name="Spende Förderverein",
                description="Spende des Fördervereins für Freizeitaktivitäten (Quelle: Förderverein Jugendarbeit e.V.)",
                amount=250.00,
                date=date(2024, 5, 15),
                event_id=event.id
            ),
            Income(
                name="Zuschuss Kirchengemeinde",
                description="Förderung kirchliche Jugendarbeit (Quelle: Ev. Kirchengemeinde Beispielstadt)",
                amount=300.00,
                date=date(2024, 6, 10),
                role_id=role_jugendlicher.id if role_jugendlicher else None,
                event_id=event.id
            )
        ]

        for income in incomes:
            db.add(income)
            print(f"✓ Einnahme erstellt: {income.name} ({income.amount}€)")

        db.commit()


def seed_expenses(db, event):
    """Erstellt Beispiel-Ausgaben"""
    expense_exists = db.query(Expense).filter(Expense.title == "Verpflegung Supermarkt", Expense.event_id == event.id).first()
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

        print("\n⚙️  Erstelle Einstellungen...")
        seed_settings(db, event)

        print("\n📝 Erstelle Rollen...")
        seed_roles(db, event)

        print("\n📋 Erstelle Regelwerk...")
        ruleset = seed_ruleset(db, event)

        print("\n👨‍👩‍👧‍👦 Erstelle Familien und Teilnehmer...")
        seed_families_and_participants(db, event, ruleset)

        print("\n💰 Erstelle Zahlungen...")
        seed_payments(db, event)

        print("\n💵 Erstelle Einnahmen...")
        seed_incomes(db, event)

        print("\n💸 Erstelle Ausgaben...")
        seed_expenses(db, event)

        print("\n✅ Seed-Prozess erfolgreich abgeschlossen!")
        print("\n📊 Zusammenfassung:")
        print(f"   • Event: {event.name}")
        print(f"   • Teilnehmer: {db.query(Participant).filter(Participant.event_id == event.id).count()}")
        print(f"   • Familien: {db.query(Family).filter(Family.event_id == event.id).count()}")
        print(f"   • Zahlungen: {db.query(Payment).filter(Payment.event_id == event.id).count()}")
        print(f"   • Einnahmen: {db.query(Income).filter(Income.event_id == event.id).count()}")
        print(f"   • Ausgaben: {db.query(Expense).filter(Expense.event_id == event.id).count()}")

    except Exception as e:
        print(f"\n❌ Fehler beim Seeding: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()
