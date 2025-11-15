"""Participant Service - Business-Logik für Teilnehmer"""
import logging
from io import BytesIO
from datetime import date
from typing import List, Optional
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from sqlalchemy.orm import Session

from app.models import Participant, Role, Event, Family, Ruleset
from app.services.price_calculator import PriceCalculator

logger = logging.getLogger(__name__)


class ParticipantService:
    """Service für Teilnehmer-Business-Logik"""

    @staticmethod
    def calculate_price_for_participant(
        db: Session,
        event_id: int,
        role_id: int,
        birth_date: date,
        family_id: Optional[int] = None
    ) -> float:
        """
        Berechnet den Preis für einen Teilnehmer.

        Args:
            db: Datenbank-Session
            event_id: ID des Events
            role_id: ID der Rolle
            birth_date: Geburtsdatum des Teilnehmers
            family_id: Optional - ID der Familie für Familienrabatte

        Returns:
            Berechneter Preis in Euro
        """
        # Event und Ruleset laden
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise ValueError(f"Event mit ID {event_id} nicht gefunden")

        ruleset = db.query(Ruleset).filter(Ruleset.id == event.ruleset_id).first()
        if not ruleset:
            raise ValueError(f"Ruleset für Event {event_id} nicht gefunden")

        # Rolle laden
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"Rolle mit ID {role_id} nicht gefunden")

        # Alter berechnen
        age = event.start_date.year - birth_date.year
        if (event.start_date.month, event.start_date.day) < (birth_date.month, birth_date.day):
            age -= 1

        # Position in der Familie bestimmen (für Familienrabatte)
        family_children_count = 1
        if family_id:
            family = db.query(Family).filter(Family.id == family_id).first()
            if family:
                # Anzahl aktiver Kinder in der Familie
                children_in_family = db.query(Participant).filter(
                    Participant.family_id == family_id,
                    Participant.event_id == event_id,
                    Participant.is_active == True
                ).order_by(Participant.birth_date.desc()).all()

                # Position des neuen Kindes wäre am Ende
                family_children_count = len(children_in_family) + 1

        # Preis berechnen
        return PriceCalculator.calculate_participant_price(
            age=age,
            role_name=role.name,
            ruleset_data=ruleset.rules,
            family_children_count=family_children_count
        )

    @staticmethod
    def export_to_excel(participants: List[Participant], event: Event) -> BytesIO:
        """
        Exportiert Teilnehmer als Excel-Datei.

        Args:
            participants: Liste der Teilnehmer
            event: Event-Objekt

        Returns:
            BytesIO-Stream mit Excel-Datei
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Teilnehmerliste"

        # Header definieren
        headers = [
            "Nachname", "Vorname", "Geburtsdatum", "Alter", "Geschlecht",
            "Rolle", "Familie", "E-Mail", "Telefon", "Preis (€)",
            "Bezahlt (€)", "Offen (€)", "Adresse"
        ]

        # Header-Formatierung
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True, size=11)
        header_alignment = Alignment(horizontal="center", vertical="center")

        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment

        # Spaltenbreiten setzen
        column_widths = {
            1: 20,  # Nachname
            2: 20,  # Vorname
            3: 15,  # Geburtsdatum
            4: 8,   # Alter
            5: 12,  # Geschlecht
            6: 15,  # Rolle
            7: 20,  # Familie
            8: 30,  # E-Mail
            9: 15,  # Telefon
            10: 12, # Preis
            11: 12, # Bezahlt
            12: 12, # Offen
            13: 40  # Adresse
        }

        for col_num, width in column_widths.items():
            ws.column_dimensions[ws.cell(row=1, column=col_num).column_letter].width = width

        # Daten schreiben
        for row_num, participant in enumerate(participants, 2):
            total_paid = sum(payment.amount for payment in participant.payments)
            outstanding = participant.final_price - total_paid

            ws.cell(row=row_num, column=1, value=participant.last_name)
            ws.cell(row=row_num, column=2, value=participant.first_name)
            ws.cell(row=row_num, column=3, value=participant.birth_date.strftime("%d.%m.%Y") if participant.birth_date else "")
            ws.cell(row=row_num, column=4, value=participant.age_at_event or "")
            ws.cell(row=row_num, column=5, value=participant.gender or "")
            ws.cell(row=row_num, column=6, value=participant.role.display_name if participant.role else "")
            ws.cell(row=row_num, column=7, value=participant.family.name if participant.family else "")
            ws.cell(row=row_num, column=8, value=participant.email or "")
            ws.cell(row=row_num, column=9, value=participant.phone or "")
            ws.cell(row=row_num, column=10, value=participant.final_price)
            ws.cell(row=row_num, column=11, value=total_paid)
            ws.cell(row=row_num, column=12, value=outstanding)
            ws.cell(row=row_num, column=13, value=participant.address or "")

        # Excel in Memory-Stream speichern
        excel_stream = BytesIO()
        wb.save(excel_stream)
        excel_stream.seek(0)

        return excel_stream
