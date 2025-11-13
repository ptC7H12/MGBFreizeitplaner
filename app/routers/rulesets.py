"""Rulesets (Regelwerke) Router"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Ruleset

router = APIRouter(prefix="/rulesets", tags=["rulesets"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse)
async def list_rulesets(request: Request, db: Session = Depends(get_db)):
    """Liste aller Regelwerke"""
    rulesets = db.query(Ruleset).order_by(Ruleset.valid_from.desc()).all()

    return templates.TemplateResponse(
        "rulesets/list.html",
        {"request": request, "title": "Regelwerke", "rulesets": rulesets}
    )


@router.get("/{ruleset_id}", response_class=HTMLResponse)
async def view_ruleset(request: Request, ruleset_id: int, db: Session = Depends(get_db)):
    """Detailansicht eines Regelwerks"""
    ruleset = db.query(Ruleset).filter(Ruleset.id == ruleset_id).first()

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
