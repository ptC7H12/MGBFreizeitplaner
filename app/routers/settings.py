"""Settings (Einstellungen) Router"""
import logging
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
from typing import Optional
from pydantic import ValidationError

from app.config import settings
from app.database import get_db
from app.models import Setting, Event, Ruleset, Expense
from app.dependencies import get_current_event_id
from sqlalchemy import func
from app.utils.error_handler import handle_db_exception
from app.utils.flash import flash
from app.schemas import SettingUpdateSchema
from app.templates_config import templates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])


def _get_or_create_setting(db: Session, event_id: int) -> Setting:
    """
    Holt oder erstellt Event-Settings

    Args:
        db: Database Session
        event_id: Event ID

    Returns:
        Setting-Objekt
    """
    setting = db.query(Setting).filter(Setting.event_id == event_id).first()

    if not setting:
        # Keine Einstellungen vorhanden -> Standard-Einstellungen erstellen
        setting = Setting(event_id=event_id)
        db.add(setting)
        db.commit()
        db.refresh(setting)
        logger.info(f"Created default settings for event {event_id}")

    return setting


@router.get("/", response_class=HTMLResponse)
async def view_settings(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Zeigt die Einstellungen für das aktuelle Event"""
    # Einstellungen für das Event laden (oder Standard-Einstellungen erstellen)
    setting = _get_or_create_setting(db, event_id)
    event = db.query(Event).filter(Event.id == event_id).first()

    # Alle Rulesets für Dropdown
    rulesets = db.query(Ruleset).filter(Ruleset.event_id == event_id).order_by(Ruleset.valid_from.desc()).all()

    # Kategorien mit Anzahl der Ausgaben laden
    categories_query = db.query(
        Expense.category,
        func.count(Expense.id).label('count')
    ).filter(
        Expense.event_id == event_id,
        Expense.category.isnot(None),
        Expense.category != ''
    ).group_by(Expense.category).order_by(Expense.category).all()

    categories = [{'name': cat.category, 'count': cat.count} for cat in categories_query]

    return templates.TemplateResponse(
        "settings/view.html",
        {
            "request": request,
            "title": "Einstellungen",
            "setting": setting,
            "event": event,
            "rulesets": rulesets,
            "categories": categories
        }
    )


@router.get("/edit", response_class=HTMLResponse)
async def edit_settings_form(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Formular zum Bearbeiten der Einstellungen"""
    # Einstellungen für das Event laden (oder Standard-Einstellungen erstellen)
    setting = _get_or_create_setting(db, event_id)
    event = db.query(Event).filter(Event.id == event_id).first()

    # Alle Rulesets für Dropdown
    rulesets = db.query(Ruleset).filter(Ruleset.event_id == event_id).order_by(Ruleset.valid_from.desc()).all()

    return templates.TemplateResponse(
        "settings/edit.html",
        {
            "request": request,
            "title": "Einstellungen bearbeiten",
            "setting": setting,
            "event": event,
            "rulesets": rulesets
        }
    )


@router.post("/edit", response_class=HTMLResponse)
async def update_settings(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    organization_name: str = Form(...),
    organization_address: Optional[str] = Form(None),
    bank_account_holder: str = Form(...),
    bank_iban: str = Form(...),
    bank_bic: Optional[str] = Form(None),
    invoice_subject_prefix: Optional[str] = Form(None),
    invoice_footer_text: Optional[str] = Form(None),
    default_github_repo: Optional[str] = Form(None),
    current_tab: Optional[str] = Form("general")
):
    """Aktualisiert die Einstellungen"""
    setting = db.query(Setting).filter(Setting.event_id == event_id).first()

    if not setting:
        # Keine Einstellungen vorhanden -> neue erstellen
        setting = Setting(event_id=event_id)
        db.add(setting)

    try:
        # Pydantic-Validierung
        setting_data = SettingUpdateSchema(
            organization_name=organization_name,
            organization_address=organization_address,
            bank_account_holder=bank_account_holder,
            bank_iban=bank_iban,
            bank_bic=bank_bic,
            invoice_subject_prefix=invoice_subject_prefix,
            invoice_footer_text=invoice_footer_text,
            default_github_repo=default_github_repo
        )

        # Einstellungen aktualisieren
        setting.organization_name = setting_data.organization_name
        setting.organization_address = setting_data.organization_address
        setting.bank_account_holder = setting_data.bank_account_holder
        setting.bank_iban = setting_data.bank_iban
        setting.bank_bic = setting_data.bank_bic
        setting.invoice_subject_prefix = setting_data.invoice_subject_prefix if setting_data.invoice_subject_prefix else "Teilnahme an"
        setting.invoice_footer_text = setting_data.invoice_footer_text if setting_data.invoice_footer_text else "Vielen Dank für Ihre Zahlung!"
        setting.default_github_repo = setting_data.default_github_repo

        db.commit()

        flash(request, "Einstellungen wurden erfolgreich aktualisiert", "success")
        # Redirect zurück zum selben Tab
        redirect_url = f"/settings#{current_tab}" if current_tab and current_tab != "general" else "/settings"
        return RedirectResponse(url=redirect_url, status_code=303)

    except ValidationError as e:
        # Pydantic-Validierungsfehler
        logger.warning(f"Validation error updating settings: {e}", exc_info=True)
        first_error = e.errors()[0]
        field_name = first_error['loc'][0] if first_error['loc'] else 'Unbekannt'
        error_msg = first_error['msg']
        flash(request, f"Validierungsfehler ({field_name}): {error_msg}", "error")
        redirect_url = f"/settings/edit#{current_tab}" if current_tab and current_tab != "general" else "/settings/edit"
        return RedirectResponse(url=redirect_url, status_code=303)

    except ValueError as e:
        logger.warning(f"Invalid input for settings update: {e}", exc_info=True)
        flash(request, f"Ungültige Eingabe: {str(e)}", "error")
        redirect_url = f"/settings/edit#{current_tab}" if current_tab and current_tab != "general" else "/settings/edit"
        return RedirectResponse(url=redirect_url, status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error updating settings: {e}", exc_info=True)
        flash(request, "Einstellungen konnten nicht aktualisiert werden (Datenbankfehler)", "error")
        redirect_url = f"/settings/edit#{current_tab}" if current_tab and current_tab != "general" else "/settings/edit"
        return RedirectResponse(url=redirect_url, status_code=303)

    except DataError as e:
        db.rollback()
        logger.error(f"Invalid data updating settings: {e}", exc_info=True)
        flash(request, "Ungültige Daten eingegeben", "error")
        redirect_url = f"/settings/edit#{current_tab}" if current_tab and current_tab != "general" else "/settings/edit"
        return RedirectResponse(url=redirect_url, status_code=303)

    except Exception as e:
        return handle_db_exception(e, f"/settings/edit#{current_tab}" if current_tab else "/settings/edit", "Updating settings", db, request)


@router.post("/categories/rename")
async def rename_category(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    old_name: str = Form(...),
    new_name: str = Form(...)
):
    """Benennt eine Kategorie um und aktualisiert alle zugehörigen Ausgaben"""
    try:
        # Validierung
        if not old_name or not new_name:
            raise HTTPException(status_code=400, detail="Kategorienamen dürfen nicht leer sein")

        if old_name == new_name:
            raise HTTPException(status_code=400, detail="Alter und neuer Name sind identisch")

        # Prüfen ob neue Kategorie bereits existiert
        existing = db.query(Expense).filter(
            Expense.event_id == event_id,
            Expense.category == new_name
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail=f"Kategorie '{new_name}' existiert bereits")

        # Alle Ausgaben mit der alten Kategorie aktualisieren
        updated_count = db.query(Expense).filter(
            Expense.event_id == event_id,
            Expense.category == old_name
        ).update({'category': new_name})

        db.commit()

        logger.info(f"Renamed category '{old_name}' to '{new_name}' for event {event_id}, updated {updated_count} expenses")
        flash(request, f"Kategorie '{old_name}' wurde zu '{new_name}' umbenannt ({updated_count} Ausgaben aktualisiert)", "success")
        return RedirectResponse(url="/settings#categories", status_code=303)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error renaming category: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fehler beim Umbenennen: {str(e)}")


@router.post("/categories/delete")
async def delete_category(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    name: str = Form(...)
):
    """Löscht eine Kategorie (setzt category auf NULL bei allen zugehörigen Ausgaben)"""
    try:
        # Validierung
        if not name:
            raise HTTPException(status_code=400, detail="Kategorienamen darf nicht leer sein")

        # Alle Ausgaben mit dieser Kategorie auf NULL setzen
        updated_count = db.query(Expense).filter(
            Expense.event_id == event_id,
            Expense.category == name
        ).update({'category': None})

        db.commit()

        logger.info(f"Deleted category '{name}' for event {event_id}, updated {updated_count} expenses")
        flash(request, f"Kategorie '{name}' wurde gelöscht ({updated_count} Ausgaben aktualisiert)", "success")
        return RedirectResponse(url="/settings#categories", status_code=303)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting category: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen: {str(e)}")


@router.post("/categories/add")
async def add_category(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    name: str = Form(...)
):
    """Fügt eine neue Kategorie hinzu (erstellt eine Dummy-Ausgabe mit dieser Kategorie)"""
    try:
        # Validierung
        if not name or not name.strip():
            raise HTTPException(status_code=400, detail="Kategorienamen darf nicht leer sein")

        name = name.strip()

        # Prüfen ob Kategorie bereits existiert
        existing = db.query(Expense).filter(
            Expense.event_id == event_id,
            Expense.category == name
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail=f"Kategorie '{name}' existiert bereits")

        # Erstelle eine Dummy-Ausgabe mit 0 EUR, um die Kategorie zu registrieren
        # Diese kann später gelöscht oder bearbeitet werden
        dummy_expense = Expense(
            event_id=event_id,
            title=f"Kategorie: {name}",
            amount=0.00,
            category=name,
            description="Automatisch erstellt zum Anlegen der Kategorie. Kann gelöscht werden.",
            is_settled=False
        )
        db.add(dummy_expense)
        db.commit()

        logger.info(f"Added new category '{name}' for event {event_id}")
        flash(request, f"Kategorie '{name}' wurde hinzugefügt", "success")
        return RedirectResponse(url="/settings#categories", status_code=303)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding category: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fehler beim Hinzufügen: {str(e)}")
