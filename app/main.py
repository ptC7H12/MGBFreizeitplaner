"""Hauptanwendung für das Freizeit-Kassen-System"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import logging

from app.config import settings
from app.database import init_db
from app.routers import dashboard, participants, families, rulesets

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

# Static Files mounten
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

# Templates konfigurieren
templates = Jinja2Templates(directory=str(settings.templates_dir))

# Router registrieren
app.include_router(dashboard.router)
app.include_router(participants.router)
app.include_router(families.router)
app.include_router(rulesets.router)


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
    """Weiterleitung zum Dashboard"""
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "Dashboard"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
