"""Hauptanwendung für das Freizeit-Kassen-System"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import logging
import secrets

from app.config import settings
from app.database import init_db
from app.routers import dashboard, participants, families, rulesets, payments, expenses, auth, settings as settings_router

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI App erstellen
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# Session Middleware hinzufügen
# WICHTIG: In Produktion sollte der secret_key aus einer Umgebungsvariable kommen!
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key if hasattr(settings, 'secret_key') else secrets.token_urlsafe(32)
)

# Static Files mounten
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

# Templates konfigurieren
templates = Jinja2Templates(directory=str(settings.templates_dir))

# Flash-Messages als Template-Global registrieren
from app.utils.flash import get_flashed_messages
templates.env.globals['get_flashed_messages'] = get_flashed_messages

# Router registrieren
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(participants.router)
app.include_router(families.router)
app.include_router(rulesets.router)
app.include_router(payments.router)
app.include_router(expenses.router)
app.include_router(settings_router.router)


@app.on_event("startup")
async def startup_event():
    """Wird beim Start der Anwendung ausgeführt"""
    logger.info(f"Starte {settings.app_name} v{settings.app_version}")
    logger.info("Initialisiere Datenbank...")
    init_db()
    logger.info("Datenbank erfolgreich initialisiert!")


@app.on_event("shutdown")
async def shutdown_event():
    """Wird beim Beenden der Anwendung ausgeführt"""
    logger.info(f"Beende {settings.app_name}")


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
