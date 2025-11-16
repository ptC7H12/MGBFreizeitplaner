"""Datenbank-Setup und Session-Management"""
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

# SQLAlchemy Engine erstellen mit optimiertem Connection Pooling
engine_kwargs = {
    "echo": settings.debug,
}

# SQLite-spezifische Konfiguration
if "sqlite" in settings.database_url:
    engine_kwargs["connect_args"] = {
        "check_same_thread": False,  # Erlaube Thread-Sharing (notwendig für FastAPI)
        "timeout": 30,  # Warte bis zu 30 Sekunden auf DB-Lock
    }
    # SQLite: Connection Pool mit Overflow
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10
    engine_kwargs["pool_pre_ping"] = True  # Teste Connection vor Verwendung
    engine_kwargs["pool_recycle"] = 3600  # Recycle Connections nach 1 Stunde

# PostgreSQL-spezifische Konfiguration
else:
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 40
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 3600

engine = create_engine(settings.database_url, **engine_kwargs)

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
    """
    Initialisiert die Datenbank und erstellt alle Tabellen

    HINWEIS: In Production sollte Alembic für Schema-Verwaltung verwendet werden:
        - Für neue Installationen: `alembic upgrade head`
        - Für bestehende DBs: `alembic stamp head` (markiert aktuelle Version)
        - Für Schema-Änderungen: `alembic revision --autogenerate -m "..."`

    Diese Methode (create_all) wird nur für Demo-Daten und Entwicklung verwendet.
    """
    from app.models import participant, family, role, ruleset, payment, expense, income, event, task
    Base.metadata.create_all(bind=engine)
