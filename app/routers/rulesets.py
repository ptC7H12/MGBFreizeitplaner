"""Rulesets (Regelwerke) Router"""
import logging
from fastapi import APIRouter, Request, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
from datetime import datetime
from typing import Optional
import httpx
import tempfile
from pathlib import Path

from app.config import settings
from app.database import get_db
from app.models import Ruleset, Event
from app.services.ruleset_parser import RulesetParser
from app.services.role_manager import RoleManager
from app.services.ruleset_scanner import RulesetScanner
from app.dependencies import get_current_event_id
from app.utils.error_handler import handle_db_exception
from app.utils.flash import flash

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rulesets", tags=["rulesets"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse)
async def list_rulesets(request: Request, db: Session = Depends(get_db), event_id: int = Depends(get_current_event_id)):
    """Liste aller Regelwerke"""
    rulesets = db.query(Ruleset).filter(Ruleset.event_id == event_id).order_by(Ruleset.valid_from.desc()).all()

    return templates.TemplateResponse(
        "rulesets/list.html",
        {"request": request, "title": "Regelwerke", "rulesets": rulesets}
    )


@router.get("/import", response_class=HTMLResponse)
async def import_ruleset_form(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    error: Optional[str] = None,
    success: Optional[str] = None
):
    """Formular zum Importieren eines Regelwerks"""
    event = db.query(Event).filter(Event.id == event_id).first()

    return templates.TemplateResponse(
        "rulesets/import.html",
        {
            "request": request,
            "title": "Regelwerk importieren",
            "event": event,
            "error": error,
            "success": success
        }
    )


