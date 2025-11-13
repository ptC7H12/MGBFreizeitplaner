"""Flash Message System - Session-basierte Benachrichtigungen"""
from typing import List, Dict
from fastapi import Request


def flash(request: Request, message: str, category: str = "info"):
    """
    Fügt eine Flash-Message zur Session hinzu

    Args:
        request: FastAPI Request mit Session
        message: Die Nachricht
        category: Kategorie (info, success, warning, error)
    """
    if "_messages" not in request.session:
        request.session["_messages"] = []

    request.session["_messages"].append({
        "message": message,
        "category": category
    })


def get_flashed_messages(request: Request) -> List[Dict[str, str]]:
    """
    Holt und entfernt alle Flash-Messages aus der Session

    Args:
        request: FastAPI Request mit Session

    Returns:
        Liste von Flash-Messages [{"message": "...", "category": "..."}]
    """
    messages = request.session.pop("_messages", [])
    return messages
