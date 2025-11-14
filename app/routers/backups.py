"""Backup Router"""
import logging
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_event_id
from app.services.backup_service import BackupService
from app.utils.flash import flash
from app.templates_config import templates
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/backups", tags=["backups"])

# Backup-Service initialisieren
backup_service = BackupService(
    db_path=settings.database_url.replace("sqlite:///", ""),
    backup_dir=str(settings.base_dir / "backups")
)


@router.get("/", response_class=HTMLResponse)
async def list_backups(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Liste aller Backups"""
    try:
        backups = backup_service.list_backups()
        stats = backup_service.get_backup_stats()

        return templates.TemplateResponse(
            "backups/list.html",
            {
                "request": request,
                "title": "Backups",
                "backups": backups,
                "stats": stats
            }
        )
    except Exception as e:
        logger.error(f"Fehler beim Laden der Backups: {e}")
        flash(request, f"Fehler beim Laden der Backups: {str(e)}", "error")
        return RedirectResponse(url="/dashboard", status_code=303)


@router.post("/create")
async def create_backup(
    request: Request,
    description: str = Form(default=""),
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Erstellt ein neues Backup"""
    try:
        result = backup_service.create_backup(description=description)
        flash(request, f"Backup '{result['filename']}' erfolgreich erstellt", "success")
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Backups: {e}")
        flash(request, f"Fehler beim Erstellen des Backups: {str(e)}", "error")

    return RedirectResponse(url="/backups", status_code=303)


@router.post("/{filename}/delete")
async def delete_backup(
    filename: str,
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Löscht ein Backup"""
    try:
        backup_service.delete_backup(filename)
        flash(request, f"Backup '{filename}' erfolgreich gelöscht", "success")
    except FileNotFoundError:
        flash(request, f"Backup '{filename}' nicht gefunden", "error")
    except Exception as e:
        logger.error(f"Fehler beim Löschen des Backups: {e}")
        flash(request, f"Fehler beim Löschen des Backups: {str(e)}", "error")

    return RedirectResponse(url="/backups", status_code=303)


@router.get("/{filename}/download")
async def download_backup(
    filename: str,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Download eines Backups"""
    try:
        backups = backup_service.list_backups()
        backup = next((b for b in backups if b['filename'] == filename), None)

        if not backup:
            raise FileNotFoundError(f"Backup '{filename}' nicht gefunden")

        return FileResponse(
            path=backup['path'],
            filename=filename,
            media_type='application/octet-stream'
        )
    except Exception as e:
        logger.error(f"Fehler beim Download des Backups: {e}")
        raise


@router.post("/cleanup")
async def cleanup_old_backups(
    request: Request,
    max_age_days: int = Form(default=30),
    keep_min: int = Form(default=5),
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Räumt alte Backups auf"""
    try:
        deleted_count = backup_service.cleanup_old_backups(
            max_age_days=max_age_days,
            keep_min=keep_min
        )
        flash(request, f"{deleted_count} alte Backups erfolgreich gelöscht", "success")
    except Exception as e:
        logger.error(f"Fehler beim Aufräumen der Backups: {e}")
        flash(request, f"Fehler beim Aufräumen der Backups: {str(e)}", "error")

    return RedirectResponse(url="/backups", status_code=303)


@router.post("/{filename}/restore")
async def restore_backup(
    filename: str,
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Stellt ein Backup wieder her"""
    try:
        backup_service.restore_backup(filename)
        flash(request, f"Backup '{filename}' erfolgreich wiederhergestellt. Bitte Anwendung neu starten!", "success")
    except FileNotFoundError:
        flash(request, f"Backup '{filename}' nicht gefunden", "error")
    except Exception as e:
        logger.error(f"Fehler beim Wiederherstellen des Backups: {e}")
        flash(request, f"Fehler beim Wiederherstellen des Backups: {str(e)}", "error")

    return RedirectResponse(url="/backups", status_code=303)
