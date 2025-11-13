"""Dashboard Router"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import settings
from app.database import get_db
from app.models import Participant, Payment, Expense, Event, Family
from app.dependencies import get_current_event_id

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db), event_id: int = Depends(get_current_event_id)):
    """Hauptdashboard mit Statistiken"""

    # Statistiken sammeln (gefiltert nach event_id)
    total_participants = db.query(func.count(Participant.id)).filter(Participant.event_id == event_id).scalar() or 0
    total_families = db.query(func.count(Family.id)).filter(Family.event_id == event_id).scalar() or 0

    # Finanzielle Übersicht (gefiltert nach event_id)
    total_revenue_target = db.query(func.sum(Participant.calculated_price)).filter(Participant.event_id == event_id).scalar() or 0.0
    total_payments = db.query(func.sum(Payment.amount)).filter(Payment.event_id == event_id).scalar() or 0.0
    total_expenses = db.query(func.sum(Expense.amount)).filter(Expense.event_id == event_id).scalar() or 0.0

    outstanding = total_revenue_target - total_payments
    balance = total_payments - total_expenses

    stats = {
        "total_participants": total_participants,
        "total_families": total_families,
        "total_revenue_target": total_revenue_target,
        "total_payments": total_payments,
        "total_expenses": total_expenses,
        "outstanding": outstanding,
        "balance": balance
    }

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "Dashboard", "stats": stats}
    )
