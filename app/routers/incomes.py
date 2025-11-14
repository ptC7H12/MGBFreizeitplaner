"""Router für Einnahmen (Zuschüsse, Spenden, etc.)"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from datetime import date as date_type

from app.database import get_db
from app.models.income import Income
from app.models.role import Role
from app.dependencies import get_current_event_id
from app.utils.flash import flash
from app.templates_config import templates

router = APIRouter(prefix="/incomes", tags=["incomes"])


@router.get("/", response_class=HTMLResponse)
async def list_incomes(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Liste aller Einnahmen für das aktuelle Event"""
    # Eager Loading um N+1 Query Problem zu vermeiden
    incomes = db.query(Income)\
        .filter(Income.event_id == event_id)\
        .options(joinedload(Income.role))\
        .order_by(Income.date.desc())\
        .all()

    # Gruppiere nach Rolle falls vorhanden
    incomes_by_role = {}
    incomes_without_role = []

    for income in incomes:
        if income.role_id:
            role_name = income.role.display_name
            if role_name not in incomes_by_role:
                incomes_by_role[role_name] = {"role": income.role, "incomes": [], "total": 0.0}
            incomes_by_role[role_name]["incomes"].append(income)
            incomes_by_role[role_name]["total"] += income.amount
        else:
            incomes_without_role.append(income)

    total_income = sum(i.amount for i in incomes)

    return templates.TemplateResponse(
        "incomes/list.html",
        {
            "request": request,
            "incomes_by_role": incomes_by_role,
            "incomes_without_role": incomes_without_role,
            "total_income": total_income,
        }
    )


@router.get("/new", response_class=HTMLResponse)
async def new_income_form(
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Formular für neue Einnahme"""
    roles = db.query(Role).filter(Role.event_id == event_id, Role.is_active == True).all()

    return templates.TemplateResponse(
        "incomes/form.html",
        {
            "request": request,
            "income": None,
            "roles": roles,
        }
    )


@router.post("/new")
async def create_income(
    request: Request,
    name: str = Form(...),
    amount: float = Form(...),
    date: date_type = Form(...),
    description: str = Form(None),
    role_id: int = Form(None),
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Erstellt eine neue Einnahme"""
    # Validiere Rolle falls angegeben
    if role_id:
        role = db.query(Role).filter(Role.id == role_id, Role.event_id == event_id).first()
        if not role:
            flash(request, "Ungültige Rolle ausgewählt", "error")
            return RedirectResponse(url="/incomes/new", status_code=303)

    income = Income(
        event_id=event_id,
        name=name,
        amount=amount,
        date=date,
        description=description,
        role_id=role_id if role_id else None
    )

    db.add(income)
    db.commit()

    flash(request, f"Einnahme '{name}' erfolgreich erstellt", "success")
    return RedirectResponse(url="/incomes", status_code=303)


@router.get("/{income_id}/edit", response_class=HTMLResponse)
async def edit_income_form(
    income_id: int,
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Formular zum Bearbeiten einer Einnahme"""
    income = db.query(Income).filter(Income.id == income_id, Income.event_id == event_id).first()
    if not income:
        raise HTTPException(status_code=404, detail="Einnahme nicht gefunden")

    roles = db.query(Role).filter(Role.event_id == event_id, Role.is_active == True).all()

    return templates.TemplateResponse(
        "incomes/form.html",
        {
            "request": request,
            "income": income,
            "roles": roles,
        }
    )


@router.post("/{income_id}/edit")
async def update_income(
    income_id: int,
    request: Request,
    name: str = Form(...),
    amount: float = Form(...),
    date: date_type = Form(...),
    description: str = Form(None),
    role_id: int = Form(None),
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Aktualisiert eine Einnahme"""
    income = db.query(Income).filter(Income.id == income_id, Income.event_id == event_id).first()
    if not income:
        raise HTTPException(status_code=404, detail="Einnahme nicht gefunden")

    # Validiere Rolle falls angegeben
    if role_id:
        role = db.query(Role).filter(Role.id == role_id, Role.event_id == event_id).first()
        if not role:
            flash(request, "Ungültige Rolle ausgewählt", "error")
            return RedirectResponse(url=f"/incomes/{income_id}/edit", status_code=303)

    income.name = name
    income.amount = amount
    income.date = date
    income.description = description
    income.role_id = role_id if role_id else None

    db.commit()

    flash(request, f"Einnahme '{name}' erfolgreich aktualisiert", "success")
    return RedirectResponse(url="/incomes", status_code=303)


@router.post("/{income_id}/delete")
async def delete_income(
    income_id: int,
    request: Request,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Löscht eine Einnahme"""
    income = db.query(Income).filter(Income.id == income_id, Income.event_id == event_id).first()
    if not income:
        raise HTTPException(status_code=404, detail="Einnahme nicht gefunden")

    name = income.name
    db.delete(income)
    db.commit()

    flash(request, f"Einnahme '{name}' erfolgreich gelöscht", "success")
    return RedirectResponse(url="/incomes", status_code=303)
