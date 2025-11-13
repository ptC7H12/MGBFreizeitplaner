"""Invoice (Rechnung) Generator Service"""
from io import BytesIO
from datetime import datetime, date
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas


class InvoiceGenerator:
    """Service für die Generierung von PDF-Rechnungen"""

    def __init__(self):
        self.pagesize = A4
        self.width, self.height = self.pagesize

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

        # Absender/Organisation
        story.append(Paragraph("Freizeit-Kassen-System", title_style))
        story.append(Paragraph("Musterstraße 123 • 12345 Musterstadt", normal_style))
        story.append(Spacer(1, 0.5*cm))

        # Rechnungsnummer und Datum
        invoice_number = f"R-{participant.id:06d}-{datetime.now().year}"
        invoice_date = datetime.now().strftime("%d.%m.%Y")

        info_data = [
            ["Rechnungsnummer:", invoice_number],
            ["Rechnungsdatum:", invoice_date],
            ["Teilnehmer-ID:", str(participant.id)]
        ]
        info_table = Table(info_data, colWidths=[5*cm, 8*cm])
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

        # Betreff
        story.append(Paragraph(f"Teilnahme an: {participant.event.name}", heading_style))
        story.append(Spacer(1, 0.5*cm))

        # Positions-Tabelle
        positions_data = [
            ["Pos.", "Beschreibung", "Menge", "Einzelpreis", "Gesamtpreis"]
        ]

        # Position: Teilnahmegebühr
        description = f"Teilnahmegebühr {participant.event.name}\n"
        description += f"Zeitraum: {participant.event.start_date.strftime('%d.%m.%Y')} - {participant.event.end_date.strftime('%d.%m.%Y')}\n"
        description += f"Teilnehmer: {participant.full_name} ({participant.age_at_event} Jahre)\n"
        description += f"Rolle: {participant.role.display_name}"

        final_price = participant.final_price
        positions_data.append([
            "1",
            description,
            "1",
            f"{final_price:.2f} €",
            f"{final_price:.2f} €"
        ])

        # Positions-Tabelle erstellen
        pos_table = Table(positions_data, colWidths=[1*cm, 10*cm, 1.5*cm, 2.5*cm, 2.5*cm])
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
        total_paid = sum(payment.amount for payment in participant.payments)
        outstanding = final_price - total_paid

        sum_data = [
            ["", "", "", "Zwischensumme:", f"{final_price:.2f} €"],
            ["", "", "", "Bereits bezahlt:", f"{total_paid:.2f} €"],
            ["", "", "", "Offener Betrag:", f"{outstanding:.2f} €"],
        ]
        sum_table = Table(sum_data, colWidths=[1*cm, 10*cm, 1.5*cm, 2.5*cm, 2.5*cm])
        sum_table.setStyle(TableStyle([
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (3, -1), (-1, -1), 12),
            ('LINEABOVE', (3, -1), (-1, -1), 2, colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (4, -1), (-1, -1), colors.HexColor('#1e40af')),
        ]))
        story.append(sum_table)
        story.append(Spacer(1, 1.5*cm))

        # Zahlungsinformationen
        if outstanding > 0:
            story.append(Paragraph("Zahlungsinformationen:", heading_style))
            payment_text = """
            Bitte überweisen Sie den offenen Betrag unter Angabe der Rechnungsnummer auf folgendes Konto:<br/>
            <br/>
            <b>Kontoinhaber:</b> Freizeit-Kassen-System<br/>
            <b>IBAN:</b> DE89 3704 0044 0532 0130 00<br/>
            <b>BIC:</b> COBADEFFXXX<br/>
            <b>Verwendungszweck:</b> {}<br/>
            <br/>
            Vielen Dank für Ihre Zahlung!
            """.format(invoice_number)
            story.append(Paragraph(payment_text, normal_style))
        else:
            story.append(Paragraph("Status: Vollständig bezahlt", heading_style))
            story.append(Paragraph("Vielen Dank für Ihre Zahlung!", normal_style))

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

        # Absender/Organisation
        story.append(Paragraph("Freizeit-Kassen-System", title_style))
        story.append(Paragraph("Musterstraße 123 • 12345 Musterstadt", normal_style))
        story.append(Spacer(1, 0.5*cm))

        # Rechnungsnummer und Datum
        invoice_number = f"SR-{family.id:06d}-{datetime.now().year}"
        invoice_date = datetime.now().strftime("%d.%m.%Y")

        info_data = [
            ["Rechnungsnummer:", invoice_number],
            ["Rechnungsdatum:", invoice_date],
            ["Familien-ID:", str(family.id)],
            ["Art:", "Sammelrechnung"]
        ]
        info_table = Table(info_data, colWidths=[5*cm, 8*cm])
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

        # Positions-Tabelle
        positions_data = [
            ["Pos.", "Beschreibung", "Menge", "Einzelpreis", "Gesamtpreis"]
        ]

        total_amount = 0
        for idx, participant in enumerate(family.participants, 1):
            if not participant.is_active:
                continue

            description = f"<b>{participant.full_name}</b>\n"
            description += f"{participant.event.name}\n"
            description += f"Zeitraum: {participant.event.start_date.strftime('%d.%m.%Y')} - {participant.event.end_date.strftime('%d.%m.%Y')}\n"
            description += f"Alter: {participant.age_at_event} Jahre, Rolle: {participant.role.display_name}"

            price = participant.final_price
            total_amount += price

            positions_data.append([
                str(idx),
                description,
                "1",
                f"{price:.2f} €",
                f"{price:.2f} €"
            ])

        # Positions-Tabelle erstellen
        pos_table = Table(positions_data, colWidths=[1*cm, 10*cm, 1.5*cm, 2.5*cm, 2.5*cm])
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
        total_paid = sum(payment.amount for payment in family.payments)
        outstanding = total_amount - total_paid

        sum_data = [
            ["", "", "", "Gesamtsumme:", f"{total_amount:.2f} €"],
            ["", "", "", "Bereits bezahlt:", f"{total_paid:.2f} €"],
            ["", "", "", "Offener Betrag:", f"{outstanding:.2f} €"],
        ]
        sum_table = Table(sum_data, colWidths=[1*cm, 10*cm, 1.5*cm, 2.5*cm, 2.5*cm])
        sum_table.setStyle(TableStyle([
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (3, -1), (-1, -1), 12),
            ('LINEABOVE', (3, -1), (-1, -1), 2, colors.HexColor('#059669')),
            ('TEXTCOLOR', (4, -1), (-1, -1), colors.HexColor('#059669')),
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
        if outstanding > 0:
            story.append(Paragraph("Zahlungsinformationen:", heading_style))
            payment_text = """
            Bitte überweisen Sie den offenen Betrag unter Angabe der Rechnungsnummer auf folgendes Konto:<br/>
            <br/>
            <b>Kontoinhaber:</b> Freizeit-Kassen-System<br/>
            <b>IBAN:</b> DE89 3704 0044 0532 0130 00<br/>
            <b>BIC:</b> COBADEFFXXX<br/>
            <b>Verwendungszweck:</b> {}<br/>
            <br/>
            Vielen Dank für Ihre Zahlung!
            """.format(invoice_number)
            story.append(Paragraph(payment_text, normal_style))
        else:
            story.append(Paragraph("Status: Vollständig bezahlt", heading_style))
            story.append(Paragraph("Vielen Dank für Ihre Zahlung!", normal_style))

        # PDF generieren
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