@router.get("/import/scan", response_class=HTMLResponse)
async def scan_rulesets_directory(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Scannt Verzeichnisse nach Regelwerk-Dateien und zeigt eine Auswahlliste"""
    event = db.query(Event).filter(Event.id == event_id).first()

    # Scanne alle konfigurierten Verzeichnisse
    all_rulesets = RulesetScanner.scan_all_default_directories()

    # Zähle gefundene Rulesets
    total_rulesets = sum(len(rulesets) for rulesets in all_rulesets.values())
    valid_rulesets_count = sum(
        len(RulesetScanner.filter_valid_rulesets(rulesets))
        for rulesets in all_rulesets.values()
    )

    return templates.TemplateResponse(
        "rulesets/scan.html",
        {
            "request": request,
            "title": "Regelwerke aus Verzeichnis auswählen",
            "event": event,
            "all_rulesets": all_rulesets,
            "total_rulesets": total_rulesets,
            "valid_rulesets_count": valid_rulesets_count
        }
    )


@router.post("/import/from-file", response_class=HTMLResponse)
async def import_ruleset_from_file(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    file_path: str = Form(...)
):
    """Importiert ein Regelwerk aus einer gescannten Datei"""
    try:
        # Datei einlesen
        yaml_file = Path(file_path)
        if not yaml_file.exists():
            flash(request, f"Datei nicht gefunden: {file_path}", "error")
            return RedirectResponse(url="/rulesets/import/scan", status_code=303)

        # YAML parsen
        parser = RulesetParser()
        data = parser.parse_yaml_file(yaml_file)

        # Validieren
        is_valid, error_msg = parser.validate_ruleset(data)
        if not is_valid:
            flash(request, f"Ungültiges Regelwerk: {error_msg}", "error")
            return RedirectResponse(url="/rulesets/import/scan", status_code=303)

        # Regelwerk in Datenbank speichern
        ruleset = Ruleset(
            name=data["name"],
            ruleset_type=data["type"],
            description=data.get("description"),
            valid_from=datetime.strptime(data["valid_from"], "%Y-%m-%d").date(),
            valid_until=datetime.strptime(data["valid_until"], "%Y-%m-%d").date(),
            age_groups=data["age_groups"],
            role_discounts=data.get("role_discounts"),
            family_discount=data.get("family_discount"),
            source_file=str(yaml_file),
            event_id=event_id
        )

        db.add(ruleset)
        db.commit()
        db.refresh(ruleset)

        # Rollen automatisch aus role_discounts erstellen
        if data.get("role_discounts"):
            RoleManager.create_roles_from_ruleset(db, event_id, data.get("role_discounts"))
            flash(request, f"Regelwerk '{data['name']}' importiert und {len(data.get('role_discounts'))} Rollen erstellt", "success")
        else:
            flash(request, f"Regelwerk '{data['name']}' erfolgreich importiert", "success")

        return RedirectResponse(url=f"/rulesets/{ruleset.id}", status_code=303)

    except Exception as e:
        logger.error(f"Error importing ruleset from file: {e}")
        db.rollback()
        flash(request, f"Fehler beim Import: {str(e)}", "error")
        return RedirectResponse(url="/rulesets/import/scan", status_code=303)


@router.post("/import/upload", response_class=HTMLResponse)
async def import_ruleset_upload(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    file: UploadFile = File(...)
):
    """Importiert ein Regelwerk aus einer hochgeladenen YAML-Datei"""
    try:
        # Datei-Inhalt lesen
        content = await file.read()
        yaml_string = content.decode('utf-8')

        # YAML parsen
        parser = RulesetParser()
        data = parser.parse_yaml_string(yaml_string)

        # Validieren
        is_valid, error_msg = parser.validate_ruleset(data)
        if not is_valid:
            return RedirectResponse(
                url=f"/rulesets/import?error={error_msg}",
                status_code=303
            )

        # Regelwerk in Datenbank speichern
        ruleset = Ruleset(
            name=data["name"],
            ruleset_type=data["type"],
            description=data.get("description"),
            valid_from=datetime.strptime(data["valid_from"], "%Y-%m-%d").date(),
            valid_until=datetime.strptime(data["valid_until"], "%Y-%m-%d").date(),
            age_groups=data["age_groups"],
            role_discounts=data.get("role_discounts"),
            family_discount=data.get("family_discount"),
            source_file=file.filename,
            event_id=event_id
        )

        db.add(ruleset)
        db.commit()
        db.refresh(ruleset)

        # Rollen automatisch aus role_discounts erstellen
        if data.get("role_discounts"):
            RoleManager.create_roles_from_ruleset(db, event_id, data.get("role_discounts"))
            flash(request, f"Regelwerk importiert und {len(data.get('role_discounts'))} Rollen erstellt", "success")
        else:
            flash(request, "Regelwerk erfolgreich importiert", "success")

        return RedirectResponse(url=f"/rulesets/{ruleset.id}", status_code=303)

    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/rulesets/import?error=Fehler beim Import: {str(e)}",
            status_code=303
        )


@router.post("/import/github", response_class=HTMLResponse)
async def import_ruleset_github(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    github_url: str = Form(...)
):
    """Importiert ein Regelwerk von einer GitHub-URL"""
    try:
        # URL validieren
        if not github_url.startswith("https://"):
            return RedirectResponse(
                url="/rulesets/import?error=Ungültige URL. Bitte HTTPS verwenden.",
                status_code=303
            )

        # GitHub-URLs automatisch zu Raw-URLs konvertieren
        # Von: https://github.com/user/repo/blob/branch/path/file.yaml
        # Zu: https://raw.githubusercontent.com/user/repo/branch/path/file.yaml
        if "github.com" in github_url and "/blob/" in github_url:
            github_url = github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

        # YAML-Datei von GitHub herunterladen
        async with httpx.AsyncClient() as client:
            response = await client.get(github_url, timeout=10.0)
            response.raise_for_status()
            yaml_string = response.text

        # YAML parsen
        parser = RulesetParser()
        data = parser.parse_yaml_string(yaml_string)

        # Validieren
        is_valid, error_msg = parser.validate_ruleset(data)
        if not is_valid:
            return RedirectResponse(
                url=f"/rulesets/import?error={error_msg}",
                status_code=303
            )

        # Regelwerk in Datenbank speichern
        ruleset = Ruleset(
            name=data["name"],
            ruleset_type=data["type"],
            description=data.get("description"),
            valid_from=datetime.strptime(data["valid_from"], "%Y-%m-%d").date(),
            valid_until=datetime.strptime(data["valid_until"], "%Y-%m-%d").date(),
            age_groups=data["age_groups"],
            role_discounts=data.get("role_discounts"),
            family_discount=data.get("family_discount"),
            source_file=github_url,
            event_id=event_id
        )

        db.add(ruleset)
        db.commit()
        db.refresh(ruleset)

        # Rollen automatisch aus role_discounts erstellen
        if data.get("role_discounts"):
            RoleManager.create_roles_from_ruleset(db, event_id, data.get("role_discounts"))
            flash(request, f"Regelwerk von GitHub importiert und {len(data.get('role_discounts'))} Rollen erstellt", "success")
        else:
            flash(request, "Regelwerk erfolgreich von GitHub importiert", "success")

        return RedirectResponse(url=f"/rulesets/{ruleset.id}", status_code=303)

    except httpx.HTTPError as e:
        return RedirectResponse(
            url=f"/rulesets/import?error=Fehler beim Herunterladen: {str(e)}",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/rulesets/import?error=Fehler beim Import: {str(e)}",
            status_code=303
        )


@router.post("/import/manual", response_class=HTMLResponse)
async def import_ruleset_manual(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    yaml_content: str = Form(...)
):
    """Importiert ein Regelwerk aus manuell eingegebenem YAML"""
    try:
        # YAML parsen
        parser = RulesetParser()
        data = parser.parse_yaml_string(yaml_content)

        # Validieren
        is_valid, error_msg = parser.validate_ruleset(data)
        if not is_valid:
            return RedirectResponse(
                url=f"/rulesets/import?error={error_msg}",
                status_code=303
            )

        # Regelwerk in Datenbank speichern
        ruleset = Ruleset(
            name=data["name"],
            ruleset_type=data["type"],
            description=data.get("description"),
            valid_from=datetime.strptime(data["valid_from"], "%Y-%m-%d").date(),
            valid_until=datetime.strptime(data["valid_until"], "%Y-%m-%d").date(),
            age_groups=data["age_groups"],
            role_discounts=data.get("role_discounts"),
            family_discount=data.get("family_discount"),
            source_file="manual_input",
            event_id=event_id
        )

        db.add(ruleset)
        db.commit()
        db.refresh(ruleset)

        # Rollen automatisch aus role_discounts erstellen
        if data.get("role_discounts"):
            RoleManager.create_roles_from_ruleset(db, event_id, data.get("role_discounts"))
            flash(request, f"Regelwerk manuell importiert und {len(data.get('role_discounts'))} Rollen erstellt", "success")
        else:
            flash(request, "Regelwerk erfolgreich manuell importiert", "success")

        return RedirectResponse(url=f"/rulesets/{ruleset.id}", status_code=303)

    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/rulesets/import?error=Fehler beim Import: {str(e)}",
            status_code=303
        )


@router.get("/{ruleset_id}", response_class=HTMLResponse)
async def view_ruleset(
    request: Request,
    ruleset_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Detailansicht eines Regelwerks"""
    ruleset = db.query(Ruleset).filter(
        Ruleset.id == ruleset_id,
        Ruleset.event_id == event_id
    ).first()

    if not ruleset:
        return RedirectResponse(url="/rulesets", status_code=303)

    return templates.TemplateResponse(
        "rulesets/detail.html",
        {
            "request": request,
            "title": f"Regelwerk: {ruleset.name}",
            "ruleset": ruleset
        }
    )


@router.get("/{ruleset_id}/export", response_class=Response)
async def export_ruleset(
    ruleset_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Exportiert ein Regelwerk als YAML-Datei"""
    ruleset = db.query(Ruleset).filter(
        Ruleset.id == ruleset_id,
        Ruleset.event_id == event_id
    ).first()

    if not ruleset:
        raise HTTPException(status_code=404, detail="Regelwerk nicht gefunden")

    # Regelwerk als YAML exportieren
    parser = RulesetParser()
    yaml_content = parser.export_ruleset_to_yaml(ruleset)

    # Dateinamen erstellen
    filename = f"{ruleset.name.replace(' ', '_')}_{ruleset.valid_from.strftime('%Y-%m-%d')}.yaml"

    # Als Download zurückgeben
    return Response(
        content=yaml_content.encode('utf-8'),
        media_type="application/x-yaml",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/{ruleset_id}/edit", response_class=HTMLResponse)
async def edit_ruleset_form(
    request: Request,
    ruleset_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Formular zum Bearbeiten eines Regelwerks"""
    ruleset = db.query(Ruleset).filter(
        Ruleset.id == ruleset_id,
        Ruleset.event_id == event_id
    ).first()

    if not ruleset:
        return RedirectResponse(url="/rulesets", status_code=303)

    # Regelwerk als YAML exportieren für Bearbeitung
    parser = RulesetParser()
    yaml_content = parser.export_ruleset_to_yaml(ruleset)

    event = db.query(Event).filter(Event.id == event_id).first()

    return templates.TemplateResponse(
        "rulesets/edit.html",
        {
            "request": request,
            "title": f"Regelwerk bearbeiten: {ruleset.name}",
            "ruleset": ruleset,
            "yaml_content": yaml_content,
            "event": event
        }
    )


@router.post("/{ruleset_id}/edit", response_class=HTMLResponse)
async def update_ruleset(
    request: Request,
    ruleset_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id),
    yaml_content: str = Form(...)
):
    """Aktualisiert ein Regelwerk aus bearbeitetem YAML"""
    ruleset = db.query(Ruleset).filter(
        Ruleset.id == ruleset_id,
        Ruleset.event_id == event_id
    ).first()

    if not ruleset:
        flash(request, "Regelwerk nicht gefunden", "error")
        return RedirectResponse(url="/rulesets", status_code=303)

    try:
        # YAML parsen
        parser = RulesetParser()
        data = parser.parse_yaml_string(yaml_content)

        # Validieren
        is_valid, error_msg = parser.validate_ruleset(data)
        if not is_valid:
            logger.warning(f"Invalid YAML for ruleset update: {error_msg}")
            flash(request, f"Ungültiges YAML: {error_msg}", "error")
            return RedirectResponse(url=f"/rulesets/{ruleset_id}/edit?error=invalid_yaml", status_code=303)

        # Regelwerk aktualisieren
        ruleset.name = data["name"]
        ruleset.ruleset_type = data["type"]
        ruleset.description = data.get("description")
        ruleset.valid_from = datetime.strptime(data["valid_from"], "%Y-%m-%d").date()
        ruleset.valid_until = datetime.strptime(data["valid_until"], "%Y-%m-%d").date()
        ruleset.age_groups = data["age_groups"]
        ruleset.role_discounts = data.get("role_discounts")
        ruleset.family_discount = data.get("family_discount")

        db.commit()

        flash(request, f"Regelwerk '{ruleset.name}' wurde erfolgreich aktualisiert", "success")
        return RedirectResponse(url=f"/rulesets/{ruleset_id}", status_code=303)

    except ValueError as e:
        logger.warning(f"Invalid date format in ruleset update: {e}", exc_info=True)
        flash(request, f"Ungültiges Datumsformat: {str(e)}", "error")
        return RedirectResponse(url=f"/rulesets/{ruleset_id}/edit?error=invalid_date", status_code=303)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error updating ruleset: {e}", exc_info=True)
        flash(request, "Regelwerk konnte nicht aktualisiert werden (Datenbankfehler)", "error")
        return RedirectResponse(url=f"/rulesets/{ruleset_id}/edit?error=db_integrity", status_code=303)

    except DataError as e:
        db.rollback()
        logger.error(f"Invalid data updating ruleset: {e}", exc_info=True)
        flash(request, "Ungültige Daten", "error")
        return RedirectResponse(url=f"/rulesets/{ruleset_id}/edit?error=invalid_data", status_code=303)

    except Exception as e:
        return handle_db_exception(e, f"/rulesets/{ruleset_id}/edit", "Updating ruleset", db, request)


@router.post("/{ruleset_id}/toggle")
async def toggle_ruleset(
    ruleset_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Aktiviert/Deaktiviert ein Regelwerk"""
    ruleset = db.query(Ruleset).filter(
        Ruleset.id == ruleset_id,
        Ruleset.event_id == event_id
    ).first()

    if not ruleset:
        raise HTTPException(status_code=404, detail="Regelwerk nicht gefunden")

    try:
        ruleset.is_active = not ruleset.is_active
        db.commit()
        return RedirectResponse(url=f"/rulesets/{ruleset_id}", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Aktualisieren")


@router.post("/{ruleset_id}/delete")
async def delete_ruleset(
    ruleset_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Löscht ein Regelwerk"""
    ruleset = db.query(Ruleset).filter(
        Ruleset.id == ruleset_id,
        Ruleset.event_id == event_id
    ).first()

    if not ruleset:
        raise HTTPException(status_code=404, detail="Regelwerk nicht gefunden")

    try:
        db.delete(ruleset)
        db.commit()
        return RedirectResponse(url="/rulesets", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Löschen")
