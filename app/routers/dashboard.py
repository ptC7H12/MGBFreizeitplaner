"""Dashboard Router"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import settings
from app.database import get_db
from app.models import Participant, Payment, Expense, Event, Family

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Hauptdashboard mit Statistiken"""

    # Statistiken sammeln
    total_participants = db.query(func.count(Participant.id)).scalar() or 0
    total_families = db.query(func.count(Family.id)).scalar() or 0
    total_events = db.query(func.count(Event.id)).scalar() or 0

    # Finanzielle Übersicht
    total_revenue_target = db.query(func.sum(Participant.calculated_price)).scalar() or 0.0
    total_payments = db.query(func.sum(Payment.amount)).scalar() or 0.0
    total_expenses = db.query(func.sum(Expense.amount)).scalar() or 0.0

    outstanding = total_revenue_target - total_payments
    balance = total_payments - total_expenses

    stats = {
        "total_participants": total_participants,
        "total_families": total_families,
        "total_events": total_events,
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
