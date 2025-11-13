"""Rulesets (Regelwerke) Router"""
from fastapi import APIRouter, Request, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import httpx
import tempfile
from pathlib import Path

from app.config import settings
from app.database import get_db
from app.models import Ruleset, Event
from app.services.ruleset_parser import RulesetParser
from app.dependencies import get_current_event_id

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
