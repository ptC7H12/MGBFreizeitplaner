"""QR-Code Service für SEPA-Überweisungen (EPC QR-Code)"""
import logging
import qrcode
from io import BytesIO
from typing import Optional

logger = logging.getLogger(__name__)


class QRCodeService:
    """Service für die Generierung von QR-Codes für Zahlungen"""

    @staticmethod
    def generate_sepa_qr_code(
        recipient_name: str,
        iban: str,
        amount: float,
        purpose: str,
        bic: Optional[str] = None
    ) -> bytes:
        """
        Generiert einen EPC QR-Code für SEPA-Überweisungen

        Der QR-Code kann von Banking-Apps gescannt werden, um eine
        Überweisung automatisch auszufüllen.

        Args:
            recipient_name: Name des Zahlungsempfängers
            iban: IBAN des Empfängers
            amount: Betrag in Euro
            purpose: Verwendungszweck
            bic: BIC des Empfängers (optional, aber empfohlen)

        Returns:
            QR-Code als PNG-Bilddaten (bytes)

        EPC QR-Code Format (Version 002):
        Zeile  1: BCD (Service Tag)
        Zeile  2: 002 (Version)
        Zeile  3: 1 (Character Set - UTF-8)
        Zeile  4: SCT (Identification - SEPA Credit Transfer)
        Zeile  5: BIC (optional)
        Zeile  6: Empfängername (max 70 Zeichen)
        Zeile  7: IBAN
        Zeile  8: EUR + Betrag (z.B. EUR123.45)
        Zeile  9: Purpose Code (leer)
        Zeile 10: Structured Reference (leer)
        Zeile 11: Unstructured Remittance (Verwendungszweck, max 140 Zeichen)
        Zeile 12: Beneficiary to Originator Information (leer)
        """
        # IBAN normalisieren (Leerzeichen entfernen, Großbuchstaben)
        iban_normalized = iban.replace(" ", "").upper()

        # BIC normalisieren falls vorhanden
        bic_normalized = ""
        if bic:
            bic_normalized = bic.replace(" ", "").upper()

        # Empfängername kürzen wenn nötig
        recipient = recipient_name[:70] if len(recipient_name) > 70 else recipient_name

        # Verwendungszweck kürzen wenn nötig
        remittance = purpose[:140] if len(purpose) > 140 else purpose

        # Betrag formatieren (maximal 2 Dezimalstellen)
        amount_str = f"EUR{amount:.2f}"

        # EPC QR-Code Daten zusammenstellen
        epc_data = [
            "BCD",                  # Service Tag
            "002",                  # Version
            "1",                    # Character Set (UTF-8)
            "SCT",                  # Identification (SEPA Credit Transfer)
            bic_normalized,         # BIC (kann leer sein)
            recipient,              # Empfängername
            iban_normalized,        # IBAN
            amount_str,             # Betrag
            "",                     # Purpose Code (leer)
            "",                     # Structured Reference (leer)
            remittance,             # Verwendungszweck
            ""                      # Beneficiary to Originator Info (leer)
        ]

        # EPC String erstellen (Zeilen mit \n getrennt)
        epc_string = "\n".join(epc_data)

        # QR-Code generieren
        qr = qrcode.QRCode(
            version=None,  # Automatische Größenanpassung
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(epc_string)
        qr.make(fit=True)

        # QR-Code als Bild erstellen
        img = qr.make_image(fill_color="black", back_color="white")

        # Bild in BytesIO speichern
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        return buffer.getvalue()

    @staticmethod
    def generate_simple_qr_code(data: str) -> bytes:
        """
        Generiert einen einfachen QR-Code für beliebige Daten

        Args:
            data: Daten für den QR-Code

        Returns:
            QR-Code als PNG-Bilddaten (bytes)
        """
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        return buffer.getvalue()
