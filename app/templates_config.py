"""Zentrale Template-Konfiguration für alle Router"""
from fastapi.templating import Jinja2Templates
from app.config import settings
from app.utils.flash import get_flashed_messages

# Zentrale Templates-Instanz mit allen Globals
templates = Jinja2Templates(directory=str(settings.templates_dir))

# Flash-Messages als Template-Global registrieren
templates.env.globals['get_flashed_messages'] = get_flashed_messages
