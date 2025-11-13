"""Dependencies for FastAPI - Session Management"""
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session

from app.models.event import Event


def get_current_event_id(request: Request) -> int:
    """
    Holt die aktuelle Event-ID aus der Session
    Wirft HTTPException wenn keine Event-ID gesetzt ist
    """
    event_id = request.session.get("event_id")
    if not event_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Keine Freizeit ausgewählt. Bitte melden Sie sich an."
        )
    return event_id


def get_current_event(request: Request, db: Session) -> Event:
    """
    Holt das aktuelle Event-Objekt aus der Datenbank
    Wirft HTTPException wenn Event nicht gefunden wird
    """
    event_id = get_current_event_id(request)
    event = db.query(Event).filter(Event.id == event_id, Event.is_active == True).first()

    if not event:
        # Session invalidieren wenn Event nicht mehr existiert
        request.session.pop("event_id", None)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Freizeit nicht gefunden oder nicht aktiv."
        )

    return event


def get_current_event_id_optional(request: Request) -> int | None:
    """
    Holt die aktuelle Event-ID aus der Session
    Gibt None zurück wenn keine Event-ID gesetzt ist (keine Exception)
    """
    return request.session.get("event_id")
