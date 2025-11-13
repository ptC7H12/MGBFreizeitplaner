"""Families (Familien) Router"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Family, Participant

router = APIRouter(prefix="/families", tags=["families"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse)
async def list_families(request: Request, db: Session = Depends(get_db)):
    """Liste aller Familien"""
    families = db.query(Family).order_by(Family.name).all()

    # Für jede Familie: Anzahl Teilnehmer und Gesamtpreis berechnen
    family_data = []
    for family in families:
        total_price = sum(p.final_price for p in family.participants)
        total_paid = sum(payment.amount for payment in family.payments)

        family_data.append({
            "family": family,
            "participant_count": len(family.participants),
            "total_price": total_price,
            "total_paid": total_paid,
            "outstanding": total_price - total_paid
        })

    return templates.TemplateResponse(
        "families/list.html",
        {"request": request, "title": "Familien", "family_data": family_data}
    )


@router.get("/{family_id}", response_class=HTMLResponse)
async def view_family(request: Request, family_id: int, db: Session = Depends(get_db)):
    """Detailansicht einer Familie"""
    family = db.query(Family).filter(Family.id == family_id).first()

    if not family:
        return RedirectResponse(url="/families", status_code=303)

    # Finanzielle Übersicht
    total_price = sum(p.final_price for p in family.participants)
    total_paid = sum(payment.amount for payment in family.payments)

    return templates.TemplateResponse(
        "families/detail.html",
        {
            "request": request,
            "title": f"Familie {family.name}",
            "family": family,
            "total_price": total_price,
            "total_paid": total_paid,
            "outstanding": total_price - total_paid
        }
    )
