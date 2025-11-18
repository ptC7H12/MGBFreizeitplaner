"""Invoice (Rechnung) Generator Service"""
import logging
from io import BytesIO
from datetime import datetime, date
from typing import List, Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
from app.services.qrcode_service import QRCodeService

logger = logging.getLogger(__name__)


class InvoiceGenerator:
    """Service für die Generierung von PDF-Rechnungen"""

    def __init__(self, db: Session):
        self.pagesize = A4
        self.width, self.height = self.pagesize
        self.db = db

    def _get_settings(self, event_id: int):
        """
        Lädt die Einstellungen für ein Event oder erstellt Standard-Einstellungen

        Args:
            event_id: ID des Events

        Returns:
            Setting-Objekt
        """
        from app.models import Setting

        setting = self.db.query(Setting).filter(Setting.event_id == event_id).first()

        if not setting:
            # Keine Einstellungen vorhanden -> Standard-Einstellungen verwenden
            setting = Setting(event_id=event_id)
            # Nicht in DB speichern, nur Standard-Werte verwenden

        return setting

    def _calculate_price_breakdown(self, participant) -> Dict[str, Any]:
        """
        Berechnet die detaillierte Preis-Aufschlüsselung für einen Teilnehmer
        Verwendet PriceCalculator um Code-Duplikation zu vermeiden

        Args:
            participant: Participant-Objekt

        Returns:
            Dictionary mit Preis-Details
        """
        from app.models import Ruleset, Participant
        from app.services.price_calculator import PriceCalculator

        # Aktives Regelwerk finden
        ruleset = self.db.query(Ruleset).filter(
            Ruleset.is_active == True,
            Ruleset.valid_from <= participant.event.start_date,
            Ruleset.valid_until >= participant.event.start_date
        ).first()

        if not ruleset:
            # Kein Regelwerk vorhanden - Minimales Breakdown zurückgeben
            return {
                'base_price': 0.0,
                'role_discount_percent': 0.0,
                'role_discount_amount': 0.0,
                'price_after_role_discount': 0.0,
                'family_discount_percent': 0.0,
                'family_discount_amount': 0.0,
                'price_after_family_discount': 0.0,
                'manual_discount_percent': participant.discount_percent,
                'manual_discount_amount': 0.0,
                'manual_price_override': participant.manual_price_override,
                'final_price': participant.final_price,
                'has_discounts': False,
                'discount_reasons': []
            }

        # Ruleset-Daten vorbereiten
        ruleset_data = {
            'age_groups': ruleset.age_groups or [],
            'role_discounts': ruleset.role_discounts or {},
            'family_discount': ruleset.family_discount or {}
        }

        # Position in Familie ermitteln
        family_position = 1
        if participant.family_id:
            siblings = self.db.query(Participant).filter(
                Participant.family_id == participant.family_id,
                Participant.is_active == True
            ).order_by(Participant.birth_date).all()
            family_position = next((i + 1 for i, p in enumerate(siblings) if p.id == participant.id), 1)

        # PriceCalculator verwenden für konsistente Berechnung
        breakdown = PriceCalculator.calculate_participant_price_with_breakdown(
            age=participant.age_at_event,
            role_name=participant.role.name if participant.role else None,
            role_display_name=participant.role.display_name if participant.role else None,
            ruleset_data=ruleset_data,
            family_children_count=family_position,
            discount_percent=participant.discount_percent,
            discount_reason=participant.discount_reason,
            manual_price_override=participant.manual_price_override
        )

        return breakdown

    def generate_participant_invoice(self, participant) -> bytes:
        """
        Generiert eine Einzelrechnung für einen Teilnehmer

        Args:
            participant: Participant-Objekt mit allen Daten

        Returns:
            PDF als bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=self.pagesize, topMargin=2*cm)
        story = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
        )
        heading_style = styles['Heading2']
        normal_style = styles['Normal']

        # Einstellungen laden
        settings = self._get_settings(participant.event_id)

        # Absender/Organisation
        story.append(Paragraph(settings.organization_name, title_style))
        if settings.organization_address:
            # Adresse aufbereiten (Zeilenumbrüche durch • ersetzen für kompakte Anzeige)
            address_compact = settings.organization_address.replace('\n', ' • ')
            story.append(Paragraph(address_compact, normal_style))
        story.append(Spacer(1, 0.5*cm))

        # Rechnungsnummer und Datum
        invoice_number = f"R-{participant.id:06d}-{datetime.now().year}"
        invoice_date = datetime.now().strftime("%d.%m.%Y")

        # QR-Code für SEPA-Zahlung vorbereiten (falls offen)
        # Konvertiere zu float um Decimal/float Typ-Konflikte zu vermeiden
        total_paid = float(sum((payment.amount for payment in participant.payments), 0))
        outstanding = float(participant.final_price) - total_paid
        qr_image = None

        # Verwendungszweck: Präfix + Teilnehmername
        subject_prefix = settings.invoice_subject_prefix or "Teilnahmegebühr"
        payment_reference = f"{subject_prefix} {participant.full_name}"

        if outstanding > 0:
            try:
                qr_code_bytes = QRCodeService.generate_sepa_qr_code(
                    recipient_name=settings.bank_account_holder,
                    iban=settings.bank_iban,
                    amount=outstanding,
                    purpose=payment_reference,
                    bic=settings.bank_bic
                )
                qr_image = Image(BytesIO(qr_code_bytes), width=3.5*cm, height=3.5*cm)
            except Exception as e:
                print(f"Warnung: QR-Code konnte nicht generiert werden: {e}")

        # Info-Tabelle links, QR-Code rechts
        if qr_image:
            # Info und QR-Code in einer Tabelle nebeneinander
            info_data = [
                ["Rechnungsnummer:", invoice_number, qr_image],
                ["Rechnungsdatum:", invoice_date, ""],
                ["Teilnehmer-ID:", str(participant.id), ""]
            ]
            info_table = Table(info_data, colWidths=[5*cm, 6*cm, 4*cm])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('VALIGN', (2, 0), (2, 0), 'MIDDLE'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (1, -1), 5),
                ('SPAN', (2, 0), (2, 2)),  # QR-Code über alle 3 Zeilen spannen
            ]))
        else:
            info_data = [
                ["Rechnungsnummer:", invoice_number],
                ["Rechnungsdatum:", invoice_date],
                ["Teilnehmer-ID:", str(participant.id)]
            ]
            info_table = Table(info_data, colWidths=[5*cm, 6*cm])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))

        story.append(info_table)
        story.append(Spacer(1, 1*cm))

        # Empfänger
        story.append(Paragraph("Rechnung für:", heading_style))
        recipient_text = f"{participant.full_name}<br/>"
        if participant.address:
            recipient_text += participant.address.replace('\n', '<br/>')
        story.append(Paragraph(recipient_text, normal_style))
        story.append(Spacer(1, 1*cm))

        # Betreff (für Rechnung - nicht für Überweisung)
        subject_prefix_display = settings.invoice_subject_prefix or "Teilnahme an"
        story.append(Paragraph(f"{subject_prefix_display}: {participant.event.name}", heading_style))
        story.append(Spacer(1, 0.5*cm))

        # Preis-Aufschlüsselung berechnen
        breakdown = self._calculate_price_breakdown(participant)

        # Positions-Tabelle (ohne Menge und Einzelpreis für kompaktere Darstellung)
        positions_data = [
            ["Pos.", "Beschreibung", "Gesamtpreis"]
        ]

        # Position: Teilnahmegebühr
        description = f"<b>Teilnahmegebühr {participant.event.name}</b>\n"
        description += f"Zeitraum: {participant.event.start_date.strftime('%d.%m.%Y')} - {participant.event.end_date.strftime('%d.%m.%Y')}\n"
        description += f"Teilnehmer: {participant.full_name} ({participant.age_at_event} Jahre)\n"
        if participant.role:
            description += f"Rolle: {participant.role.display_name}\n"

        # Rabatt-Details hinzufügen
        if breakdown['has_discounts']:
            description += "\n<b>Preisberechnung:</b>\n"
            if breakdown['manual_price_override'] is None:
                # Normale Berechnung
                description += f"• Basispreis (Altersgruppe): {breakdown['base_price']:.2f} €\n"
                if breakdown['role_discount_percent'] > 0:
                    role_name = participant.role.display_name if participant.role else "Rolle"
                    description += f"• Rollenrabatt ({role_name}): -{breakdown['role_discount_percent']:.0f}% (-{breakdown['role_discount_amount']:.2f} €)\n"
                    description += f"  → Nach Rollenrabatt: {breakdown['price_after_role_discount']:.2f} €\n"
                if breakdown['family_discount_percent'] > 0:
                    description += f"• Familienrabatt: -{breakdown['family_discount_percent']:.0f}% (-{breakdown['family_discount_amount']:.2f} €)\n"
                    description += f"  → Nach Familienrabatt: {breakdown['price_after_family_discount']:.2f} €\n"
                if breakdown['manual_discount_percent'] > 0:
                    description += f"• Zusätzlicher Rabatt: -{breakdown['manual_discount_percent']:.0f}% (-{breakdown['manual_discount_amount']:.2f} €)\n"
                    if participant.discount_reason:
                        description += f"  Grund: {participant.discount_reason}\n"
            else:
                # Manuelle Preisüberschreibung
                description += f"• Manuell gesetzter Preis: {breakdown['manual_price_override']:.2f} €\n"
                if participant.discount_reason:
                    description += f"  Grund: {participant.discount_reason}\n"

        final_price = participant.final_price
        positions_data.append([
            "1",
            Paragraph(description, normal_style),  # Wrap in Paragraph to render HTML tags
            f"{final_price:.2f} €"
        ])

        # Positions-Tabelle erstellen
        pos_table = Table(positions_data, colWidths=[1.5*cm, 13*cm, 3*cm])
        pos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(pos_table)
        story.append(Spacer(1, 0.5*cm))

        # Summen-Tabelle
        sum_data = [
            ["", "Zwischensumme:", f"{final_price:.2f} €"],
            ["", "Bereits bezahlt:", f"{total_paid:.2f} €"],
            ["", "Offener Betrag:", f"{outstanding:.2f} €"],
        ]
        sum_table = Table(sum_data, colWidths=[1.5*cm, 13*cm, 3*cm])
        sum_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, -1), (-1, -1), 12),
            ('LINEABOVE', (1, -1), (-1, -1), 2, colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (2, -1), (-1, -1), colors.HexColor('#1e40af')),
        ]))
        story.append(sum_table)
        story.append(Spacer(1, 1.5*cm))

        # Zahlungsinformationen
        footer_text = settings.invoice_footer_text or "Vielen Dank für Ihre Zahlung!"
        if outstanding > 0:
            story.append(Paragraph("Zahlungsinformationen:", heading_style))
            payment_text = f"""
            Bitte überweisen Sie den offenen Betrag unter Angabe der Rechnungsnummer auf folgendes Konto:<br/>
            <br/>
            <b>Kontoinhaber:</b> {settings.bank_account_holder}<br/>
            <b>IBAN:</b> {settings.bank_iban}<br/>
            """
            if settings.bank_bic:
                payment_text += f"<b>BIC:</b> {settings.bank_bic}<br/>"
            payment_text += f"""<b>Verwendungszweck:</b> {payment_reference}<br/>
            <br/>
            {footer_text}
            """
            story.append(Paragraph(payment_text, normal_style))
            if qr_image:
                story.append(Spacer(1, 0.3*cm))
                story.append(Paragraph(
                    f"<i>Tipp: Scannen Sie den QR-Code oben rechts mit Ihrer Banking-App um die Überweisung von {outstanding:.2f} € direkt auszuführen.</i>",
                    normal_style
                ))
        else:
            story.append(Paragraph("Status: Vollständig bezahlt", heading_style))
            story.append(Paragraph(footer_text, normal_style))

        # PDF generieren
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_family_invoice(self, family) -> bytes:
        """
        Generiert eine Sammelrechnung für eine Familie

        Args:
            family: Family-Objekt mit allen Teilnehmern

        Returns:
            PDF als bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=self.pagesize, topMargin=2*cm)
        story = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#059669'),
            spaceAfter=30,
        )
        heading_style = styles['Heading2']
        normal_style = styles['Normal']

        # Einstellungen laden
        settings = self._get_settings(family.event_id)

        # Absender/Organisation
        story.append(Paragraph(settings.organization_name, title_style))
        if settings.organization_address:
            # Adresse aufbereiten (Zeilenumbrüche durch • ersetzen für kompakte Anzeige)
            address_compact = settings.organization_address.replace('\n', ' • ')
            story.append(Paragraph(address_compact, normal_style))
        story.append(Spacer(1, 0.5*cm))

        # Rechnungsnummer und Datum
        invoice_number = f"SR-{family.id:06d}-{datetime.now().year}"
        invoice_date = datetime.now().strftime("%d.%m.%Y")

        # Gesamtbetrag und ausstehenden Betrag berechnen
        # Konvertiere zu float um Decimal/float Typ-Konflikte zu vermeiden
        total_amount = float(sum((p.final_price for p in family.participants if p.is_active), 0))

        # Zahlungen: Sowohl direkte Familienzahlungen als auch Zahlungen an einzelne Mitglieder
        family_payments = float(sum((payment.amount for payment in family.payments), 0))
        member_payments = float(sum(
            (payment.amount
            for participant in family.participants
            for payment in participant.payments), 0
        ))
        total_paid = family_payments + member_payments
        outstanding = total_amount - total_paid

        qr_image = None

        # Verwendungszweck: Präfix + Familienname
        subject_prefix = settings.invoice_subject_prefix or "Teilnahmegebühr"
        payment_reference = f"{subject_prefix} Familie {family.name}"

        # QR-Code für SEPA-Zahlung generieren (falls offen)
        if outstanding > 0:
            try:
                qr_code_bytes = QRCodeService.generate_sepa_qr_code(
                    recipient_name=settings.bank_account_holder,
                    iban=settings.bank_iban,
                    amount=outstanding,
                    purpose=payment_reference,
                    bic=settings.bank_bic
                )
                qr_image = Image(BytesIO(qr_code_bytes), width=3.5*cm, height=3.5*cm)
            except Exception as e:
                print(f"Warnung: QR-Code konnte nicht generiert werden: {e}")

        # Info-Tabelle links, QR-Code rechts
        if qr_image:
            # Info und QR-Code in einer Tabelle nebeneinander
            info_data = [
                ["Rechnungsnummer:", invoice_number, qr_image],
                ["Rechnungsdatum:", invoice_date, ""],
                ["Familien-ID:", str(family.id), ""],
                ["Art:", "Sammelrechnung", ""]
            ]
            info_table = Table(info_data, colWidths=[5*cm, 6*cm, 4*cm])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('VALIGN', (2, 0), (2, 0), 'MIDDLE'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (1, -1), 5),
                ('SPAN', (2, 0), (2, 3)),  # QR-Code über alle 4 Zeilen spannen
            ]))
        else:
            info_data = [
                ["Rechnungsnummer:", invoice_number],
                ["Rechnungsdatum:", invoice_date],
                ["Familien-ID:", str(family.id)],
                ["Art:", "Sammelrechnung"]
            ]
            info_table = Table(info_data, colWidths=[5*cm, 6*cm])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))

        story.append(info_table)
        story.append(Spacer(1, 1*cm))

        # Empfänger
        story.append(Paragraph("Sammelrechnung für Familie:", heading_style))
        recipient_text = f"<b>{family.name}</b><br/>"
        if family.contact_person:
            recipient_text += f"Ansprechpartner: {family.contact_person}<br/>"
        if family.address:
            recipient_text += family.address.replace('\n', '<br/>')
        story.append(Paragraph(recipient_text, normal_style))
        story.append(Spacer(1, 1*cm))

        # Positions-Tabelle (ohne Menge und Einzelpreis für kompaktere Darstellung)
        positions_data = [
            ["Pos.", "Beschreibung", "Gesamtpreis"]
        ]

        for idx, participant in enumerate(family.participants, 1):
            if not participant.is_active:
                continue

            # Preis-Aufschlüsselung berechnen
            breakdown = self._calculate_price_breakdown(participant)

            description = f"<b>{participant.full_name}</b>\n"
            description += f"{participant.event.name}\n"
            description += f"Zeitraum: {participant.event.start_date.strftime('%d.%m.%Y')} - {participant.event.end_date.strftime('%d.%m.%Y')}\n"
            role_info = f", Rolle: {participant.role.display_name}" if participant.role else ""
            description += f"Alter: {participant.age_at_event} Jahre{role_info}\n"

            # Rabatt-Details hinzufügen
            if breakdown['has_discounts']:
                description += "\n<b>Preisberechnung:</b>\n"
                if breakdown['manual_price_override'] is None:
                    # Normale Berechnung
                    description += f"• Basispreis: {breakdown['base_price']:.2f} €\n"
                    if breakdown['role_discount_percent'] > 0:
                        description += f"• Rollenrabatt: -{breakdown['role_discount_percent']:.0f}% (-{breakdown['role_discount_amount']:.2f} €) → {breakdown['price_after_role_discount']:.2f} €\n"
                    if breakdown['family_discount_percent'] > 0:
                        description += f"• Familienrabatt: -{breakdown['family_discount_percent']:.0f}% (-{breakdown['family_discount_amount']:.2f} €) → {breakdown['price_after_family_discount']:.2f} €\n"
                    if breakdown['manual_discount_percent'] > 0:
                        description += f"• Zusätzl. Rabatt: -{breakdown['manual_discount_percent']:.0f}%"
                        if participant.discount_reason:
                            description += f" ({participant.discount_reason})"
                        description += "\n"
                else:
                    # Manuelle Preisüberschreibung
                    description += f"• Manueller Preis: {breakdown['manual_price_override']:.2f} €\n"
                    if participant.discount_reason:
                        description += f"  Grund: {participant.discount_reason}\n"

            price = participant.final_price

            positions_data.append([
                str(idx),
                Paragraph(description, normal_style),  # Wrap in Paragraph to render HTML tags
                f"{price:.2f} €"
            ])

        # Positions-Tabelle erstellen
        pos_table = Table(positions_data, colWidths=[1.5*cm, 13*cm, 3*cm])
        pos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(pos_table)
        story.append(Spacer(1, 0.5*cm))

        # Summen-Tabelle
        # (total_amount, total_paid und outstanding wurden bereits oben berechnet)
        sum_data = [
            ["", "Gesamtsumme:", f"{total_amount:.2f} €"],
            ["", "Bereits bezahlt:", f"{total_paid:.2f} €"],
            ["", "Offener Betrag:", f"{outstanding:.2f} €"],
        ]
        sum_table = Table(sum_data, colWidths=[1.5*cm, 13*cm, 3*cm])
        sum_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, -1), (-1, -1), 12),
            ('LINEABOVE', (1, -1), (-1, -1), 2, colors.HexColor('#059669')),
            ('TEXTCOLOR', (2, -1), (-1, -1), colors.HexColor('#059669')),
        ]))
        story.append(sum_table)
        story.append(Spacer(1, 1*cm))

        # Hinweis auf Familienrabatt
        if len(family.participants) >= 2:
            story.append(Paragraph("Hinweis:", heading_style))
            discount_text = f"Die Preise enthalten bereits Familienrabatte für {len(family.participants)} Teilnehmer."
            story.append(Paragraph(discount_text, normal_style))
            story.append(Spacer(1, 0.5*cm))

        # Zahlungsinformationen
        footer_text = settings.invoice_footer_text or "Vielen Dank für Ihre Zahlung!"
        if outstanding > 0:
            story.append(Paragraph("Zahlungsinformationen:", heading_style))
            payment_text = f"""
            Bitte überweisen Sie den offenen Betrag unter Angabe der Rechnungsnummer auf folgendes Konto:<br/>
            <br/>
            <b>Kontoinhaber:</b> {settings.bank_account_holder}<br/>
            <b>IBAN:</b> {settings.bank_iban}<br/>
            """
            if settings.bank_bic:
                payment_text += f"<b>BIC:</b> {settings.bank_bic}<br/>"
            payment_text += f"""<b>Verwendungszweck:</b> {payment_reference}<br/>
            <br/>
            {footer_text}
            """
            story.append(Paragraph(payment_text, normal_style))
            if qr_image:
                story.append(Spacer(1, 0.3*cm))
                story.append(Paragraph(
                    f"<i>Tipp: Scannen Sie den QR-Code oben rechts mit Ihrer Banking-App um die Überweisung von {outstanding:.2f} € direkt auszuführen.</i>",
                    normal_style
                ))
        else:
            story.append(Paragraph("Status: Vollständig bezahlt", heading_style))
            story.append(Paragraph(footer_text, normal_style))

        # PDF generieren
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
