"""Helper für Receipt-Upload/-Delete in Expenses/Incomes"""
import logging
from typing import Optional, Tuple
from fastapi import UploadFile, Request
from sqlalchemy.orm import Session

from app.utils.file_upload import save_receipt_file, delete_receipt_file
from app.utils.flash import flash

logger = logging.getLogger(__name__)


async def handle_receipt_upload(
    receipt_file: Optional[UploadFile],
    event_id: int,
    transaction_id: int,
    transaction_type: str,
    db_entity,
    db: Session,
    request: Request
) -> Tuple[bool, Optional[str]]:
    """
    Uploaded Receipt für Expense/Income und speichert den Pfad in der DB.

    Args:
        receipt_file: Die hochgeladene Datei (oder None)
        event_id: ID des Events
        transaction_id: ID der Transaktion (Expense/Income)
        transaction_type: Typ der Transaktion ("expense" oder "income")
        db_entity: Die DB-Entity (Expense oder Income Objekt)
        db: Datenbank-Session
        request: FastAPI Request für Flash-Messages

    Returns:
        Tuple (success, warning_message):
            - success: True wenn erfolgreich oder kein File, False bei Fehler
            - warning_message: Warnmeldung bei teilweisem Fehler, None bei Erfolg

    Example:
        success, warning = await handle_receipt_upload(
            receipt_file, event_id, expense.id, "expense", expense, db, request
        )
        if warning:
            flash(request, f"Ausgabe erstellt, aber {warning}", "warning")
    """
    # Kein File = kein Fehler (Upload ist optional)
    if not receipt_file or not receipt_file.filename:
        return True, None

    # Datei speichern (inkl. Validierung)
    file_path, error = await save_receipt_file(
        receipt_file, event_id, transaction_id, transaction_type
    )

    if error:
        logger.warning(
            f"Failed to upload receipt for {transaction_type} {transaction_id}: {error}"
        )
        return False, f"Beleg-Upload fehlgeschlagen: {error}"

    # Pfad in DB speichern
    db_entity.receipt_file_path = file_path
    try:
        db.commit()
        logger.info(f"Receipt uploaded for {transaction_type} {transaction_id}: {file_path}")
        return True, None

    except Exception as e:
        logger.error(f"Failed to save receipt path to database: {e}", exc_info=True)
        db.rollback()

        # Versuche hochgeladene Datei zu löschen (Cleanup)
        if file_path:
            if delete_receipt_file(file_path):
                logger.info(f"Cleaned up uploaded file after DB error: {file_path}")
            else:
                logger.warning(f"Failed to cleanup uploaded file: {file_path}")

        return False, "Beleg-Upload fehlgeschlagen (Datenbank-Fehler)"


def handle_receipt_delete(
    db_entity,
    db: Session,
    request: Request
) -> bool:
    """
    Löscht Receipt für Expense/Income (Datei + DB-Eintrag).

    Args:
        db_entity: Die DB-Entity (Expense oder Income Objekt)
        db: Datenbank-Session
        request: FastAPI Request für Flash-Messages

    Returns:
        True wenn Receipt gelöscht wurde, False wenn kein Receipt vorhanden war

    Example:
        if handle_receipt_delete(expense, db, request):
            flash(request, "Beleg gelöscht", "success")
    """
    old_path = db_entity.receipt_file_path

    if not old_path:
        # Kein Receipt vorhanden
        return False

    # Datei löschen
    if not delete_receipt_file(old_path):
        logger.warning(f"Failed to delete receipt file: {old_path}")
        flash(
            request,
            "Warnung: Beleg-Datei konnte nicht gelöscht werden",
            "warning"
        )
        # Trotzdem fortfahren und DB-Eintrag löschen

    # DB-Eintrag entfernen
    db_entity.receipt_file_path = None
    try:
        db.commit()
        logger.info(f"Receipt path removed from database: {old_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to remove receipt path from database: {e}", exc_info=True)
        db.rollback()
        flash(request, "Fehler beim Entfernen des Belegs aus der Datenbank", "error")
        return False


async def handle_receipt_update(
    new_receipt_file: Optional[UploadFile],
    event_id: int,
    transaction_id: int,
    transaction_type: str,
    db_entity,
    db: Session,
    request: Request
) -> Tuple[bool, Optional[str]]:
    """
    Updated Receipt für Expense/Income (löscht alten, uploaded neuen).

    Args:
        new_receipt_file: Die neue hochgeladene Datei (oder None)
        event_id: ID des Events
        transaction_id: ID der Transaktion (Expense/Income)
        transaction_type: Typ der Transaktion ("expense" oder "income")
        db_entity: Die DB-Entity (Expense oder Income Objekt)
        db: Datenbank-Session
        request: FastAPI Request für Flash-Messages

    Returns:
        Tuple (success, warning_message):
            - success: True wenn erfolgreich, False bei Fehler
            - warning_message: Warnmeldung bei teilweisem Fehler, None bei Erfolg

    Example:
        success, warning = await handle_receipt_update(
            new_receipt_file, event_id, expense.id, "expense", expense, db, request
        )
        if warning:
            flash(request, warning, "warning")
    """
    # Wenn neues File vorhanden ist
    if new_receipt_file and new_receipt_file.filename:
        # Alten Beleg löschen (falls vorhanden)
        old_path = db_entity.receipt_file_path
        if old_path:
            if not delete_receipt_file(old_path):
                logger.warning(f"Failed to delete old receipt: {old_path}")
                # Trotzdem fortfahren mit neuem Upload

        # Neuen Beleg hochladen
        return await handle_receipt_upload(
            new_receipt_file,
            event_id,
            transaction_id,
            transaction_type,
            db_entity,
            db,
            request
        )

    # Kein neues File = keine Änderung
    return True, None
