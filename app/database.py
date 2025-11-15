"""Datenbank-Setup und Session-Management"""
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

# SQLAlchemy Engine erstellen
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug
)

# Session-Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Basis-Klasse für alle Models
Base = declarative_base()


def get_db():
    """
    Dependency für FastAPI-Routen.
    Stellt eine Datenbank-Session bereit und schließt sie nach der Anfrage.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def transaction(db: Session):
    """
    Context Manager für sichere Datenbank-Transaktionen.

    Verwendung:
        with transaction(db):
            db.add(participant)
            db.flush()  # Für ID-Generierung
            # Weitere Operationen...
        # Auto-commit bei Erfolg, auto-rollback bei Exception

    Vorteil:
        - Automatisches commit() bei Erfolg
        - Automatisches rollback() bei Exceptions
        - Keine vergessenen commits/rollbacks mehr
        - Sauberere Code-Struktur
    """
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise


def init_db():
    """Initialisiert die Datenbank und erstellt alle Tabellen"""
    from app.models import participant, family, role, ruleset, payment, expense, income, event, task
    Base.metadata.create_all(bind=engine)
