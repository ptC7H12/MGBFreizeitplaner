"""Flash Message System - Session-basierte Benachrichtigungen"""
from typing import List, Dict
from fastapi import Request


def flash(request: Request, message: str, category: str = "info") -> None:
    """
    Fügt eine Flash-Message zur Session hinzu.

    Flash-Messages sind einmalige Benachrichtigungen die nach dem
    nächsten Request automatisch gelöscht werden.

    Args:
        request: FastAPI Request mit Session
        message: Die anzuzeigende Nachricht
        category: Nachrichtenkategorie für Styling
            - "info": Informations-Hinweis (blau)
            - "success": Erfolgreiche Operation (grün)
            - "warning": Warnung (gelb)
            - "error": Fehler (rot)

    Example:
        flash(request, "Teilnehmer erfolgreich erstellt", "success")
        flash(request, "Bitte Formular ausfüllen", "error")
    """
    if "_messages" not in request.session:
        request.session["_messages"] = []

    request.session["_messages"].append({
        "message": message,
        "category": category
    })


def get_flashed_messages(request: Request) -> List[Dict[str, str]]:
    """
    Holt und entfernt alle Flash-Messages aus der Session.

    Diese Funktion sollte im Template aufgerufen werden um Messages
    anzuzeigen. Nach dem Abruf werden die Messages gelöscht.

    Args:
        request: FastAPI Request mit Session

    Returns:
        Liste von Message-Dictionaries:
        [{"message": "Text hier", "category": "success"}, ...]

    Example:
        {% for message in get_flashed_messages(request) %}
            <div class="alert alert-{{ message.category }}">
                {{ message.message }}
            </div>
        {% endfor %}
    """
    messages = request.session.pop("_messages", [])
    return messages
