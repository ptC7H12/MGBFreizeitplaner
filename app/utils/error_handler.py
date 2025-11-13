"""Error Handler Utility - Zentralisierte Fehlerbehandlung"""
import logging
from typing import Optional
from sqlalchemy.exc import IntegrityError, DataError, OperationalError
from fastapi import Request
from fastapi.responses import RedirectResponse

logger = logging.getLogger(__name__)


def handle_db_exception(
    e: Exception,
    redirect_url: str,
    operation: str,
    db_session=None,
    request: Optional[Request] = None
) -> RedirectResponse:
    """
    Zentralisierte Fehlerbehandlung mit Logging und benutzerfreundlichen Error-Codes

    Args:
        e: Die aufgetretene Exception
        redirect_url: URL für die Weiterleitung
        operation: Beschreibung der Operation (für Logging)
        db_session: Datenbank-Session für Rollback (optional)
        request: FastAPI Request für Flash-Messages (optional)

    Returns:
        RedirectResponse mit entsprechendem Error-Code
    """
    # Rollback falls Session vorhanden
    if db_session:
        try:
            db_session.rollback()
        except Exception as rollback_error:
            logger.error(f"Rollback failed: {rollback_error}")

    # Flash-Message setzen falls Request vorhanden
    error_message = ""
    error_code = "unexpected"

    # Spezifische Fehlerbehandlung
    if isinstance(e, ValueError):
        logger.warning(f"{operation}: Invalid input - {str(e)}", exc_info=True)
        error_message = "Ungültige Eingabe. Bitte überprüfen Sie Ihre Daten."
        error_code = "invalid_input"

    elif isinstance(e, IntegrityError):
        logger.error(f"{operation}: Database integrity error - {str(e)}", exc_info=True)
        error_message = "Datenbankfehler: Diese Daten verletzen eine Integritätsbedingung."
        error_code = "db_integrity"

    elif isinstance(e, DataError):
        logger.error(f"{operation}: Invalid data - {str(e)}", exc_info=True)
        error_message = "Ungültige Daten. Bitte überprüfen Sie Ihre Eingaben."
        error_code = "invalid_data"

    elif isinstance(e, OperationalError):
        logger.error(f"{operation}: Database operational error - {str(e)}", exc_info=True)
        error_message = "Datenbankverbindungsfehler. Bitte versuchen Sie es später erneut."
        error_code = "db_error"

    else:
        logger.exception(f"{operation}: Unexpected error - {str(e)}")
        error_message = "Ein unerwarteter Fehler ist aufgetreten. Bitte kontaktieren Sie den Administrator."
        error_code = "unexpected"

    # Flash-Message setzen
    if request:
        from app.utils.flash import flash
        flash(request, error_message, "error")

    # Redirect mit Error-Code (als Fallback)
    return RedirectResponse(url=f"{redirect_url}?error={error_code}", status_code=303)
