"""Hauptanwendung für das Freizeit-Kassen-System"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import secrets

from app.config import settings
from app.logging_config import setup_logging
from app.database import init_db
from app.templates_config import templates
from app.routers import dashboard, participants, families, rulesets, payments, expenses, incomes, auth, settings as settings_router, tasks, backups, cash_status

# Logging konfigurieren (strukturiert mit Datei-Rotation)
setup_logging(debug=settings.debug)
logger = logging.getLogger(__name__)

# Rate Limiter konfigurieren (schützt vor Fehlbedienung)
# Für lokalen Single-User Betrieb: Großzügige Limits
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan Context Manager für Startup und Shutdown Events.
    Ersetzt die deprecated @app.on_event("startup") und @app.on_event("shutdown") Dekoratoren.
    """
    # ===== STARTUP =====
    logger.info(f"Starte {settings.app_name} v{settings.app_version}")

    # Warnung wenn SECRET_KEY nicht gesetzt ist
    if not settings.is_secret_key_from_env():
        logger.warning("=" * 80)
        logger.warning("⚠️  SECRET_KEY ist nicht in .env gesetzt!")
        logger.warning("⚠️  Sessions gehen bei jedem Neustart verloren!")
        logger.warning("⚠️  Bitte SECRET_KEY in .env setzen für persistente Sessions.")
        logger.warning("⚠️  Generieren: python generate_secret_key.py")
        logger.warning("=" * 80)

    logger.info("Initialisiere Datenbank...")
    init_db()
    logger.info("Datenbank erfolgreich initialisiert!")

    # Prüfe und führe Alembic-Migrationen aus (automatisch)
    try:
        from app.utils.migration_checker import check_and_run_migrations
        check_and_run_migrations(auto_upgrade=True)
    except RuntimeError as e:
        logger.error(f"Migrations-Fehler beim Start: {e}")
        logger.error("App wird NICHT gestartet - bitte Migrationen manuell prüfen!")
        raise
    except Exception as e:
        logger.warning(f"Migrations-Check fehlgeschlagen: {e}")
        logger.warning("App wird trotzdem gestartet (Migration manuell prüfen!)")

    # Prüfen ob Demo-Daten erstellt werden sollen (nur beim ersten Start)
    from app.database import SessionLocal
    from app.models.event import Event
    db = SessionLocal()
    try:
        event_count = db.query(Event).count()
        if event_count == 0:
            logger.info("Keine Events gefunden - erstelle Demo-Daten...")
            from app.utils.seed_helper import create_demo_data
            create_demo_data(db)
            logger.info("Demo-Daten erfolgreich erstellt!")
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Demo-Daten: {e}")
    finally:
        db.close()

    # App läuft...
    yield

    # ===== SHUTDOWN =====
    logger.info(f"Beende {settings.app_name}")


# FastAPI App erstellen
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# Rate Limiter zur App hinzufügen
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Session Middleware hinzufügen
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key
)

# Static Files mounten
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

# Router registrieren
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(tasks.router)
app.include_router(participants.router)
app.include_router(families.router)
app.include_router(rulesets.router)
app.include_router(payments.router)
app.include_router(expenses.router)
app.include_router(incomes.router)
app.include_router(cash_status.router)
app.include_router(settings_router.router)
app.include_router(backups.router)


@app.get("/health")
async def health_check():
    """Health-Check-Endpunkt für Docker"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Weiterleitung zur Landing Page oder Dashboard"""
    # Prüfen ob Event in Session vorhanden ist
    event_id = request.session.get("event_id")
    if event_id:
        # Bereits eingeloggt -> zum Dashboard
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        # Nicht eingeloggt -> zur Landing Page
        return RedirectResponse(url="/auth/", status_code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
