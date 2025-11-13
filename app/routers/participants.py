"""Participants (Teilnehmer) Router"""
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from app.config import settings
from app.database import get_db
from app.models import Participant, Role, Event, Family

router = APIRouter(prefix="/participants", tags=["participants"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse)
async def list_participants(request: Request, db: Session = Depends(get_db)):
    """Liste aller Teilnehmer"""
    participants = db.query(Participant).order_by(Participant.last_name).all()

    return templates.TemplateResponse(
        "participants/list.html",
        {"request": request, "title": "Teilnehmer", "participants": participants}
    )


@router.get("/create", response_class=HTMLResponse)
async def create_participant_form(request: Request, db: Session = Depends(get_db)):
    """Formular zum Erstellen eines neuen Teilnehmers"""
    roles = db.query(Role).filter(Role.is_active == True).all()
    events = db.query(Event).all()
    families = db.query(Family).order_by(Family.name).all()

    return templates.TemplateResponse(
        "participants/create.html",
        {
            "request": request,
            "title": "Neuer Teilnehmer",
            "roles": roles,
            "events": events,
            "families": families
        }
    )


@router.get("/{participant_id}", response_class=HTMLResponse)
async def view_participant(request: Request, participant_id: int, db: Session = Depends(get_db)):
    """Detailansicht eines Teilnehmers"""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()

    if not participant:
        return RedirectResponse(url="/participants", status_code=303)

    # Zahlungen des Teilnehmers
    total_paid = sum(payment.amount for payment in participant.payments)

    return templates.TemplateResponse(
        "participants/detail.html",
        {
            "request": request,
            "title": f"{participant.full_name}",
            "participant": participant,
            "total_paid": total_paid,
            "outstanding": participant.final_price - total_paid
        }
    )
