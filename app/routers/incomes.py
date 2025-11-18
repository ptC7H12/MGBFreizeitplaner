"""Router für Einnahmen (Zuschüsse, Spenden, etc.)"""
import logging
from pathlib import Path
from fastapi import APIRouter, Request, Depends, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.orm import Session, joinedload
from datetime import date as date_type
from typing import Optional

from app.database import get_db
from app.models.income import Income
from app.models.role import Role
from app.dependencies import get_current_event_id
from app.utils.flash import flash
from app.utils.file_upload import save_receipt_file, delete_receipt_file
from app.templates_config import templates

logger = logging.getLogger(__name__)

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
            # Konvertiere zu float um Decimal/float Typ-Konflikte zu vermeiden
            incomes_by_role[role_name]["total"] += float(income.amount)
        else:
            incomes_without_role.append(income)

    # Konvertiere zu float um Decimal/float Typ-Konflikte zu vermeiden
    total_income = float(sum((i.amount for i in incomes), 0))

    return templates.TemplateResponse(
        "incomes/list.html",
        {
            "request": request,
            "incomes_by_role": incomes_by_role,
            "incomes_without_role": incomes_without_role,
            "total_income": total_income,
        }
    )


@router.get("/create", response_class=HTMLResponse)
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


@router.post("/create", response_class=HTMLResponse)
async def create_income(
    request: Request,
    name: str = Form(...),
    amount: float = Form(...),
    date: date_type = Form(...),
    description: str = Form(None),
    role_id: Optional[str] = Form(None),
    receipt_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Erstellt eine neue Einnahme"""
    # Konvertiere leere Strings zu None
    role_id_int = int(role_id) if role_id and role_id.strip() else None

    # Validiere Rolle falls angegeben
    if role_id_int:
        role = db.query(Role).filter(Role.id == role_id_int, Role.event_id == event_id).first()
        if not role:
            flash(request, "Ungültige Rolle ausgewählt", "error")
            return RedirectResponse(url="/incomes/create", status_code=303)

    income = Income(
        event_id=event_id,
        name=name,
        amount=amount,
        date=date,
        description=description,
        role_id=role_id_int
    )

    db.add(income)
    db.commit()
    db.refresh(income)

    # Beleg-Upload verarbeiten (falls vorhanden)
    if receipt_file and receipt_file.filename:
        file_path, error = await save_receipt_file(
            receipt_file,
            event_id,
            income.id,
            "incomes"
        )

        if error:
            logger.warning(f"Failed to upload receipt for income {income.id}: {error}")
            flash(request, f"Einnahme erstellt, aber Beleg-Upload fehlgeschlagen: {error}", "warning")
        else:
            income.receipt_file_path = file_path
            db.commit()
            logger.info(f"Receipt uploaded for income {income.id}: {file_path}")

    flash(request, f"Einnahme '{name}' erfolgreich erstellt", "success")
    return RedirectResponse(url="/incomes", status_code=303)


@router.get("/{income_id}/edit", response_class=HTMLResponse)
async def edit_income_form(
    request: Request,
    income_id: int,
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


@router.post("/{income_id}/edit", response_class=HTMLResponse)
async def update_income(
    request: Request,
    income_id: int,
    name: str = Form(...),
    amount: float = Form(...),
    date: date_type = Form(...),
    description: str = Form(None),
    role_id: Optional[str] = Form(None),
    receipt_file: Optional[UploadFile] = File(None),
    remove_receipt: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Aktualisiert eine Einnahme"""
    income = db.query(Income).filter(Income.id == income_id, Income.event_id == event_id).first()
    if not income:
        raise HTTPException(status_code=404, detail="Einnahme nicht gefunden")

    # Konvertiere leere Strings zu None
    role_id_int = int(role_id) if role_id and role_id.strip() else None

    # Validiere Rolle falls angegeben
    if role_id_int:
        role = db.query(Role).filter(Role.id == role_id_int, Role.event_id == event_id).first()
        if not role:
            flash(request, "Ungültige Rolle ausgewählt", "error")
            return RedirectResponse(url=f"/incomes/{income_id}/edit", status_code=303)

    income.name = name
    income.amount = amount
    income.date = date
    income.description = description
    income.role_id = role_id_int

    # Beleg entfernen, falls gewünscht
    if remove_receipt == "true" and income.receipt_file_path:
        delete_receipt_file(income.receipt_file_path)
        income.receipt_file_path = None
        logger.info(f"Receipt removed from income {income_id}")

    # Neuen Beleg hochladen, falls vorhanden
    if receipt_file and receipt_file.filename:
        # Alten Beleg löschen
        if income.receipt_file_path:
            delete_receipt_file(income.receipt_file_path)

        # Neuen Beleg speichern
        file_path, error = await save_receipt_file(
            receipt_file,
            event_id,
            income.id,
            "incomes"
        )

        if error:
            logger.warning(f"Failed to upload receipt for income {income.id}: {error}")
            flash(request, f"Einnahme aktualisiert, aber Beleg-Upload fehlgeschlagen: {error}", "warning")
        else:
            income.receipt_file_path = file_path
            logger.info(f"Receipt updated for income {income.id}: {file_path}")

    db.commit()

    flash(request, f"Einnahme '{name}' erfolgreich aktualisiert", "success")
    return RedirectResponse(url="/incomes", status_code=303)


@router.get("/{income_id}/receipt/download")
async def download_income_receipt(income_id: int, db: Session = Depends(get_db), event_id: int = Depends(get_current_event_id)):
    """Lädt den Beleg einer Einnahme herunter"""
    income = db.query(Income).filter(Income.id == income_id, Income.event_id == event_id).first()

    if not income:
        raise HTTPException(status_code=404, detail="Einnahme nicht gefunden")

    if not income.receipt_file_path:
        raise HTTPException(status_code=404, detail="Kein Beleg vorhanden")

    file_path = Path(income.receipt_file_path)

    if not file_path.exists():
        logger.error(f"Receipt file not found: {income.receipt_file_path}")
        raise HTTPException(status_code=404, detail="Beleg-Datei wurde nicht gefunden")

    # MIME-Type basierend auf Dateiendung
    mime_type = "application/octet-stream"
    if file_path.suffix.lower() == '.pdf':
        mime_type = "application/pdf"
    elif file_path.suffix.lower() in ['.jpg', '.jpeg']:
        mime_type = "image/jpeg"
    elif file_path.suffix.lower() == '.png':
        mime_type = "image/png"

    logger.info(f"Downloading receipt for income {income_id}: {income.receipt_file_path}")

    return FileResponse(
        path=file_path,
        media_type=mime_type,
        filename=file_path.name
    )


@router.post("/{income_id}/delete", response_class=HTMLResponse)
async def delete_income(
    request: Request,
    income_id: int,
    db: Session = Depends(get_db),
    event_id: int = Depends(get_current_event_id)
):
    """Löscht eine Einnahme"""
    income = db.query(Income).filter(Income.id == income_id, Income.event_id == event_id).first()
    if not income:
        raise HTTPException(status_code=404, detail="Einnahme nicht gefunden")

    name = income.name

    # Beleg löschen, falls vorhanden
    if income.receipt_file_path:
        delete_receipt_file(income.receipt_file_path)
        logger.info(f"Receipt deleted for income {income_id}")

    db.delete(income)
    db.commit()

    flash(request, f"Einnahme '{name}' erfolgreich gelöscht", "success")
    return RedirectResponse(url="/incomes", status_code=303)
