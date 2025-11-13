"""Datenbank-Setup und Session-Management"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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


def init_db():
    """Initialisiert die Datenbank und erstellt alle Tabellen"""
    from app.models import participant, family, role, ruleset, payment, expense, event, task
    Base.metadata.create_all(bind=engine)
