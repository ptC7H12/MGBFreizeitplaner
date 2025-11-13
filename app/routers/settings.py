"""Settings (Einstellungen) Router"""
import logging
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
from typing import Optional
from pydantic import ValidationError

from app.config import settings
from app.database import get_db
from app.models import Setting, Event, Ruleset
from app.dependencies import get_current_event_id
from app.utils.error_handler import handle_db_exception
from app.utils.flash import flash
from app.schemas import SettingUpdateSchema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse)
async def view_settings(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Zeigt die Einstellungen für das aktuelle Event"""
    # Einstellungen für das Event laden (oder Standard-Einstellungen erstellen)
    setting = db.query(Setting).filter(Setting.event_id == event_id).first()

    if not setting:
        # Keine Einstellungen vorhanden -> Standard-Einstellungen erstellen
        setting = Setting(event_id=event_id)
        db.add(setting)
        db.commit()
        db.refresh(setting)
        logger.info(f"Created default settings for event {event_id}")

    event = db.query(Event).filter(Event.id == event_id).first()

    # Alle Rulesets für Dropdown
    rulesets = db.query(Ruleset).filter(Ruleset.event_id == event_id).order_by(Ruleset.valid_from.desc()).all()

    return templates.TemplateResponse(
        "settings/view.html",
        {
            "request": request,
            "title": "Einstellungen",
            "setting": setting,
            "event": event,
            "rulesets": rulesets
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
    setting = db.query(Setting).filter(Setting.event_id == event_id).first()

    if not setting:
        # Keine Einstellungen vorhanden -> Standard-Einstellungen erstellen
        setting = Setting(event_id=event_id)
        db.add(setting)
        db.commit()
        db.refresh(setting)
        logger.info(f"Created default settings for event {event_id}")

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
    invoice_footer_text: Optional[str] = Form(None)
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
            invoice_footer_text=invoice_footer_text
        )

        # Einstellungen aktualisieren
        setting.organization_name = setting_data.organization_name
        setting.organization_address = setting_data.organization_address
        setting.bank_account_holder = setting_data.bank_account_holder
        setting.bank_iban = setting_data.bank_iban
        setting.bank_bic = setting_data.bank_bic
        setting.invoice_subject_prefix = setting_data.invoice_subject_prefix if setting_data.invoice_subject_prefix else "Teilnahme an"
        setting.invoice_footer_text = setting_data.invoice_footer_text if setting_data.invoice_footer_text else "Vielen Dank für Ihre Zahlung!"

        db.commit()

        flash(request, "Einstellungen wurden erfolgreich aktualisiert", "success")
        return RedirectResponse(url="/settings", status_code=303)

    except ValidationError as e:
        # Pydantic-Validierungsfehler
        logger.warning(f"Validation error updating settings: {e}", exc_info=True)
        first_error = e.errors()[0]
        field_name = first_error['loc'][0] if first_error['loc'] else 'Unbekannt'
        error_msg = first_error['msg']
        flash(request, f"Validierungsfehler ({field_name}): {error_msg}", "error")
        return RedirectResponse(url="/settings/edit?error=validation", status_code=303)

    except ValueError as e:
        logger.warning(f"Invalid input for settings update: {e}", exc_info=True)
        flash(request, f"Ungültige Eingabe: {str(e)}", "error")
        return RedirectResponse(url="/settings/edit?error=invalid_input", status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error updating settings: {e}", exc_info=True)
        flash(request, "Einstellungen konnten nicht aktualisiert werden (Datenbankfehler)", "error")
        return RedirectResponse(url="/settings/edit?error=db_integrity", status_code=303)

    except DataError as e:
        db.rollback()
        logger.error(f"Invalid data updating settings: {e}", exc_info=True)
        flash(request, "Ungültige Daten eingegeben", "error")
        return RedirectResponse(url="/settings/edit?error=invalid_data", status_code=303)

    except Exception as e:
        return handle_db_exception(e, "/settings/edit", "Updating settings", db, request)
