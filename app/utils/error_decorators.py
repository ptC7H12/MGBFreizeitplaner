"""Decorator für konsistentes Error-Handling in Routern"""
import logging
from functools import wraps
from typing import Callable, Optional
from fastapi import Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm import Session

from app.utils.flash import flash
from app.utils.error_handler import handle_db_exception

logger = logging.getLogger(__name__)


def handle_route_errors(
    entity_name: str,
    redirect_url_on_error: str,
    operation: str = "Creating"
):
    """
    Decorator für einheitliches Error-Handling in POST-Routes.

    Fängt häufige Exceptions ab und leitet mit Flash-Messages weiter:
    - ValidationError (Pydantic): Ungültige Eingabedaten
    - ValueError: Logik-Fehler in der Anwendung
    - IntegrityError: Datenbank-Integritätsverletzung
    - DataError: Ungültige Daten für Datenbank
    - Exception: Catch-All für unerwartete Fehler

    Args:
        entity_name: Name der Entity für Fehlermeldungen (z.B. "Teilnehmer", "Ausgabe")
        redirect_url_on_error: URL für Redirect bei Fehler
        operation: Operation-Beschreibung für Logging (z.B. "Creating participant")

    Usage:
        @router.post("/create")
        @handle_route_errors("Teilnehmer", "/participants/create", "Creating participant")
        async def create_participant(
            request: Request,
            db: Session = Depends(get_db),
            ...
        ):
            # Deine Logik hier - ohne try-catch!
            # Der Decorator fängt alle Fehler ab
            pass

    Wichtig:
        - Die dekorierte Funktion MUSS 'request' und 'db' als Parameter haben
        - 'request' kann als positionaler oder Keyword-Argument übergeben werden
        - 'db' kann als positionaler oder Keyword-Argument übergeben werden
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Request und DB aus Args oder Kwargs extrahieren
            request: Optional[Request] = None
            db: Optional[Session] = None

            # Versuche Request aus kwargs zu holen
            if 'request' in kwargs:
                request = kwargs['request']
            # Falls nicht in kwargs, versuche aus args (meist erster Parameter)
            elif len(args) > 0 and isinstance(args[0], Request):
                request = args[0]

            # Versuche DB aus kwargs zu holen
            if 'db' in kwargs:
                db = kwargs['db']
            # Falls nicht in kwargs, versuche aus args (meist zweiter Parameter)
            elif len(args) > 1 and isinstance(args[1], Session):
                db = args[1]

            try:
                return await func(*args, **kwargs)

            except ValidationError as e:
                logger.warning(f"Validation error {operation} {entity_name}: {e}", exc_info=True)

                # Ersten Fehler extrahieren für benutzerfreundliche Meldung
                first_error = e.errors()[0]
                field_name = first_error['loc'][0] if first_error['loc'] else 'Unbekannt'
                error_msg = first_error['msg']

                if request:
                    flash(request, f"Validierungsfehler ({field_name}): {error_msg}", "error")

                return RedirectResponse(
                    url=f"{redirect_url_on_error}?error=validation",
                    status_code=303
                )

            except ValueError as e:
                logger.warning(f"Invalid input {operation} {entity_name}: {e}", exc_info=True)

                if request:
                    flash(request, f"Ungültige Eingabe: {str(e)}", "error")

                return RedirectResponse(
                    url=f"{redirect_url_on_error}?error=invalid_input",
                    status_code=303
                )

            except IntegrityError as e:
                if db:
                    db.rollback()

                logger.error(f"Database integrity error {operation} {entity_name}: {e}", exc_info=True)

                if request:
                    flash(request, f"{entity_name} konnte nicht erstellt werden (Datenbankfehler)", "error")

                return RedirectResponse(
                    url=f"{redirect_url_on_error}?error=db_integrity",
                    status_code=303
                )

            except DataError as e:
                if db:
                    db.rollback()

                logger.error(f"Invalid data {operation} {entity_name}: {e}", exc_info=True)

                if request:
                    flash(request, "Ungültige Daten eingegeben", "error")

                return RedirectResponse(
                    url=f"{redirect_url_on_error}?error=invalid_data",
                    status_code=303
                )

            except Exception as e:
                # Verwende handle_db_exception für alle anderen Fehler
                return handle_db_exception(
                    e,
                    redirect_url_on_error,
                    f"{operation} {entity_name}",
                    db,
                    request
                )

        return wrapper
    return decorator
