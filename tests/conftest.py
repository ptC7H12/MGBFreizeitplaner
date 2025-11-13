"""Pytest Fixtures und Test-Konfiguration"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from datetime import date, timedelta

from app.database import Base
from app.models import Event, Participant, Role, Ruleset, Family, Payment, Expense, Income, Setting


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Erstellt eine temporäre In-Memory-SQLite-Datenbank für Tests
    Jeder Test bekommt eine frische, isolierte Datenbank
    """
    # In-Memory SQLite für schnelle Tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Alle Tabellen erstellen
    Base.metadata.create_all(bind=engine)

    # Session erstellen
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_event(db_session: Session) -> Event:
    """Erstellt ein Beispiel-Event"""
    event = Event(
        name="Testfreizeit 2024",
        event_type="Freizeit",
        start_date=date.today() + timedelta(days=30),
        end_date=date.today() + timedelta(days=37),
        location="Testort",
        is_active=True
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


@pytest.fixture
def sample_roles(db_session: Session, sample_event: Event) -> dict[str, Role]:
    """Erstellt Beispiel-Rollen"""
    roles = {
        'kind': Role(
            event_id=sample_event.id,
            name='kind',
            display_name='Kind',
            color='blue',
            is_active=True
        ),
        'betreuer': Role(
            event_id=sample_event.id,
            name='betreuer',
            display_name='Betreuer',
            color='green',
            is_active=True
        ),
        'kueche': Role(
            event_id=sample_event.id,
            name='kueche',
            display_name='Küche',
            color='orange',
            is_active=True
        )
    }

    for role in roles.values():
        db_session.add(role)

    db_session.commit()

    for role in roles.values():
        db_session.refresh(role)

    return roles


@pytest.fixture
def sample_ruleset(db_session: Session, sample_event: Event) -> Ruleset:
    """Erstellt ein Beispiel-Regelwerk"""
    ruleset = Ruleset(
        event_id=sample_event.id,
        name="Standard-Regelwerk",
        is_active=True,
        valid_from=sample_event.start_date - timedelta(days=365),
        valid_until=sample_event.start_date + timedelta(days=365),
        age_groups=[
            {"name": "Kinder 6-11", "min_age": 6, "max_age": 11, "price": 150.0},
            {"name": "Jugendliche 12-17", "min_age": 12, "max_age": 17, "price": 180.0},
            {"name": "Erwachsene 18+", "min_age": 18, "max_age": 999, "price": 220.0}
        ],
        role_discounts={
            "betreuer": {"discount_percent": 100, "description": "Kostenlos für Betreuer"},
            "kueche": {"discount_percent": 50, "description": "50% für Küchenpersonal"}
        },
        family_discount={
            "enabled": True,
            "second_child_percent": 10,
            "third_plus_child_percent": 20,
            "description": "10% ab 2. Kind, 20% ab 3. Kind"
        }
    )
    db_session.add(ruleset)
    db_session.commit()
    db_session.refresh(ruleset)
    return ruleset


@pytest.fixture
def sample_family(db_session: Session, sample_event: Event) -> Family:
    """Erstellt eine Beispiel-Familie"""
    family = Family(
        event_id=sample_event.id,
        name="Familie Mustermann",
        contact_person="Max Mustermann",
        email="max@mustermann.de",
        phone="0123456789"
    )
    db_session.add(family)
    db_session.commit()
    db_session.refresh(family)
    return family


@pytest.fixture
def sample_participant(
    db_session: Session,
    sample_event: Event,
    sample_roles: dict[str, Role]
) -> Participant:
    """Erstellt einen Beispiel-Teilnehmer"""
    participant = Participant(
        event_id=sample_event.id,
        role_id=sample_roles['kind'].id,
        first_name="Max",
        last_name="Mustermann",
        birth_date=date(2010, 5, 15),  # 14 Jahre alt
        email="max.junior@mustermann.de",
        phone="0123456789",
        address="Musterstraße 1\n12345 Musterstadt",
        calculated_price=180.0,
        discount_percent=0.0,
        manual_price_override=None,
        is_active=True
    )
    db_session.add(participant)
    db_session.commit()
    db_session.refresh(participant)
    return participant


@pytest.fixture
def sample_setting(db_session: Session, sample_event: Event) -> Setting:
    """Erstellt Beispiel-Einstellungen"""
    setting = Setting(
        event_id=sample_event.id,
        organization_name="Test-Organisation",
        organization_address="Teststraße 1\n12345 Teststadt",
        bank_account_holder="Test-Organisation e.V.",
        bank_iban="DE89370400440532013000",
        bank_bic="COBADEFFXXX",
        invoice_subject_prefix="Teilnahme an",
        invoice_footer_text="Vielen Dank für Ihre Zahlung!"
    )
    db_session.add(setting)
    db_session.commit()
    db_session.refresh(setting)
    return setting


# Marker für schnelle Unit-Tests
pytest.mark.unit = pytest.mark.unit

# Marker für Integration-Tests mit DB
pytest.mark.integration = pytest.mark.integration
