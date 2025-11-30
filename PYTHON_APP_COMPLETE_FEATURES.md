# MGBFreizeitplaner - Vollständige Feature-Spezifikation der Python-App

**Zweck**: Dieses Dokument beschreibt ALLE Funktionen der ursprünglichen Python/FastAPI-Webanwendung, damit eine KI diese Features 1:1 in die Flutter-App übertragen kann.

**Version**: Python-App (Original)
**Erstellt**: 2025-11-30

---

## Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Fehlende Features in Flutter-App](#fehlende-features-in-flutter-app)
3. [Detaillierte Feature-Spezifikationen](#detaillierte-feature-spezifikationen)
   - [1. Teilnehmer-Management](#1-teilnehmer-management)
   - [2. Familien-Management](#2-familien-management)
   - [3. Zahlungs-Management](#3-zahlungs-management)
   - [4. Ausgaben-Management](#4-ausgaben-management)
   - [5. Einnahmen-Management](#5-einnahmen-management)
   - [6. Regelwerk-Management](#6-regelwerk-management)
   - [7. Rollen-Management](#7-rollen-management)
   - [8. Aufgaben-System](#8-aufgaben-system)
   - [9. Dashboard & Analytics](#9-dashboard--analytics)
   - [10. Rechnungsgenerierung](#10-rechnungsgenerierung)
   - [11. Import/Export-Funktionen](#11-importexport-funktionen)
   - [12. Kassenstand & Finanzübersicht](#12-kassenstand--finanzübersicht)
   - [13. Einstellungen & Konfiguration](#13-einstellungen--konfiguration)
   - [14. Event-Management](#14-event-management)
4. [Business Logic & Berechnungen](#business-logic--berechnungen)
5. [UI-Komponenten & Workflows](#ui-komponenten--workflows)

---

## Übersicht

Die Python-App ist eine vollständige Verwaltungssoftware für Freizeiten (Familien-, Kinder-, Jugend-, Teeniefreizeiten) mit folgenden Hauptfunktionen:

- **Multi-Event-Fähigkeit**: Mehrere Veranstaltungen parallel verwalten
- **Komplexe Preisberechnung**: Altersgruppen, Rollenrabatte, Familienrabatte, manuelle Rabatte
- **Automatisches Aufgaben-System**: 14 verschiedene Aufgabentypen werden automatisch erkannt
- **Regelwerk-System**: YAML-basierte Regelwerke mit GitHub-Integration
- **Vollständiges Finanz-Management**: Einnahmen, Ausgaben, Zahlungen, Kassenstand
- **PDF-Rechnungsgenerierung**: Einzel- und Sammelrechnungen mit SEPA-QR-Codes
- **Excel-Import/Export**: Massenimport und -export von Teilnehmern
- **Beleg-Management**: Upload und Verwaltung von Ausgabenbelegen
- **Rollenbasierte Rabatte**: Betreuer, Küche, etc. mit individuellen Rabatten
- **Familienrabatte**: Gestaffelte Rabatte für 1., 2., 3.+ Kinder
- **Bildung & Teilhabe**: BuT-Integration für Zuschüsse

---

## Fehlende Features in Flutter-App

Die aktuelle Flutter-App hat folgende Basisfunktionen, aber es fehlen viele erweiterte Features:

### Bereits in Flutter implementiert:
- ✅ Teilnehmer-Liste (Grundfunktion)
- ✅ Teilnehmer hinzufügen/bearbeiten/löschen
- ✅ Familien-Liste und -Verwaltung
- ✅ Zahlungen erfassen
- ✅ Ausgaben erfassen
- ✅ Einnahmen erfassen
- ✅ Regelwerk-Liste
- ✅ Rollen-Verwaltung
- ✅ Aufgaben-Liste (Basis)
- ✅ Dashboard mit Statistiken
- ✅ Kassenstand-Übersicht
- ✅ Einstellungen-Screen (neu)

### Fehlende Features (müssen implementiert werden):

#### Teilnehmer-Management:
- ❌ **Excel-Import**: Massenimport von Teilnehmern aus Excel-Datei
- ❌ **Excel-Export**: Export aller Teilnehmer nach Excel
- ❌ **PDF-Export**: Teilnehmerliste als PDF
- ❌ **QR-Code Generierung**: Für jeden Teilnehmer (schneller Zugriff)
- ❌ **Erweiterte Filter**: Nach Alter, Geschlecht, Rolle, Familie
- ❌ **Sortierung**: Nach allen Feldern sortierbar
- ❌ **Suche**: Echtzeit-Suche über alle Felder
- ❌ **Notizen-Feld**: Freitextfeld für zusätzliche Informationen
- ❌ **Adresse**: Vollständige Adressverwaltung (Straße, PLZ, Ort)
- ❌ **Telefon/Email**: Kontaktdaten
- ❌ **Bildung & Teilhabe ID**: BuT-Nummer für Zuschüsse
- ❌ **Preis-Breakdown-Ansicht**: Detaillierte Aufschlüsselung wie Preis berechnet wurde

#### Familien-Management:
- ❌ **Sammelrechnung-PDF**: Rechnung für ganze Familie generieren
- ❌ **Familien-Zahlungen**: Zahlungen die für ganze Familie gelten (nicht nur einzelne Mitglieder)
- ❌ **Kontaktperson**: Hauptansprechpartner der Familie
- ❌ **Telefon/Email**: Familien-Kontaktdaten
- ❌ **Automatische Sortierung**: Kinder nach Alter sortieren für Familienrabatt-Berechnung

#### Zahlungs-Management:
- ❌ **Teilnehmer-Rechnung-PDF**: Einzelrechnung mit SEPA-QR-Code
- ❌ **Familien-Rechnung-PDF**: Sammelrechnung mit SEPA-QR-Code
- ❌ **Rechnungsnummern**: Automatische Nummerierung (R-XXXXXX-YYYY)
- ❌ **SEPA-QR-Codes**: Scanbare QR-Codes für Banking-Apps
- ❌ **Zahlungsübersicht pro Teilnehmer**: Alle Zahlungen eines Teilnehmers
- ❌ **Zahlungsmethoden-Tracking**: Bar, Überweisung, PayPal, etc.
- ❌ **Referenznummer**: Verwendungszweck/Referenz erfassen

#### Ausgaben-Management:
- ❌ **Beleg-Upload**: Fotos/PDFs von Belegen hochladen
- ❌ **Beleg-Anzeige**: Hochgeladene Belege anzeigen
- ❌ **Beleg-Download**: Belege herunterladen
- ❌ **Kategorien-Management**: Kategorien erstellen/umbenennen/löschen
- ❌ **Ausgaben-Filter**: Nach Kategorie, Status, Datum
- ❌ **Ausgaben-Sortierung**: Nach allen Feldern
- ❌ **Erstattungs-Status**: Ausgabe erstattet/nicht erstattet
- ❌ **Bezahlt-von**: Wer hat die Ausgabe ausgelegt

#### Regelwerk-Management:
- ❌ **YAML-Import von Datei**: Regelwerk aus lokaler YAML-Datei importieren
- ❌ **YAML-Import von GitHub**: Regelwerk direkt von GitHub-URL importieren
- ❌ **YAML-Export**: Regelwerk als YAML-Datei exportieren
- ❌ **Verzeichnis-Scanner**: Lokale Verzeichnisse nach Regelwerken durchsuchen
- ❌ **Manueller YAML-Editor**: Regelwerk als Text bearbeiten
- ❌ **Regelwerk aktivieren/deaktivieren**: Nur ein aktives Regelwerk pro Event
- ❌ **Automatische Rollen-Erstellung**: Rollen aus Regelwerk automatisch anlegen
- ❌ **Automatische Preisneuberechnung**: Bei Regelwerk-Wechsel alle Preise neu berechnen
- ❌ **Automatischer GitHub-Import**: Passendes Regelwerk bei Event-Erstellung automatisch laden

#### Dashboard & Analytics:
- ❌ **Altersverteilung-Diagramm**: Balkendiagramm nach Altersgruppen (0-5, 6-11, 12-17, 18-25, 26-40, 41+)
- ❌ **Zahlungsverlauf-Diagramm**: Kumulative Zahlungseingänge über Zeit
- ❌ **Rollen-Verteilung-Diagramm**: Kreisdiagramm Teilnehmer pro Rolle
- ❌ **Ausgaben-Kategorien-Diagramm**: Kreisdiagramm Ausgaben pro Kategorie
- ❌ **Zahlungsmethoden-Diagramm**: Verteilung der Zahlungsmethoden
- ❌ **Detaillierte Finanz-KPIs**:
  - Soll-Zahlungseingänge vs. Ist-Zahlungseingänge
  - Basispreise vs. Rabattierte Preise
  - Erwartete Zuschüsse
  - Zahlungsquote in Prozent
  - Offene Zahlungen
  - Saldo (Einnahmen - Ausgaben)

#### Aufgaben-System (automatisch generiert):
- ❌ **14 verschiedene Aufgabentypen**:
  1. **Bildung & Teilhabe**: Teilnehmer mit BuT-Nummer (müssen beantragt werden)
  2. **Ausgaben-Erstattung**: Nicht erstattete Ausgaben
  3. **Offene Zahlungen**: Teilnehmer mit ausstehenden Zahlungen
  4. **Manuelle Preise prüfen**: Teilnehmer mit manuell gesetzten Preisen
  5. **Überfällige Zahlungen**: Zahlungen nach Frist (14 Tage vor Event-Start)
  6. **Zuschuss-Differenzen (Rollen)**: Zuschüsse vs. gewährte Rollenrabatte
  7. **Zuschuss-Differenzen (Familien)**: Kinderzuschuss vs. Familienrabatte
  8. **Rollen-Überschreitungen**: Zu viele Teilnehmer einer Rolle
  9. **Geburtstagskinder**: Geburtstage während der Freizeit
  10. **Küchenteam-Geschenk**: Erinnerung Geschenk für Küche
  11. **Familienfreizeit-Prüfung**: Prüfen ob Kinder von Nicht-Mitgliedern dabei sind
  12. **Custom Tasks**: Manuell erstellte Aufgaben
  13. **Task-Notizen**: Notizen zu erledigten Aufgaben
  14. **Auto-Payment-Creation**: Automatische Zahlung bei "erledigt" markieren
- ❌ **Aufgaben als erledigt markieren**
- ❌ **Aufgaben wieder öffnen**
- ❌ **Notizen zu Aufgaben**
- ❌ **Aufgabenzähler**: Badge mit Anzahl offener Aufgaben

#### Kassenstand & Finanzübersicht:
- ❌ **Zuschüsse-Berechnung**:
  - Erwartete Rollenrabatte pro Rolle
  - Erwartete Familienrabatte
  - Vergleich mit tatsächlichen Einnahmen (Incomes)
  - Differenz-Anzeige
- ❌ **Detaillierte Tabellen**:
  - Zuschüsse pro Rolle (erwartet vs. erhalten)
  - Familienrabatte (berechnet)
  - Basispreise (ohne Rabatte)
- ❌ **PDF-Export**: Kassenstand-Bericht als PDF

#### Einstellungen:
- ❌ **Organisation**: Name, Adresse
- ❌ **Bankdaten**: IBAN, BIC, Kontoinhaber
- ❌ **Rechnungs-Texte**: Betreff-Präfix, Fußzeile
- ❌ **GitHub-Repository**: Standard-Repo für Regelwerk-Import
- ❌ **Kategorien-Verwaltung**: Ausgaben-Kategorien bearbeiten

---

## Detaillierte Feature-Spezifikationen

### 1. Teilnehmer-Management

#### 1.1 Excel-Import

**Beschreibung**: Massenimport von Teilnehmern aus einer Excel-Datei (.xlsx)

**Funktion**:
1. Excel-Datei auswählen (File Picker)
2. Datei wird gelesen und validiert
3. Vorschau der zu importierenden Daten
4. Import ausführen
5. Erfolgs-/Fehlermeldung mit Statistik

**Excel-Format** (Spalten):
```
Vorname | Nachname | Geburtsdatum | Geschlecht | Adresse | Telefon | Email | Notizen | Rolle | BuT-ID
```

**Spalten-Details**:
- **Vorname** (Pflicht): Text
- **Nachname** (Pflicht): Text
- **Geburtsdatum** (Pflicht): Format DD.MM.YYYY oder YYYY-MM-DD
- **Geschlecht** (Optional): "M", "W", "D" oder leer
- **Adresse** (Optional): Text (kann Zeilenumbrüche enthalten)
- **Telefon** (Optional): Text
- **Email** (Optional): Email-Format
- **Notizen** (Optional): Freitext
- **Rolle** (Optional): Rollen-Name (muss existieren oder wird erstellt)
- **BuT-ID** (Optional): Bildung & Teilhabe Nummer

**Validierung**:
- Pflichtfelder prüfen (Vorname, Nachname, Geburtsdatum)
- Geburtsdatum-Format prüfen
- Email-Format prüfen (falls vorhanden)
- Duplikate erkennen (gleicher Name + Geburtsdatum)
- Rolle prüfen (existiert oder erstellen?)

**Import-Logik**:
```dart
1. Excel-Datei lesen (excel package)
2. Erste Zeile als Header lesen
3. Spalten-Mapping erstellen
4. Jede Zeile durchgehen:
   a. Daten extrahieren
   b. Validieren
   c. Participant-Objekt erstellen
   d. Rolle zuweisen (falls vorhanden)
   e. Preis berechnen (calculate_participant_price)
   f. In Datenbank speichern
5. Statistik erstellen:
   - X Teilnehmer erfolgreich importiert
   - Y Teilnehmer übersprungen (Fehler)
   - Liste der Fehler
```

**UI-Flow**:
```
1. Button "Excel importieren" in Teilnehmer-Liste
2. File Picker öffnen (xlsx-Filter)
3. Datei auswählen
4. Ladebildschirm mit Progress
5. Vorschau-Dialog:
   - "X Teilnehmer gefunden"
   - "Y valide, Z Fehler"
   - Liste der Fehler (falls vorhanden)
   - Buttons: "Abbrechen" | "Importieren"
6. Import ausführen
7. Erfolgs-Dialog:
   - "X Teilnehmer importiert"
   - "Y Fehler"
   - Button: "OK"
```

**Code-Beispiel** (Struktur):
```dart
class ExcelImportService {
  static Future<ImportResult> importParticipantsFromExcel(
    File excelFile,
    int eventId,
    Database db
  ) async {
    // 1. Excel lesen
    var bytes = excelFile.readAsBytesSync();
    var excel = Excel.decodeBytes(bytes);

    // 2. Erste Tabelle verwenden
    var table = excel.tables[excel.tables.keys.first];

    // 3. Header-Row lesen (Zeile 0)
    var headers = table.rows[0];
    var columnMapping = _mapColumns(headers);

    // 4. Daten-Rows verarbeiten (ab Zeile 1)
    List<Participant> imported = [];
    List<String> errors = [];

    for (int i = 1; i < table.rows.length; i++) {
      var row = table.rows[i];
      try {
        var participant = _parseRowToParticipant(row, columnMapping, eventId);
        // Preis berechnen
        participant.calculated_price = await PriceCalculator.calculatePrice(...);
        // In DB speichern
        await db.participantsRepository.insert(participant);
        imported.add(participant);
      } catch (e) {
        errors.add("Zeile ${i+1}: ${e.toString()}");
      }
    }

    return ImportResult(
      success: imported.length,
      errors: errors
    );
  }

  static Map<String, int> _mapColumns(List<Data?> headers) {
    // Spalten-Namen zu Index mappen
    Map<String, int> mapping = {};
    for (int i = 0; i < headers.length; i++) {
      var header = headers[i]?.value?.toString().toLowerCase() ?? '';
      if (header.contains('vorname') || header.contains('first')) {
        mapping['first_name'] = i;
      }
      // ... weitere Mappings
    }
    return mapping;
  }

  static Participant _parseRowToParticipant(
    List<Data?> row,
    Map<String, int> columnMapping,
    int eventId
  ) {
    // Werte extrahieren
    String firstName = row[columnMapping['first_name']]?.value?.toString() ?? '';
    String lastName = row[columnMapping['last_name']]?.value?.toString() ?? '';
    // ... weitere Felder

    // Validierung
    if (firstName.isEmpty || lastName.isEmpty) {
      throw Exception('Vorname und Nachname sind Pflichtfelder');
    }

    // Geburtsdatum parsen
    DateTime birthDate = _parseBirthDate(row[columnMapping['birth_date']]?.value);

    // Participant erstellen
    return Participant(
      firstName: firstName,
      lastName: lastName,
      birthDate: birthDate,
      // ... weitere Felder
      eventId: eventId
    );
  }

  static DateTime _parseBirthDate(dynamic value) {
    // Verschiedene Formate unterstützen
    if (value is DateTime) return value;

    String dateStr = value.toString();

    // Format: DD.MM.YYYY
    if (dateStr.contains('.')) {
      var parts = dateStr.split('.');
      return DateTime(
        int.parse(parts[2]),
        int.parse(parts[1]),
        int.parse(parts[0])
      );
    }

    // Format: YYYY-MM-DD
    return DateTime.parse(dateStr);
  }
}

class ImportResult {
  final int success;
  final List<String> errors;

  ImportResult({required this.success, required this.errors});
}
```

---

#### 1.2 Excel-Export

**Beschreibung**: Export aller Teilnehmer in eine Excel-Datei (.xlsx)

**Funktion**:
1. Button "Excel exportieren" in Teilnehmer-Liste
2. Alle Teilnehmer abfragen (mit Filtern falls aktiv)
3. Excel-Datei erstellen
4. Datei speichern (File Picker für Zielort)
5. Erfolgs-/Fehlermeldung

**Excel-Format** (Spalten):
```
ID | Vorname | Nachname | Geburtsdatum | Alter | Geschlecht | Adresse | Telefon | Email |
Rolle | Familie | Basispreis | Rollenrabatt | Familienrabatt | Manueller Rabatt |
Endpreis | Bezahlt | Offen | Notizen | BuT-ID | Erstellt am
```

**Spalten-Details**:
- **ID**: Interne Teilnehmer-ID
- **Vorname**: Text
- **Nachname**: Text
- **Geburtsdatum**: Format DD.MM.YYYY
- **Alter**: Berechnet zum Event-Start
- **Geschlecht**: "Männlich", "Weiblich", "Divers", oder leer
- **Adresse**: Text (Zeilenumbrüche beibehalten)
- **Telefon**: Text
- **Email**: Text
- **Rolle**: Rollen-Display-Name
- **Familie**: Familien-Name (falls zugewiesen)
- **Basispreis**: Preis ohne Rabatte (aus Regelwerk)
- **Rollenrabatt**: Rabatt in % (aus Regelwerk)
- **Familienrabatt**: Rabatt in % (aus Regelwerk)
- **Manueller Rabatt**: Zusätzlicher Rabatt in % oder manueller Preis
- **Endpreis**: Finaler zu zahlender Preis
- **Bezahlt**: Summe aller Zahlungen
- **Offen**: Noch zu zahlender Betrag
- **Notizen**: Freitext
- **BuT-ID**: Bildung & Teilhabe Nummer
- **Erstellt am**: Zeitstempel

**Export-Logik**:
```dart
class ExcelExportService {
  static Future<void> exportParticipantsToExcel(
    List<Participant> participants,
    String filePath
  ) async {
    var excel = Excel.createExcel();
    Sheet sheet = excel['Teilnehmer'];

    // Header-Zeile
    sheet.appendRow([
      'ID', 'Vorname', 'Nachname', 'Geburtsdatum', 'Alter', 'Geschlecht',
      'Adresse', 'Telefon', 'Email', 'Rolle', 'Familie',
      'Basispreis', 'Rollenrabatt %', 'Familienrabatt %',
      'Manueller Rabatt/Preis', 'Endpreis', 'Bezahlt', 'Offen',
      'Notizen', 'BuT-ID', 'Erstellt am'
    ]);

    // Daten-Zeilen
    for (var p in participants) {
      // Preis-Breakdown berechnen
      var breakdown = PriceCalculator.calculatePriceBreakdown(p);

      // Zahlungen summieren
      double totalPaid = p.payments.fold(0.0, (sum, payment) => sum + payment.amount);
      double outstanding = p.final_price - totalPaid;

      sheet.appendRow([
        p.id,
        p.firstName,
        p.lastName,
        _formatDate(p.birthDate),
        p.ageAtEvent,
        p.gender ?? '',
        p.address ?? '',
        p.phone ?? '',
        p.email ?? '',
        p.role?.displayName ?? '',
        p.family?.name ?? '',
        breakdown.basePrice,
        breakdown.roleDiscountPercent,
        breakdown.familyDiscountPercent,
        p.manualPriceOverride ?? p.discountPercent,
        p.final_price,
        totalPaid,
        outstanding,
        p.notes ?? '',
        p.bildungTeilhabeId ?? '',
        _formatDateTime(p.createdAt)
      ]);
    }

    // Formatierung
    _formatSheet(sheet);

    // Datei speichern
    var fileBytes = excel.save();
    File(filePath)
      ..createSync(recursive: true)
      ..writeAsBytesSync(fileBytes!);
  }

  static String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}.${date.month.toString().padLeft(2, '0')}.${date.year}';
  }

  static String _formatDateTime(DateTime dt) {
    return '${_formatDate(dt)} ${dt.hour}:${dt.minute.toString().padLeft(2, '0')}';
  }

  static void _formatSheet(Sheet sheet) {
    // Header fett und mit Hintergrundfarbe
    for (int i = 0; i < sheet.maxCols; i++) {
      var cell = sheet.cell(CellIndex.indexByColumnRow(columnIndex: i, rowIndex: 0));
      cell.cellStyle = CellStyle(
        bold: true,
        backgroundColorHex: '#1e40af',
        fontColorHex: '#ffffff'
      );
    }

    // Spaltenbreiten anpassen
    // ... (automatisch oder manuell)
  }
}
```

**UI-Flow**:
```
1. Button "Exportieren" → Dropdown-Menü:
   - "Als Excel exportieren"
   - "Als PDF exportieren"
2. Bei "Als Excel":
   - File Picker öffnen (Zielort wählen)
   - Standard-Dateiname: "Teilnehmer_{EventName}_{Datum}.xlsx"
3. Export ausführen (mit Progress-Indikator)
4. Erfolgs-Snackbar: "X Teilnehmer exportiert nach {Pfad}"
5. Option "Datei öffnen" anbieten
```

---

#### 1.3 PDF-Export (Teilnehmerliste)

**Beschreibung**: Export aller Teilnehmer als formatierte PDF-Datei

**Funktion**:
1. PDF mit Teilnehmer-Tabelle erstellen
2. Filterbare/sortierbare Liste (aktuell angezeigte Teilnehmer)
3. Professionelles Layout mit Header/Footer
4. Gruppierung optional (nach Familie, Rolle, Alter)

**PDF-Layout**:
```
+-------------------------------------------------+
| LOGO               TEILNEHMERLISTE              |
| {EventName}                     Datum: DD.MM.YY |
+-------------------------------------------------+
| Gesamtzahl: X Teilnehmer                        |
+-------------------------------------------------+

+----+----------------+-------+--------+-------------+
| Nr | Name           | Alter | Rolle  | Preis       |
+----+----------------+-------+--------+-------------+
| 1  | Müller, Max    | 12    | Kind   | 150,00 €    |
| 2  | Müller, Anna   | 10    | Kind   | 112,50 €    |
...
+----+----------------+-------+--------+-------------+

Summen:
- Gesamtpreis (Soll):     X.XXX,XX €
- Bereits bezahlt (Ist):  X.XXX,XX €
- Offen:                  X.XXX,XX €

+-------------------------------------------------+
| Seite 1 von X          Erstellt: DD.MM.YY HH:MM |
+-------------------------------------------------+
```

**Code-Beispiel**:
```dart
class PdfExportService {
  static Future<Uint8List> generateParticipantListPdf(
    List<Participant> participants,
    Event event
  ) async {
    final pdf = pw.Document();

    // Daten vorbereiten
    final tableData = [
      ['Nr', 'Name', 'Geb.', 'Alter', 'Rolle', 'Preis', 'Bezahlt', 'Offen']
    ];

    double totalPrice = 0;
    double totalPaid = 0;

    for (int i = 0; i < participants.length; i++) {
      var p = participants[i];
      double paid = p.payments.fold(0.0, (sum, payment) => sum + payment.amount);
      double outstanding = p.final_price - paid;

      totalPrice += p.final_price;
      totalPaid += paid;

      tableData.add([
        (i + 1).toString(),
        '${p.lastName}, ${p.firstName}',
        _formatDate(p.birthDate),
        p.ageAtEvent.toString(),
        p.role?.displayName ?? '-',
        _formatCurrency(p.final_price),
        _formatCurrency(paid),
        _formatCurrency(outstanding)
      ]);
    }

    double totalOutstanding = totalPrice - totalPaid;

    // PDF-Seite erstellen
    pdf.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        margin: pw.EdgeInsets.all(32),
        build: (pw.Context context) {
          return [
            // Header
            pw.Header(
              level: 0,
              child: pw.Row(
                mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                children: [
                  pw.Text(
                    'TEILNEHMERLISTE',
                    style: pw.TextStyle(fontSize: 24, fontWeight: pw.FontWeight.bold)
                  ),
                  pw.Text(
                    _formatDate(DateTime.now()),
                    style: pw.TextStyle(fontSize: 12)
                  )
                ]
              )
            ),

            pw.SizedBox(height: 10),

            // Event-Info
            pw.Text(
              event.name,
              style: pw.TextStyle(fontSize: 16, fontWeight: pw.FontWeight.bold)
            ),
            pw.Text(
              '${_formatDate(event.startDate)} - ${_formatDate(event.endDate)}',
              style: pw.TextStyle(fontSize: 12, color: PdfColors.grey700)
            ),

            pw.SizedBox(height: 20),

            // Statistik
            pw.Container(
              padding: pw.EdgeInsets.all(10),
              decoration: pw.BoxDecoration(
                border: pw.Border.all(color: PdfColors.grey),
                borderRadius: pw.BorderRadius.circular(5)
              ),
              child: pw.Text('Gesamtzahl: ${participants.length} Teilnehmer')
            ),

            pw.SizedBox(height: 20),

            // Tabelle
            pw.Table.fromTextArray(
              headers: tableData[0],
              data: tableData.sublist(1),
              headerStyle: pw.TextStyle(
                fontWeight: pw.FontWeight.bold,
                color: PdfColors.white
              ),
              headerDecoration: pw.BoxDecoration(
                color: PdfColors.blue900
              ),
              cellHeight: 25,
              cellAlignment: pw.Alignment.centerLeft,
              cellAlignments: {
                0: pw.Alignment.center,  // Nr
                3: pw.Alignment.center,  // Alter
                5: pw.Alignment.centerRight,  // Preis
                6: pw.Alignment.centerRight,  // Bezahlt
                7: pw.Alignment.centerRight,  // Offen
              }
            ),

            pw.SizedBox(height: 20),

            // Summen
            pw.Container(
              padding: pw.EdgeInsets.all(10),
              decoration: pw.BoxDecoration(
                border: pw.Border.all(color: PdfColors.grey),
                borderRadius: pw.BorderRadius.circular(5)
              ),
              child: pw.Column(
                crossAxisAlignment: pw.CrossAxisAlignment.start,
                children: [
                  pw.Text(
                    'Summen:',
                    style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 14)
                  ),
                  pw.SizedBox(height: 5),
                  pw.Row(
                    mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                    children: [
                      pw.Text('Gesamtpreis (Soll):'),
                      pw.Text(_formatCurrency(totalPrice), style: pw.TextStyle(fontWeight: pw.FontWeight.bold))
                    ]
                  ),
                  pw.Row(
                    mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                    children: [
                      pw.Text('Bereits bezahlt (Ist):'),
                      pw.Text(_formatCurrency(totalPaid), style: pw.TextStyle(fontWeight: pw.FontWeight.bold))
                    ]
                  ),
                  pw.Divider(),
                  pw.Row(
                    mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                    children: [
                      pw.Text('Offen:', style: pw.TextStyle(fontWeight: pw.FontWeight.bold)),
                      pw.Text(
                        _formatCurrency(totalOutstanding),
                        style: pw.TextStyle(
                          fontWeight: pw.FontWeight.bold,
                          fontSize: 16,
                          color: totalOutstanding > 0 ? PdfColors.red : PdfColors.green
                        )
                      )
                    ]
                  ),
                ]
              )
            ),
          ];
        },
        footer: (pw.Context context) {
          return pw.Container(
            alignment: pw.Alignment.centerRight,
            margin: const pw.EdgeInsets.only(top: 10),
            child: pw.Text(
              'Seite ${context.pageNumber} von ${context.pagesCount}  |  Erstellt: ${_formatDateTime(DateTime.now())}',
              style: pw.TextStyle(fontSize: 10, color: PdfColors.grey)
            )
          );
        }
      )
    );

    return pdf.save();
  }
}
```

---

#### 1.4 QR-Code Generierung

**Beschreibung**: QR-Code für jeden Teilnehmer generieren (schneller Zugriff auf Details)

**Funktion**:
1. QR-Code enthält Teilnehmer-ID und Event-ID
2. Scannen öffnet Teilnehmer-Detailansicht
3. QR-Code in Detailansicht anzeigen
4. QR-Code kann geteilt/gedruckt werden

**QR-Code Format**:
```
mgb://participant/{eventId}/{participantId}
```

**Code-Beispiel**:
```dart
import 'package:qr_flutter/qr_flutter.dart';

class QRCodeService {
  static String generateParticipantUrl(int eventId, int participantId) {
    return 'mgb://participant/$eventId/$participantId';
  }

  static Widget buildQRCode(int eventId, int participantId, {double size = 200}) {
    String data = generateParticipantUrl(eventId, participantId);

    return QrImageView(
      data: data,
      version: QrVersions.auto,
      size: size,
      gapless: false,
      errorStateBuilder: (context, error) {
        return Center(
          child: Text('QR-Code konnte nicht erstellt werden')
        );
      }
    );
  }

  static Future<Participant?> parseQRCode(String data, Database db) async {
    // Parse URL
    if (!data.startsWith('mgb://participant/')) return null;

    var parts = data.substring('mgb://participant/'.length).split('/');
    if (parts.length != 2) return null;

    int eventId = int.parse(parts[0]);
    int participantId = int.parse(parts[1]);

    // Teilnehmer laden
    return await db.participantsRepository.getById(participantId, eventId);
  }
}

// In Participant Detail Screen:
class ParticipantDetailScreen extends StatelessWidget {
  final Participant participant;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(participant.fullName),
        actions: [
          IconButton(
            icon: Icon(Icons.qr_code),
            onPressed: () => _showQRCode(context)
          )
        ]
      ),
      body: // ... Details
    );
  }

  void _showQRCode(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('QR-Code'),
        content: QRCodeService.buildQRCode(
          participant.eventId,
          participant.id,
          size: 300
        ),
        actions: [
          TextButton(
            onPressed: () => _shareQRCode(),
            child: Text('Teilen')
          ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Schließen')
          )
        ]
      )
    );
  }
}
```

---

#### 1.5 Erweiterte Filter & Suche

**Beschreibung**: Umfassende Filter- und Suchfunktionen für Teilnehmer

**Filter-Optionen**:
1. **Altersgruppen**:
   - 0-5 Jahre
   - 6-11 Jahre
   - 12-17 Jahre
   - 18-25 Jahre
   - 26-40 Jahre
   - 41+ Jahre

2. **Geschlecht**:
   - Alle
   - Männlich
   - Weiblich
   - Divers

3. **Rolle**:
   - Alle
   - [Liste aller Rollen]

4. **Familie**:
   - Alle
   - Mit Familie
   - Ohne Familie
   - [Liste aller Familien]

5. **Zahlungsstatus**:
   - Alle
   - Vollständig bezahlt
   - Teilweise bezahlt
   - Nicht bezahlt
   - Überfällig

6. **Aktiv/Inaktiv**:
   - Alle
   - Nur aktive
   - Nur inaktive

**Such-Funktionen**:
- **Echtzeit-Suche** über:
  - Vorname
  - Nachname
  - Email
  - Telefon
  - BuT-ID
  - Notizen
  - Adresse

**Sortier-Optionen**:
- Nach Name (A-Z, Z-A)
- Nach Alter (aufsteigend, absteigend)
- Nach Preis (aufsteigend, absteigend)
- Nach Zahlungsstatus (offen → bezahlt)
- Nach Erstellungsdatum (neueste → älteste)

**Code-Beispiel**:
```dart
class ParticipantsListScreen extends ConsumerStatefulWidget {
  @override
  _ParticipantsListScreenState createState() => _ParticipantsListScreenState();
}

class _ParticipantsListScreenState extends ConsumerState<ParticipantsListScreen> {
  String _searchQuery = '';
  String? _selectedRole;
  String? _selectedFamily;
  String? _selectedAgeGroup;
  String? _selectedGender;
  String? _selectedPaymentStatus;
  bool _showOnlyActive = true;
  String _sortBy = 'name_asc';

  @override
  Widget build(BuildContext context) {
    final participants = ref.watch(filteredParticipantsProvider(
      searchQuery: _searchQuery,
      roleId: _selectedRole,
      familyId: _selectedFamily,
      ageGroup: _selectedAgeGroup,
      gender: _selectedGender,
      paymentStatus: _selectedPaymentStatus,
      showOnlyActive: _showOnlyActive,
      sortBy: _sortBy
    ));

    return Scaffold(
      appBar: AppBar(
        title: Text('Teilnehmer (${participants.length})'),
        actions: [
          IconButton(
            icon: Icon(Icons.search),
            onPressed: () => _showSearchDialog()
          ),
          IconButton(
            icon: Icon(Icons.filter_list),
            onPressed: () => _showFilterDialog()
          ),
          IconButton(
            icon: Icon(Icons.sort),
            onPressed: () => _showSortDialog()
          ),
        ]
      ),
      body: Column(
        children: [
          // Active Filters Chips
          if (_hasActiveFilters())
            _buildActiveFiltersChips(),

          // Search Bar
          Padding(
            padding: EdgeInsets.all(16),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Suchen...',
                prefixIcon: Icon(Icons.search),
                suffixIcon: _searchQuery.isNotEmpty
                  ? IconButton(
                      icon: Icon(Icons.clear),
                      onPressed: () => setState(() => _searchQuery = '')
                    )
                  : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(25)
                )
              ),
              onChanged: (value) => setState(() => _searchQuery = value)
            )
          ),

          // Participants List
          Expanded(
            child: participants.isEmpty
              ? Center(child: Text('Keine Teilnehmer gefunden'))
              : ListView.builder(
                  itemCount: participants.length,
                  itemBuilder: (context, index) {
                    return ParticipantListTile(participant: participants[index]);
                  }
                )
          )
        ]
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _navigateToAddParticipant(),
        child: Icon(Icons.add)
      )
    );
  }

  bool _hasActiveFilters() {
    return _searchQuery.isNotEmpty ||
           _selectedRole != null ||
           _selectedFamily != null ||
           _selectedAgeGroup != null ||
           _selectedGender != null ||
           _selectedPaymentStatus != null ||
           !_showOnlyActive;
  }

  Widget _buildActiveFiltersChips() {
    List<Widget> chips = [];

    if (_searchQuery.isNotEmpty) {
      chips.add(_buildFilterChip('Suche: $_searchQuery', () {
        setState(() => _searchQuery = '');
      }));
    }

    if (_selectedRole != null) {
      chips.add(_buildFilterChip('Rolle: $_selectedRole', () {
        setState(() => _selectedRole = null);
      }));
    }

    // ... weitere Filter-Chips

    return Container(
      padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Wrap(
        spacing: 8,
        children: chips
      )
    );
  }

  Widget _buildFilterChip(String label, VoidCallback onDelete) {
    return Chip(
      label: Text(label),
      onDeleted: onDelete,
      deleteIcon: Icon(Icons.close, size: 18)
    );
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Filter'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Altersgruppe
              DropdownButtonFormField<String>(
                decoration: InputDecoration(labelText: 'Altersgruppe'),
                value: _selectedAgeGroup,
                items: [
                  DropdownMenuItem(value: null, child: Text('Alle')),
                  DropdownMenuItem(value: '0-5', child: Text('0-5 Jahre')),
                  DropdownMenuItem(value: '6-11', child: Text('6-11 Jahre')),
                  DropdownMenuItem(value: '12-17', child: Text('12-17 Jahre')),
                  DropdownMenuItem(value: '18-25', child: Text('18-25 Jahre')),
                  DropdownMenuItem(value: '26-40', child: Text('26-40 Jahre')),
                  DropdownMenuItem(value: '41+', child: Text('41+ Jahre')),
                ],
                onChanged: (value) => setState(() => _selectedAgeGroup = value)
              ),

              // Geschlecht
              DropdownButtonFormField<String>(
                decoration: InputDecoration(labelText: 'Geschlecht'),
                value: _selectedGender,
                items: [
                  DropdownMenuItem(value: null, child: Text('Alle')),
                  DropdownMenuItem(value: 'M', child: Text('Männlich')),
                  DropdownMenuItem(value: 'W', child: Text('Weiblich')),
                  DropdownMenuItem(value: 'D', child: Text('Divers')),
                ],
                onChanged: (value) => setState(() => _selectedGender = value)
              ),

              // Zahlungsstatus
              DropdownButtonFormField<String>(
                decoration: InputDecoration(labelText: 'Zahlungsstatus'),
                value: _selectedPaymentStatus,
                items: [
                  DropdownMenuItem(value: null, child: Text('Alle')),
                  DropdownMenuItem(value: 'paid', child: Text('Vollständig bezahlt')),
                  DropdownMenuItem(value: 'partial', child: Text('Teilweise bezahlt')),
                  DropdownMenuItem(value: 'unpaid', child: Text('Nicht bezahlt')),
                  DropdownMenuItem(value: 'overdue', child: Text('Überfällig')),
                ],
                onChanged: (value) => setState(() => _selectedPaymentStatus = value)
              ),

              // Aktiv/Inaktiv
              SwitchListTile(
                title: Text('Nur aktive Teilnehmer'),
                value: _showOnlyActive,
                onChanged: (value) => setState(() => _showOnlyActive = value)
              ),
            ]
          )
        ),
        actions: [
          TextButton(
            onPressed: () {
              setState(() {
                _selectedAgeGroup = null;
                _selectedGender = null;
                _selectedPaymentStatus = null;
                _showOnlyActive = true;
              });
              Navigator.pop(context);
            },
            child: Text('Zurücksetzen')
          ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Anwenden')
          ),
        ]
      )
    );
  }
}

// Riverpod Provider für gefilterte Teilnehmer
final filteredParticipantsProvider = StreamProvider.family<List<Participant>, FilterParams>(
  (ref, params) {
    final database = ref.watch(databaseProvider);
    final currentEvent = ref.watch(currentEventProvider);

    if (currentEvent == null) return Stream.value([]);

    // Base query
    var query = database.select(database.participants)
      ..where((tbl) => tbl.eventId.equals(currentEvent.id));

    // Aktiv-Filter
    if (params.showOnlyActive) {
      query = query..where((tbl) => tbl.isActive.equals(true));
    }

    // Rollen-Filter
    if (params.roleId != null) {
      query = query..where((tbl) => tbl.roleId.equals(params.roleId!));
    }

    // ... weitere Filter

    return query.watch().map((participants) {
      // Such-Filter (text search)
      if (params.searchQuery.isNotEmpty) {
        participants = participants.where((p) {
          String search = params.searchQuery.toLowerCase();
          return p.firstName.toLowerCase().contains(search) ||
                 p.lastName.toLowerCase().contains(search) ||
                 (p.email?.toLowerCase().contains(search) ?? false) ||
                 (p.phone?.toLowerCase().contains(search) ?? false) ||
                 (p.bildungTeilhabeId?.toLowerCase().contains(search) ?? false);
        }).toList();
      }

      // Altersgruppen-Filter
      if (params.ageGroup != null) {
        participants = participants.where((p) {
          int age = p.ageAtEvent;
          switch (params.ageGroup) {
            case '0-5': return age >= 0 && age <= 5;
            case '6-11': return age >= 6 && age <= 11;
            case '12-17': return age >= 12 && age <= 17;
            case '18-25': return age >= 18 && age <= 25;
            case '26-40': return age >= 26 && age <= 40;
            case '41+': return age >= 41;
            default: return true;
          }
        }).toList();
      }

      // Geschlechts-Filter
      if (params.gender != null) {
        participants = participants.where((p) => p.gender == params.gender).toList();
      }

      // Zahlungsstatus-Filter
      if (params.paymentStatus != null) {
        // TODO: Zahlungen laden und filtern
      }

      // Sortierung
      switch (params.sortBy) {
        case 'name_asc':
          participants.sort((a, b) => a.fullName.compareTo(b.fullName));
          break;
        case 'name_desc':
          participants.sort((a, b) => b.fullName.compareTo(a.fullName));
          break;
        case 'age_asc':
          participants.sort((a, b) => a.ageAtEvent.compareTo(b.ageAtEvent));
          break;
        case 'age_desc':
          participants.sort((a, b) => b.ageAtEvent.compareTo(a.ageAtEvent));
          break;
        // ... weitere Sortierungen
      }

      return participants;
    });
  }
);

class FilterParams {
  final String searchQuery;
  final int? roleId;
  final int? familyId;
  final String? ageGroup;
  final String? gender;
  final String? paymentStatus;
  final bool showOnlyActive;
  final String sortBy;

  FilterParams({
    this.searchQuery = '',
    this.roleId,
    this.familyId,
    this.ageGroup,
    this.gender,
    this.paymentStatus,
    this.showOnlyActive = true,
    this.sortBy = 'name_asc'
  });

  @override
  bool operator ==(Object other) =>
    identical(this, other) ||
    other is FilterParams &&
      runtimeType == other.runtimeType &&
      searchQuery == other.searchQuery &&
      roleId == other.roleId &&
      // ... alle Felder vergleichen
      sortBy == other.sortBy;

  @override
  int get hashCode => Object.hash(
    searchQuery, roleId, familyId, ageGroup, gender,
    paymentStatus, showOnlyActive, sortBy
  );
}
```

---

*(Aufgrund der Länge wird das Dokument hier fortgesetzt. Ich werde weitere Abschnitte hinzufügen)*

---

### 2. Familien-Management

#### 2.1 Sammelrechnung (PDF)

**Beschreibung**: PDF-Rechnung für eine ganze Familie mit allen Teilnehmern

**Features**:
- Alle Familienmitglieder in einer Rechnung
- Preis-Breakdown für jedes Mitglied
- Gesamtsumme für Familie
- SEPA-QR-Code für Gesamtbetrag
- Hinweis auf Familienrabatte

**Format**: Siehe Invoice Generator Code (bereits gelesen)

**Besonderheit**:
- Zahlungen werden sowohl auf Familien- als auch auf Teilnehmer-Ebene erfasst
- Rechnung zeigt beide Zahlungsströme:
  ```
  Gesamtsumme Familie:     500,00 €

  Zahlungen:
  - Familienzahlungen:     300,00 €  (direkt an Familie)
  - Einzelzahlungen:       150,00 €  (an einzelne Mitglieder)
  -------------------------
  Gesamt bezahlt:          450,00 €
  Noch offen:               50,00 €
  ```

---

#### 2.2 Familien-Zahlungen

**Beschreibung**: Zahlungen die für die ganze Familie gelten (nicht einzelne Mitglieder)

**Datenbankschema**:
```dart
@DataClassName('Payment')
class Payments extends Table {
  IntColumn get id => integer().autoIncrement()();
  RealColumn get amount => real()();
  DateTimeColumn get paymentDate => dateTime()();
  TextColumn get paymentMethod => text().nullable()();
  TextColumn get reference => text().nullable()();
  TextColumn get notes => text().nullable()();
  IntColumn get eventId => integer().references(Events, #id)();

  // WICHTIG: Entweder participant_id ODER family_id (nicht beide)
  IntColumn get participantId => integer().nullable().references(Participants, #id)();
  IntColumn get familyId => integer().nullable().references(Families, #id)();

  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}
```

**Logik**:
1. Payment hat ENTWEDER `participantId` ODER `familyId` (nicht beide)
2. Bei Familienzahlung: `familyId` gesetzt, `participantId` = null
3. Bei Einzelzahlung: `participantId` gesetzt, `familyId` = null

**UI-Flow**:
```
Familie-Details → Tab "Zahlungen" → Button "Zahlung erfassen"

Dialog:
┌─────────────────────────────────────┐
│ Zahlung erfassen                    │
├─────────────────────────────────────┤
│ Betrag: [_______] €                 │
│ Datum:  [DD.MM.YYYY]               │
│ Methode: [Dropdown]                 │
│   - Bar                             │
│   - Überweisung                     │
│   - PayPal                          │
│   - Sonstiges                       │
│ Referenz: [____________]            │
│ Notiz:    [____________]            │
│                                     │
│ Zahlung gilt für:                   │
│ ○ Ganze Familie                     │
│ ○ Einzelnes Mitglied: [Dropdown]    │
│   - Max Müller                      │
│   - Anna Müller                     │
│   - ...                             │
│                                     │
│ [Abbrechen]  [Speichern]            │
└─────────────────────────────────────┘
```

**Code-Beispiel**:
```dart
class PaymentFormDialog extends StatefulWidget {
  final Family family;

  @override
  _PaymentFormDialogState createState() => _PaymentFormDialogState();
}

class _PaymentFormDialogState extends State<PaymentFormDialog> {
  bool _isForWholeFamily = true;
  Participant? _selectedParticipant;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Zahlung erfassen'),
      content: SingleChildScrollView(
        child: Column(
          children: [
            // Betrag, Datum, Methode, etc. (wie üblich)

            // Spezialfall: Für wen gilt die Zahlung?
            RadioListTile<bool>(
              title: Text('Ganze Familie'),
              value: true,
              groupValue: _isForWholeFamily,
              onChanged: (value) => setState(() {
                _isForWholeFamily = value!;
                _selectedParticipant = null;
              })
            ),
            RadioListTile<bool>(
              title: Text('Einzelnes Mitglied'),
              value: false,
              groupValue: _isForWholeFamily,
              onChanged: (value) => setState(() => _isForWholeFamily = value!)
            ),

            if (!_isForWholeFamily)
              DropdownButtonFormField<Participant>(
                decoration: InputDecoration(labelText: 'Mitglied'),
                value: _selectedParticipant,
                items: widget.family.participants.map((p) {
                  return DropdownMenuItem(
                    value: p,
                    child: Text(p.fullName)
                  );
                }).toList(),
                onChanged: (value) => setState(() => _selectedParticipant = value)
              ),
          ]
        )
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text('Abbrechen')
        ),
        ElevatedButton(
          onPressed: () => _savePayment(),
          child: Text('Speichern')
        ),
      ]
    );
  }

  Future<void> _savePayment() async {
    final payment = PaymentsCompanion.insert(
      amount: _amount,
      paymentDate: _paymentDate,
      paymentMethod: Value(_paymentMethod),
      reference: Value(_reference),
      notes: Value(_notes),
      eventId: widget.family.eventId,
      // WICHTIG: Entweder familyId ODER participantId
      familyId: _isForWholeFamily ? Value(widget.family.id) : Value.absent(),
      participantId: !_isForWholeFamily && _selectedParticipant != null
        ? Value(_selectedParticipant!.id)
        : Value.absent()
    );

    await database.paymentsRepository.insert(payment);
    Navigator.pop(context);
  }
}
```

---

### 3. Zahlungs-Management

#### 3.1 Rechnungsgenerierung mit SEPA-QR-Codes

**Beschreibung**: PDF-Rechnungen mit integrierten SEPA-QR-Codes für einfache Überweisung

**SEPA-QR-Code Format**: EPC-Standard (European Payments Council)

**QR-Code Inhalt**:
```
BCD
002
1
SCT
{BIC}
{Empfängername}
{IBAN}
EUR{Betrag}


{Verwendungszweck}
```

**Zeilen-Erklärung**:
- Zeile 1: "BCD" (Service Tag)
- Zeile 2: "002" (Version)
- Zeile 3: "1" (Character Set = UTF-8)
- Zeile 4: "SCT" (SEPA Credit Transfer)
- Zeile 5: BIC (optional, kann leer sein)
- Zeile 6: Empfängername (max 70 Zeichen)
- Zeile 7: IBAN
- Zeile 8: "EUR" + Betrag (z.B. "EUR150.00")
- Zeile 9: Purpose (leer)
- Zeile 10: Structured Reference (leer)
- Zeile 11: Unstructured Reference (Verwendungszweck, max 140 Zeichen)

**Code-Beispiel**:
```dart
import 'package:qr_flutter/qr_flutter.dart';

class SEPAQRCodeService {
  static String generateSEPAString({
    required String recipientName,
    required String iban,
    required double amount,
    required String purpose,
    String? bic
  }) {
    // IBAN formatieren (Leerzeichen entfernen)
    String cleanIban = iban.replaceAll(' ', '');

    // Betrag formatieren (max 2 Dezimalstellen)
    String formattedAmount = 'EUR${amount.toStringAsFixed(2)}';

    // Empfängername kürzen wenn nötig
    String shortName = recipientName.length > 70
      ? recipientName.substring(0, 70)
      : recipientName;

    // Verwendungszweck kürzen wenn nötig
    String shortPurpose = purpose.length > 140
      ? purpose.substring(0, 140)
      : purpose;

    // SEPA String nach EPC-Standard
    return [
      'BCD',                    // Service Tag
      '002',                    // Version
      '1',                      // Character Set (1 = UTF-8)
      'SCT',                    // Identification (SEPA Credit Transfer)
      bic ?? '',                // BIC (optional)
      shortName,                // Beneficiary Name
      cleanIban,                // Beneficiary Account (IBAN)
      formattedAmount,          // Amount
      '',                       // Purpose (leer)
      '',                       // Structured Reference (leer)
      shortPurpose,             // Unstructured Reference (Verwendungszweck)
      '',                       // Beneficiary to Originator Information (leer)
    ].join('\n');
  }

  static Future<Uint8List> generateQRCodeImage({
    required String recipientName,
    required String iban,
    required double amount,
    required String purpose,
    String? bic,
    int size = 300
  }) async {
    String sepaData = generateSEPAString(
      recipientName: recipientName,
      iban: iban,
      amount: amount,
      purpose: purpose,
      bic: bic
    );

    // QR-Code als Image generieren
    final qrValidationResult = QrValidator.validate(
      data: sepaData,
      version: QrVersions.auto,
      errorCorrectionLevel: QrErrorCorrectLevel.M,
    );

    if (qrValidationResult.status == QrValidationStatus.valid) {
      final qrCode = qrValidationResult.qrCode!;

      final painter = QrPainter.withQr(
        qr: qrCode,
        gapless: true,
        errorCorrectionLevel: QrErrorCorrectLevel.M,
      );

      final picData = await painter.toImageData(size.toDouble());
      return picData!.buffer.asUint8List();
    } else {
      throw Exception('QR-Code Validierung fehlgeschlagen');
    }
  }
}
```

**Integration in PDF**:
```dart
// In InvoiceGenerator:
Future<Uint8List> generateInvoicePDF(Participant participant) async {
  // ... PDF erstellen

  // QR-Code generieren
  if (outstanding > 0) {
    final qrBytes = await SEPAQRCodeService.generateQRCodeImage(
      recipientName: settings.bankAccountHolder,
      iban: settings.bankIban,
      amount: outstanding,
      purpose: 'Teilnahmegebühr ${participant.fullName}',
      bic: settings.bankBic,
      size: 300
    );

    final qrImage = pw.MemoryImage(qrBytes);

    // QR-Code in PDF einfügen
    story.add(
      pw.Container(
        alignment: pw.Alignment.centerRight,
        child: pw.Image(qrImage, width: 100, height: 100)
      )
    );

    story.add(
      pw.Paragraph(
        text: 'Scannen Sie den QR-Code mit Ihrer Banking-App',
        style: pw.TextStyle(fontSize: 10, fontStyle: pw.FontStyle.italic)
      )
    );
  }

  // ... Rest der PDF

  return pdf.save();
}
```

---

### 4. Ausgaben-Management

#### 4.1 Beleg-Upload & Verwaltung

**Beschreibung**: Fotos/PDFs von Ausgabenbelegen hochladen, anzeigen und verwalten

**Datenbankschema**:
```dart
@DataClassName('Expense')
class Expenses extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get title => text()();
  RealColumn get amount => real()();
  TextColumn get category => text().nullable()();
  DateTimeColumn get expenseDate => dateTime().withDefault(currentDate)();
  TextColumn get description => text().nullable()();
  TextColumn get paidBy => text().nullable()();
  BoolColumn get isSettled => boolean().withDefault(const Constant(false))();
  IntColumn get eventId => integer().references(Events, #id)();

  // NEU: Beleg-Dateipfad
  TextColumn get receiptPath => text().nullable()();
  TextColumn get receiptFilename => text().nullable()();
  TextColumn get receiptMimeType => text().nullable()();  // image/jpeg, application/pdf, etc.

  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}
```

**Datei-Speicherung**:
```
{AppDocumentsDirectory}/receipts/{eventId}/{expenseId}_{timestamp}.{ext}
```

**Code-Beispiel**:
```dart
class ReceiptService {
  static Future<String> uploadReceipt(int eventId, int expenseId, File file) async {
    // App Documents Directory holen
    final appDir = await getApplicationDocumentsDirectory();
    final receiptsDir = Directory('${appDir.path}/receipts/$eventId');

    // Verzeichnis erstellen falls nicht vorhanden
    if (!await receiptsDir.exists()) {
      await receiptsDir.create(recursive: true);
    }

    // Dateiname generieren
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final extension = path.extension(file.path);
    final filename = '${expenseId}_$timestamp$extension';
    final targetPath = '${receiptsDir.path}/$filename';

    // Datei kopieren
    await file.copy(targetPath);

    return targetPath;
  }

  static Future<File?> pickReceiptFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['jpg', 'jpeg', 'png', 'pdf'],
      allowMultiple: false
    );

    if (result != null && result.files.single.path != null) {
      return File(result.files.single.path!);
    }

    return null;
  }

  static Future<File?> takeReceiptPhoto() async {
    final ImagePicker picker = ImagePicker();
    final XFile? photo = await picker.pickImage(
      source: ImageSource.camera,
      imageQuality: 85,
      maxWidth: 1920
    );

    if (photo != null) {
      return File(photo.path);
    }

    return null;
  }

  static Future<void> deleteReceipt(String path) async {
    final file = File(path);
    if (await file.exists()) {
      await file.delete();
    }
  }

  static String getMimeType(String path) {
    final extension = path.extension(path).toLowerCase();
    switch (extension) {
      case '.jpg':
      case '.jpeg':
        return 'image/jpeg';
      case '.png':
        return 'image/png';
      case '.pdf':
        return 'application/pdf';
      default:
        return 'application/octet-stream';
    }
  }
}
```

**UI-Integration**:
```dart
class ExpenseFormScreen extends ConsumerStatefulWidget {
  final Expense? expense;

  @override
  _ExpenseFormScreenState createState() => _ExpenseFormScreenState();
}

class _ExpenseFormScreenState extends ConsumerState<ExpenseFormScreen> {
  File? _receiptFile;
  String? _existingReceiptPath;

  @override
  void initState() {
    super.initState();
    if (widget.expense != null) {
      _existingReceiptPath = widget.expense!.receiptPath;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Ausgabe')),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            // ... Titel, Betrag, Kategorie, etc.

            // Beleg-Upload-Section
            Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Beleg',
                      style: Theme.of(context).textTheme.titleMedium
                    ),
                    SizedBox(height: 16),

                    // Aktueller Beleg (falls vorhanden)
                    if (_existingReceiptPath != null || _receiptFile != null)
                      _buildReceiptPreview(),

                    // Upload-Buttons
                    Row(
                      children: [
                        ElevatedButton.icon(
                          icon: Icon(Icons.camera_alt),
                          label: Text('Foto aufnehmen'),
                          onPressed: () => _takePhoto()
                        ),
                        SizedBox(width: 8),
                        ElevatedButton.icon(
                          icon: Icon(Icons.upload_file),
                          label: Text('Datei wählen'),
                          onPressed: () => _pickFile()
                        ),
                      ]
                    ),

                    if (_existingReceiptPath != null || _receiptFile != null)
                      TextButton.icon(
                        icon: Icon(Icons.delete, color: Colors.red),
                        label: Text('Beleg entfernen', style: TextStyle(color: Colors.red)),
                        onPressed: () => _removeReceipt()
                      ),
                  ]
                )
              )
            ),

            SizedBox(height: 24),

            // Speichern-Button
            ElevatedButton(
              onPressed: () => _saveExpense(),
              child: Text('Speichern')
            ),
          ]
        )
      )
    );
  }

  Widget _buildReceiptPreview() {
    final path = _receiptFile?.path ?? _existingReceiptPath!;
    final mimeType = ReceiptService.getMimeType(path);

    if (mimeType.startsWith('image/')) {
      // Bild-Vorschau
      return GestureDetector(
        onTap: () => _viewReceipt(path),
        child: Container(
          height: 200,
          margin: EdgeInsets.only(bottom: 16),
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey),
            borderRadius: BorderRadius.circular(8)
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Image.file(
              File(path),
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                return Center(child: Icon(Icons.error, size: 48));
              }
            )
          )
        )
      );
    } else if (mimeType == 'application/pdf') {
      // PDF-Icon
      return GestureDetector(
        onTap: () => _viewReceipt(path),
        child: Container(
          height: 200,
          margin: EdgeInsets.only(bottom: 16),
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey),
            borderRadius: BorderRadius.circular(8)
          ),
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.picture_as_pdf, size: 64, color: Colors.red),
                SizedBox(height: 8),
                Text('PDF-Beleg', style: TextStyle(fontSize: 16)),
                SizedBox(height: 4),
                Text(
                  path.split('/').last,
                  style: TextStyle(fontSize: 12, color: Colors.grey)
                ),
              ]
            )
          )
        )
      );
    }

    return SizedBox.shrink();
  }

  Future<void> _takePhoto() async {
    final file = await ReceiptService.takeReceiptPhoto();
    if (file != null) {
      setState(() {
        _receiptFile = file;
        _existingReceiptPath = null;
      });
    }
  }

  Future<void> _pickFile() async {
    final file = await ReceiptService.pickReceiptFile();
    if (file != null) {
      setState(() {
        _receiptFile = file;
        _existingReceiptPath = null;
      });
    }
  }

  void _removeReceipt() {
    setState(() {
      _receiptFile = null;
      _existingReceiptPath = null;
    });
  }

  void _viewReceipt(String path) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ReceiptViewerScreen(filePath: path)
      )
    );
  }

  Future<void> _saveExpense() async {
    // ... Validierung

    String? receiptPath;
    String? receiptFilename;
    String? receiptMimeType;

    // Beleg hochladen falls neu
    if (_receiptFile != null) {
      final eventId = ref.read(currentEventProvider)!.id;

      // Temporäre ID falls neue Expense
      final tempExpenseId = widget.expense?.id ?? DateTime.now().millisecondsSinceEpoch;

      receiptPath = await ReceiptService.uploadReceipt(
        eventId,
        tempExpenseId,
        _receiptFile!
      );
      receiptFilename = path.basename(receiptPath);
      receiptMimeType = ReceiptService.getMimeType(receiptPath);
    } else if (_existingReceiptPath != null) {
      // Behalten existierenden Beleg
      receiptPath = _existingReceiptPath;
      receiptFilename = widget.expense?.receiptFilename;
      receiptMimeType = widget.expense?.receiptMimeType;
    }

    // Expense speichern
    final expense = ExpensesCompanion.insert(
      title: _titleController.text,
      amount: double.parse(_amountController.text),
      category: Value(_selectedCategory),
      description: Value(_descriptionController.text),
      paidBy: Value(_paidByController.text),
      isSettled: Value(_isSettled),
      receiptPath: Value(receiptPath),
      receiptFilename: Value(receiptFilename),
      receiptMimeType: Value(receiptMimeType),
      eventId: eventId
    );

    await database.expensesRepository.insert(expense);

    Navigator.pop(context);
  }
}

class ReceiptViewerScreen extends StatelessWidget {
  final String filePath;

  const ReceiptViewerScreen({required this.filePath});

  @override
  Widget build(BuildContext context) {
    final mimeType = ReceiptService.getMimeType(filePath);

    return Scaffold(
      appBar: AppBar(
        title: Text('Beleg'),
        actions: [
          IconButton(
            icon: Icon(Icons.share),
            onPressed: () => _shareReceipt()
          ),
        ]
      ),
      body: Center(
        child: mimeType.startsWith('image/')
          ? InteractiveViewer(
              child: Image.file(File(filePath))
            )
          : mimeType == 'application/pdf'
            ? PDFView(filePath: filePath)  // Benötigt flutter_pdfview package
            : Text('Nicht unterstütztes Format')
      )
    );
  }

  Future<void> _shareReceipt() async {
    await Share.shareXFiles([XFile(filePath)]);
  }
}
```

---

*(Das Dokument ist sehr umfangreich. Ich werde weitere kritische Abschnitte hinzufügen und dann das Dokument fertigstellen)*

---

### 6. Regelwerk-Management

#### 6.1 YAML-Import von GitHub

**Beschreibung**: Regelwerke direkt von GitHub-URL importieren

**Features**:
- URL-Eingabe mit Validierung
- Automatische Konvertierung von github.com zu raw.githubusercontent.com
- Automatische Dateiname-Erkennung basierend auf Event-Typ und Jahr
- Validierung vor Import
- Automatische Rollen-Erstellung aus Regelwerk

**Automatische URL-Konstruktion**:
```
Input (Verzeichnis):
https://github.com/user/repo/tree/main/rulesets/valid/

Event-Typ: Familienfreizeit
Event-Jahr: 2024

Automatisch konstruierte URL:
https://raw.githubusercontent.com/user/repo/main/rulesets/valid/Familienfreizeiten_2024.yaml
```

**Mapping Event-Typ → Dateiname**:
```dart
Map<String, String> eventTypeToFilename = {
  'familienfreizeit': 'Familienfreizeiten',
  'kinderfreizeit': 'Kinderfreizeiten',
  'jugendfreizeit': 'Jugendfreizeiten',
  'teeniefreizeit': 'Teeniefreizeiten',
};
```

**Code-Beispiel**:
```dart
class RulesetImportService {
  static Future<Ruleset?> importFromGitHub({
    required String githubUrl,
    required int eventId,
    required Database db
  }) async {
    try {
      // URL validieren
      if (!githubUrl.startsWith('https://')) {
        throw Exception('URL muss mit https:// beginnen');
      }

      // Automatisch zu Raw-URL konvertieren
      String rawUrl = _convertToRawUrl(githubUrl);

      // YAML herunterladen
      final response = await http.get(Uri.parse(rawUrl));

      if (response.statusCode != 200) {
        throw Exception('Datei nicht gefunden (HTTP ${response.statusCode})');
      }

      String yamlContent = response.body;

      // BOM entfernen (falls vorhanden)
      if (yamlContent.startsWith('\ufeff')) {
        yamlContent = yamlContent.substring(1);
      }

      // Editor-Metadaten entfernen
      yamlContent = _cleanYaml(yamlContent);

      // YAML parsen
      final yamlMap = loadYaml(yamlContent) as Map;

      // Validieren
      _validateRuleset(yamlMap);

      // Alle anderen Rulesets deaktivieren
      await db.rulesetsRepository.deactivateAll(eventId);

      // Ruleset in Datenbank speichern
      final ruleset = RulesetsCompanion.insert(
        name: yamlMap['name'] as String,
        rulesetType: yamlMap['type'] as String,
        description: Value(yamlMap['description'] as String?),
        validFrom: _parseDate(yamlMap['valid_from']),
        validUntil: _parseDate(yamlMap['valid_until']),
        ageGroups: jsonEncode(yamlMap['age_groups']),
        roleDiscounts: Value(jsonEncode(yamlMap['role_discounts'])),
        familyDiscount: Value(jsonEncode(yamlMap['family_discount'])),
        sourceFile: Value(rawUrl),
        eventId: eventId,
        isActive: Value(true)
      );

      final rulesetId = await db.rulesetsRepository.insert(ruleset);

      // Rollen automatisch erstellen
      if (yamlMap.containsKey('role_discounts')) {
        await _createRolesFromRuleset(
          yamlMap['role_discounts'] as Map,
          eventId,
          db
        );
      }

      // Alle Teilnehmerpreise neu berechnen
      await PriceCalculator.recalculateAllPrices(db, eventId);

      return await db.rulesetsRepository.getById(rulesetId);

    } catch (e) {
      print('Fehler beim GitHub-Import: $e');
      rethrow;
    }
  }

  static String _convertToRawUrl(String url) {
    // Konvertierung:
    // Von: https://github.com/user/repo/blob/branch/path/file.yaml
    // Zu: https://raw.githubusercontent.com/user/repo/branch/path/file.yaml

    if (url.contains('raw.githubusercontent.com')) {
      return url;  // Bereits Raw-URL
    }

    return url
      .replaceAll('github.com', 'raw.githubusercontent.com')
      .replaceAll('/blob/', '/');
  }

  static String _cleanYaml(String yaml) {
    // Entferne Editor-spezifische Zeilen
    final lines = yaml.split('\n');
    final cleanedLines = lines.where((line) {
      return !line.contains('--tab-size-preference') &&
             !line.toLowerCase().contains('# editorconfig');
    }).toList();

    return cleanedLines.join('\n');
  }

  static void _validateRuleset(Map yamlMap) {
    // Pflichtfelder prüfen
    final requiredFields = ['name', 'type', 'valid_from', 'valid_until', 'age_groups'];

    for (final field in requiredFields) {
      if (!yamlMap.containsKey(field)) {
        throw Exception('Pflichtfeld fehlt: $field');
      }
    }

    // Datumsformat prüfen
    try {
      _parseDate(yamlMap['valid_from']);
      _parseDate(yamlMap['valid_until']);
    } catch (e) {
      throw Exception('Ungültiges Datumsformat (erwartet: YYYY-MM-DD)');
    }

    // age_groups validieren
    final ageGroups = yamlMap['age_groups'];
    if (ageGroups is! List || ageGroups.isEmpty) {
      throw Exception('age_groups muss eine nicht-leere Liste sein');
    }

    for (final group in ageGroups) {
      if (!group.containsKey('min_age') ||
          !group.containsKey('max_age') ||
          !group.containsKey('base_price')) {
        throw Exception('age_groups: Jede Gruppe benötigt min_age, max_age und base_price');
      }
    }
  }

  static DateTime _parseDate(dynamic value) {
    if (value is DateTime) return value;

    final parts = value.toString().split('-');
    return DateTime(
      int.parse(parts[0]),  // Jahr
      int.parse(parts[1]),  // Monat
      int.parse(parts[2])   // Tag
    );
  }

  static Future<void> _createRolesFromRuleset(
    Map roleDiscounts,
    int eventId,
    Database db
  ) async {
    for (final entry in roleDiscounts.entries) {
      final roleName = entry.key as String;
      final roleConfig = entry.value as Map;

      // Prüfen ob Rolle bereits existiert
      final existing = await db.rolesRepository.getByName(roleName, eventId);

      if (existing == null) {
        // Neue Rolle erstellen
        final role = RolesCompanion.insert(
          name: roleName,
          displayName: roleConfig['display_name'] as String? ?? _capitalize(roleName),
          description: Value(roleConfig['description'] as String?),
          eventId: eventId
        );

        await db.rolesRepository.insert(role);
      }
    }
  }

  static String _capitalize(String text) {
    if (text.isEmpty) return text;
    return text[0].toUpperCase() + text.substring(1);
  }

  /// Automatischer Import bei Event-Erstellung
  static Future<bool> tryAutoImportForEvent({
    required Event event,
    required String? defaultGithubRepo,
    required Database db
  }) async {
    if (defaultGithubRepo == null || defaultGithubRepo.isEmpty) {
      return false;
    }

    try {
      // Erwarteten Dateinamen generieren
      final year = event.startDate.year;
      final filename = _getFilenameForEventType(event.eventType, year);

      if (filename == null) return false;

      // URL konstruieren
      final url = defaultGithubRepo.endsWith('/')
        ? '$defaultGithubRepo$filename'
        : '$defaultGithubRepo/$filename';

      // Import versuchen
      await importFromGitHub(
        githubUrl: url,
        eventId: event.id,
        db: db
      );

      return true;
    } catch (e) {
      print('Auto-Import fehlgeschlagen: $e');
      return false;
    }
  }

  static String? _getFilenameForEventType(String eventType, int year) {
    const mapping = {
      'familienfreizeit': 'Familienfreizeiten',
      'kinderfreizeit': 'Kinderfreizeiten',
      'jugendfreizeit': 'Jugendfreizeiten',
      'teeniefreizeit': 'Teeniefreizeiten',
    };

    final prefix = mapping[eventType.toLowerCase()];
    if (prefix == null) return null;

    return '${prefix}_$year.yaml';
  }
}
```

---

### 8. Aufgaben-System (automatisch generiert)

**Beschreibung**: Das System generiert automatisch 14 verschiedene Aufgabentypen basierend auf Datenbank-Zustand

**Wichtig**: Aufgaben werden NICHT in der Datenbank gespeichert (außer wenn als "erledigt" markiert). Sie werden bei jedem Laden dynamisch berechnet.

**Task-Datenbank** (nur für erledigte Tasks):
```dart
@DataClassName('Task')
class Tasks extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get taskType => text()();  // z.B. "bildung_teilhabe"
  IntColumn get referenceId => integer()();  // ID der referenzierten Entität (Participant, Expense, etc.)
  BoolColumn get isCompleted => boolean().withDefault(const Constant(false))();
  DateTimeColumn get completedAt => dateTime().nullable()();
  TextColumn get completionNote => text().nullable()();  // Notiz beim Erledigen
  IntColumn get eventId => integer().references(Events, #id)();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}
```

**Die 14 Aufgabentypen**:

#### 1. Bildung & Teilhabe (bildung_teilhabe)
**Trigger**: Teilnehmer hat `bildung_teilhabe_id` gesetzt
**Beschreibung**: "BuT-Nummer: {id}"
**Link**: `/participants/{id}`
**Action**: Antrag bei zuständiger Stelle einreichen

#### 2. Ausgaben-Erstattung (expense_reimbursement)
**Trigger**: Ausgabe mit `is_settled = false` und `paid_by != null`
**Beschreibung**: "{amount}€ - Bezahlt von: {paid_by}"
**Link**: `/expenses/{id}`
**Action**: Ausgabe erstatten, dann `is_settled = true` setzen

#### 3. Offene Zahlungen (outstanding_payment)
**Trigger**: Teilnehmer mit `final_price > sum(payments.amount)`
**Beschreibung**: "Ausstehend: {outstanding}€ (von {final_price}€)"
**Link**: `/participants/{id}`
**Action**: Zahlung erfassen

#### 4. Manuelle Preise prüfen (manual_price_override)
**Trigger**: Teilnehmer mit `manual_price_override != null`
**Beschreibung**: "Manueller Preis: {manual_price}€ (statt {calculated_price}€)"
**Link**: `/participants/{id}`
**Action**: Prüfen ob manueller Preis noch korrekt ist

#### 5. Überfällige Zahlungen (overdue_payment)
**Trigger**: `today >= event.start_date - 14 days` UND offene Zahlungen
**Beschreibung**: "Ausstehend: {outstanding}€ - ÜBERFÄLLIG!"
**Link**: `/participants/{id}`
**Action**: Dringend Zahlung anfordern

#### 6. Zuschuss-Differenzen Rollen (income_subsidy_mismatch)
**Trigger**: `sum(incomes where role_id = X) != sum(expected_role_discounts for role X)`
**Beschreibung**: "Zuschuss: {total}€ | Rabatte: {expected}€ | Differenz: {diff}€"
**Link**: `/incomes`
**Action**: Zuschuss beantragen oder Rabatte korrigieren

**Berechnung**:
```dart
// Für jede Rolle:
// 1. Summe aller Incomes mit dieser role_id
double totalSubsidy = incomes
  .where((i) => i.roleId == roleId)
  .fold(0.0, (sum, i) => sum + i.amount);

// 2. Erwartete Rabatte berechnen
double expectedDiscounts = 0.0;
for (var participant in participants.where((p) => p.roleId == roleId)) {
  double basePrice = PriceCalculator.getBasePrice(participant.ageAtEvent, ruleset);
  double discountPercent = ruleset.roleDiscounts[role.name]['discount_percent'];
  expectedDiscounts += basePrice * (discountPercent / 100);
}

// 3. Differenz
double difference = totalSubsidy - expectedDiscounts;

// 4. Task erstellen wenn |difference| > 1.0€
if (difference.abs() > 1.0) {
  tasks.add(Task(
    type: 'income_subsidy_mismatch',
    referenceId: roleId,
    title: 'Zuschuss-Differenz: ${role.displayName}',
    description: 'Zuschuss: ${totalSubsidy.toStringAsFixed(2)}€ | Rabatte: ${expectedDiscounts.toStringAsFixed(2)}€ | Differenz: ${difference.abs().toStringAsFixed(2)}€ (${difference > 0 ? "zu viel" : "zu wenig"})',
    link: '/incomes'
  ));
}
```

#### 7. Zuschuss-Differenzen Familien (family_subsidy_mismatch)
**Trigger**: `sum(incomes where description like '%Kinderzuschuss%') != sum(expected_family_discounts)`
**Beschreibung**: "Zuschuss: {total}€ | Familienrabatte: {expected}€ | Differenz: {diff}€"
**Link**: `/incomes`
**Action**: Kinderzuschuss beantragen

**Berechnung**:
```dart
// 1. Summe aller "Kinderzuschuss" Incomes
double totalFamilySubsidy = incomes
  .where((i) => i.description?.contains('Kinderzuschuss') ?? false)
  .fold(0.0, (sum, i) => sum + i.amount);

// 2. Erwartete Familienrabatte berechnen
double expectedFamilyDiscounts = 0.0;

// Gruppiere Kinder nach Familie
Map<int, List<Participant>> familiesMap = {};
for (var p in participants.where((p) => p.ageAtEvent < 18 && p.familyId != null)) {
  if (!familiesMap.containsKey(p.familyId)) {
    familiesMap[p.familyId!] = [];
  }
  familiesMap[p.familyId!].add(p);
}

// Für jede Familie:
for (var familyChildren in familiesMap.values) {
  // Nach Geburtsdatum sortieren (ältestes zuerst)
  familyChildren.sort((a, b) => a.birthDate.compareTo(b.birthDate));

  for (int i = 0; i < familyChildren.length; i++) {
    var child = familyChildren[i];
    int childPosition = i + 1;  // 1 = ältestes, 2 = zweites, etc.

    double basePrice = PriceCalculator.getBasePrice(child.ageAtEvent, ruleset);
    double discountPercent = PriceCalculator.getFamilyDiscount(
      child.ageAtEvent,
      childPosition,
      ruleset.familyDiscount
    );

    expectedFamilyDiscounts += basePrice * (discountPercent / 100);
  }
}

// 3. Differenz
double difference = totalFamilySubsidy - expectedFamilyDiscounts;

// 4. Task erstellen
if (difference.abs() > 1.0) {
  tasks.add(Task(...));
}
```

#### 8. Rollen-Überschreitungen (role_count_exceeded)
**Trigger**: `count(participants where role_id = X) > ruleset.role_discounts[role].max_count`
**Beschreibung**: "Aktuell: {current} | Maximum: {max} | Überschreitung: {excess}"
**Link**: `/participants?role_id={id}`
**Action**: Teilnehmer anderen Rollen zuweisen oder max_count erhöhen

#### 9. Geburtstagskinder (birthday_gifts)
**Trigger**: Teilnehmer haben Geburtstag während `event.start_date` bis `event.end_date`
**Beschreibung**: "Geburtstagskinder: {name1} (DD.MM.), {name2} (DD.MM.), ..."
**Link**: `/participants`
**Action**: Geschenke besorgen

**Berechnung**:
```dart
List<Map> birthdayChildren = [];

for (var p in participants) {
  if (p.birthDate == null) continue;

  // Geburtstag im Event-Jahr konstruieren
  DateTime birthdayThisYear = DateTime(
    event.startDate.year,
    p.birthDate.month,
    p.birthDate.day
  );

  // Prüfen ob zwischen start_date und end_date
  if (birthdayThisYear.isAfter(event.startDate.subtract(Duration(days: 1))) &&
      birthdayThisYear.isBefore(event.endDate.add(Duration(days: 1)))) {
    birthdayChildren.add({
      'name': p.fullName,
      'date': birthdayThisYear,
      'age': p.ageAtEvent + 1  // Alter nach Geburtstag
    });
  }
}

if (birthdayChildren.isNotEmpty) {
  // Nach Datum sortieren
  birthdayChildren.sort((a, b) => a['date'].compareTo(b['date']));

  String namesList = birthdayChildren
    .map((c) => '${c['name']} (${DateFormat('dd.MM.').format(c['date'])})')
    .join(', ');

  tasks.add(Task(
    type: 'birthday_gifts',
    referenceId: event.id,
    title: 'Geschenke für ${birthdayChildren.length} Geburtstagskind(er)',
    description: 'Geburtstagskinder während der Freizeit: $namesList',
    link: '/participants'
  ));
}
```

#### 10. Küchenteam-Geschenk (kitchen_team_gift)
**Trigger**: Teilnehmer mit Rolle "Küche" (oder "kueche", "kitchen")
**Beschreibung**: "Küchenteam-Mitglieder: {name1}, {name2}, ..."
**Link**: `/participants?role_id={kitchen_role_id}`
**Action**: Dankeschön-Geschenk für Küchenteam besorgen

#### 11. Familienfreizeit Nicht-Mitglieder (familienfreizeit_non_member_check)
**Trigger**: `event.event_type = 'familienfreizeit'`
**Beschreibung**: "Prüfen ob Kinder von Nicht-Gemeindemitgliedern mitfahren"
**Link**: `/participants`
**Action**: Manuell prüfen - Zuschüsse nur für Mitglieder

---

**Task-UI-Komponente**:
```dart
class TasksListScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tasks = ref.watch(generatedTasksProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text('Offene Aufgaben (${tasks.length})'),
      ),
      body: tasks.isEmpty
        ? Center(child: Text('Keine offenen Aufgaben! 🎉'))
        : ListView.builder(
            itemCount: tasks.length,
            itemBuilder: (context, index) {
              return TaskListTile(task: tasks[index]);
            }
          )
    );
  }
}

class TaskListTile extends ConsumerWidget {
  final GeneratedTask task;

  const TaskListTile({required this.task});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: ListTile(
        leading: _getIcon(task.type),
        title: Text(task.title),
        subtitle: Text(task.description),
        trailing: IconButton(
          icon: Icon(Icons.check_circle_outline),
          onPressed: () => _completeTask(context, ref, task)
        ),
        onTap: () {
          // Navigation zum Link
          context.go(task.link);
        }
      )
    );
  }

  Widget _getIcon(String type) {
    switch (type) {
      case 'bildung_teilhabe':
        return Icon(Icons.school, color: Colors.blue);
      case 'expense_reimbursement':
        return Icon(Icons.attach_money, color: Colors.green);
      case 'outstanding_payment':
      case 'overdue_payment':
        return Icon(Icons.payment, color: Colors.orange);
      case 'income_subsidy_mismatch':
      case 'family_subsidy_mismatch':
        return Icon(Icons.account_balance, color: Colors.purple);
      case 'role_count_exceeded':
        return Icon(Icons.group, color: Colors.red);
      case 'birthday_gifts':
        return Icon(Icons.cake, color: Colors.pink);
      case 'kitchen_team_gift':
        return Icon(Icons.restaurant, color: Colors.brown);
      default:
        return Icon(Icons.task, color: Colors.grey);
    }
  }

  Future<void> _completeTask(BuildContext context, WidgetRef ref, GeneratedTask task) async {
    // Dialog für Notiz
    final note = await showDialog<String>(
      context: context,
      builder: (context) => _CompleteTaskDialog(task: task)
    );

    if (note != null) {
      final database = ref.read(databaseProvider);

      // Task in DB speichern
      await database.tasksRepository.insert(
        TasksCompanion.insert(
          taskType: task.type,
          referenceId: task.referenceId,
          isCompleted: Value(true),
          completionNote: Value(note),
          eventId: task.eventId
        )
      );

      // Spezielle Actions für bestimmte Task-Typen
      if (task.type == 'expense_reimbursement') {
        // Expense als erstattet markieren
        final expense = await database.expensesRepository.getById(task.referenceId);
        if (expense != null) {
          await database.expensesRepository.update(
            expense.copyWith(isSettled: true)
          );
        }
      } else if (task.type == 'outstanding_payment') {
        // Optional: Automatisch Zahlung erstellen
        final participant = await database.participantsRepository.getById(task.referenceId);
        if (participant != null) {
          // Offenen Betrag berechnen
          final payments = await database.paymentsRepository.getByParticipant(participant.id);
          final totalPaid = payments.fold(0.0, (sum, p) => sum + p.amount);
          final outstanding = participant.final_price - totalPaid;

          if (outstanding > 0.01) {
            // Zahlung erstellen
            await database.paymentsRepository.insert(
              PaymentsCompanion.insert(
                amount: outstanding,
                paymentDate: DateTime.now(),
                paymentMethod: Value('Automatisch'),
                reference: Value('Aufgabe erledigt: ${participant.fullName}'),
                notes: Value(note),
                eventId: participant.eventId,
                participantId: Value(participant.id)
              )
            );
          }
        }
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Aufgabe als erledigt markiert'))
      );
    }
  }
}

class _CompleteTaskDialog extends StatefulWidget {
  final GeneratedTask task;

  const _CompleteTaskDialog({required this.task});

  @override
  _CompleteTaskDialogState createState() => _CompleteTaskDialogState();
}

class _CompleteTaskDialogState extends State<_CompleteTaskDialog> {
  final _noteController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Aufgabe erledigen'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            widget.task.title,
            style: TextStyle(fontWeight: FontWeight.bold)
          ),
          SizedBox(height: 8),
          Text(widget.task.description),
          SizedBox(height: 16),
          TextField(
            controller: _noteController,
            decoration: InputDecoration(
              labelText: 'Notiz (optional)',
              hintText: 'Was wurde erledigt?',
              border: OutlineInputBorder()
            ),
            maxLines: 3
          ),
        ]
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text('Abbrechen')
        ),
        ElevatedButton(
          onPressed: () => Navigator.pop(context, _noteController.text),
          child: Text('Erledigt')
        ),
      ]
    );
  }
}

// Provider für generierte Tasks
final generatedTasksProvider = StreamProvider<List<GeneratedTask>>((ref) async* {
  final database = ref.watch(databaseProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    yield [];
    return;
  }

  // Erledigte Tasks aus DB laden
  final completedTasks = await database.tasksRepository.getCompleted(currentEvent.id);
  final completedSet = completedTasks.map((t) => '${t.taskType}_${t.referenceId}').toSet();

  // Tasks generieren
  final taskGenerator = TaskGenerator(database, currentEvent);
  final tasks = await taskGenerator.generateAllTasks();

  // Erledigte Tasks rausfiltern
  final openTasks = tasks.where((t) {
    return !completedSet.contains('${t.type}_${t.referenceId}');
  }).toList();

  yield openTasks;
});

class GeneratedTask {
  final String type;
  final int referenceId;
  final int eventId;
  final String title;
  final String description;
  final String link;

  GeneratedTask({
    required this.type,
    required this.referenceId,
    required this.eventId,
    required this.title,
    required this.description,
    required this.link
  });
}

class TaskGenerator {
  final Database db;
  final Event event;

  TaskGenerator(this.db, this.event);

  Future<List<GeneratedTask>> generateAllTasks() async {
    List<GeneratedTask> tasks = [];

    // 1. Bildung & Teilhabe
    tasks.addAll(await _generateBildungTeilhabeTasks());

    // 2. Expense Reimbursement
    tasks.addAll(await _generateExpenseReimbursementTasks());

    // 3. Outstanding Payments
    tasks.addAll(await _generateOutstandingPaymentTasks());

    // 4. Manual Price Override
    tasks.addAll(await _generateManualPriceOverrideTasks());

    // 5. Overdue Payments
    if (DateTime.now().isAfter(event.startDate.subtract(Duration(days: 14)))) {
      tasks.addAll(await _generateOverduePaymentTasks());
    }

    // 6. Income Subsidy Mismatch
    tasks.addAll(await _generateIncomeSubsidyMismatchTasks());

    // 7. Family Subsidy Mismatch
    tasks.addAll(await _generateFamilySubsidyMismatchTasks());

    // 8. Role Count Exceeded
    tasks.addAll(await _generateRoleCountExceededTasks());

    // 9. Birthday Gifts
    tasks.addAll(await _generateBirthdayGiftsTasks());

    // 10. Kitchen Team Gift
    tasks.addAll(await _generateKitchenTeamGiftTask());

    // 11. Familienfreizeit Non-Member Check
    if (event.eventType.toLowerCase() == 'familienfreizeit') {
      tasks.add(_generateFamilienfreizeitNonMemberCheckTask());
    }

    return tasks;
  }

  Future<List<GeneratedTask>> _generateBildungTeilhabeTasks() async {
    final participants = await db.participantsRepository.getWithBuT(event.id);

    return participants.map((p) {
      return GeneratedTask(
        type: 'bildung_teilhabe',
        referenceId: p.id,
        eventId: event.id,
        title: p.fullName,
        description: 'BuT-Nummer: ${p.bildungTeilhabeId}',
        link: '/participants/${p.id}'
      );
    }).toList();
  }

  // ... weitere _generate Methoden für jeden Task-Typ
}
```

---

## Business Logic & Berechnungen

### Preisberechnung (PriceCalculator)

**Vollständige Logik** (bereits in TECHNICAL_README.md dokumentiert, aber hier nochmal komplett):

```dart
class PriceCalculator {
  /// Berechnet den Preis für einen Teilnehmer
  ///
  /// Formel:
  /// Endpreis = Basispreis - Rollenrabatt - Familienrabatt - Manueller Rabatt
  ///
  /// WICHTIG: Rabatte werden NICHT gestapelt!
  /// Alle Rabatte werden vom Basispreis berechnet.
  ///
  /// Beispiel:
  /// Basispreis: 100€
  /// Rollenrabatt: 50% (= 50€)
  /// Familienrabatt: 20% (= 20€)
  /// Endpreis: 100€ - 50€ - 20€ = 30€
  static double calculatePrice({
    required int age,
    required String? roleName,
    required Map<String, dynamic> ruleset,
    required int familyChildPosition
  }) {
    // 1. Basispreis aus Altersgruppen
    double basePrice = _getBasePriceByAge(age, ruleset['age_groups']);

    // 2. Rollenrabatt (vom Basispreis)
    double roleDiscountPercent = roleName != null
      ? _getRoleDiscount(roleName, ruleset['role_discounts'])
      : 0.0;
    double roleDiscountAmount = basePrice * (roleDiscountPercent / 100);

    // 3. Familienrabatt (vom Basispreis, nicht gestapelt!)
    // Nur für Kinder unter 18
    double familyDiscountPercent = age < 18
      ? _getFamilyDiscount(age, familyChildPosition, ruleset['family_discount'])
      : 0.0;
    double familyDiscountAmount = basePrice * (familyDiscountPercent / 100);

    // 4. Endpreis
    double finalPrice = basePrice - roleDiscountAmount - familyDiscountAmount;

    return max(0.0, finalPrice);  // Nie negativ
  }

  static double _getBasePriceByAge(int age, List<dynamic> ageGroups) {
    for (var group in ageGroups) {
      int minAge = group['min_age'] ?? 0;
      int maxAge = group['max_age'] ?? 999;

      if (age >= minAge && age <= maxAge) {
        return (group['base_price'] ?? 0.0).toDouble();
      }
    }

    return 0.0;  // Keine passende Altersgruppe
  }

  static double _getRoleDiscount(String roleName, Map<String, dynamic>? roleDiscounts) {
    if (roleDiscounts == null) return 0.0;

    // Case-insensitive Suche
    final roleNameLower = roleName.toLowerCase();

    for (var entry in roleDiscounts.entries) {
      if (entry.key.toLowerCase() == roleNameLower) {
        return (entry.value['discount_percent'] ?? 0.0).toDouble();
      }
    }

    return 0.0;
  }

  static double _getFamilyDiscount(
    int age,
    int childPosition,
    Map<String, dynamic>? familyDiscount
  ) {
    if (familyDiscount == null || !(familyDiscount['enabled'] ?? false)) {
      return 0.0;
    }

    // Familienrabatte gelten NUR für Kinder unter 18
    if (age >= 18) return 0.0;

    // Rabatt basierend auf Position in Familie
    switch (childPosition) {
      case 1:  // Erstes Kind (ältestes)
        return (familyDiscount['first_child_percent'] ?? 0.0).toDouble();
      case 2:  // Zweites Kind
        return (familyDiscount['second_child_percent'] ?? 0.0).toDouble();
      default:  // Drittes und weitere Kinder (jüngstes)
        return (familyDiscount['third_plus_child_percent'] ?? 0.0).toDouble();
    }
  }

  /// Berechnet die Position eines Kindes in der Familie
  ///
  /// Sortierung: Nach Geburtsdatum (ältestes = 1)
  static Future<int> getFamilyChildPosition(
    Participant participant,
    Database db
  ) async {
    if (participant.familyId == null) return 1;

    // Alle Kinder der Familie (unter 18) holen
    final siblings = await db.participantsRepository.getByFamily(
      participant.familyId!,
      participant.eventId
    );

    // Nach Geburtsdatum sortieren (ältestes zuerst)
    siblings.sort((a, b) => a.birthDate.compareTo(b.birthDate));

    // Position finden
    for (int i = 0; i < siblings.length; i++) {
      if (siblings[i].id == participant.id) {
        return i + 1;  // 1-basiert
      }
    }

    return 1;  // Fallback
  }

  /// Neuberechnung aller Preise bei Regelwerk-Wechsel
  ///
  /// WICHTIG: Teilnehmer mit manual_price_override werden NICHT neu berechnet!
  static Future<int> recalculateAllPrices(Database db, int eventId) async {
    final participants = await db.participantsRepository.getAll(eventId);
    int updatedCount = 0;

    for (var participant in participants) {
      // Überspringe manuelle Preise
      if (participant.manualPriceOverride != null) continue;

      // Neuen Preis berechnen
      final newPrice = await calculatePriceFromDB(
        participant: participant,
        db: db
      );

      // Aktualisieren wenn geändert
      if ((newPrice - participant.calculatedPrice).abs() > 0.01) {
        await db.participantsRepository.update(
          participant.copyWith(calculatedPrice: newPrice)
        );
        updatedCount++;
      }
    }

    return updatedCount;
  }

  static Future<double> calculatePriceFromDB({
    required Participant participant,
    required Database db
  }) async {
    // Event laden
    final event = await db.eventsRepository.getById(participant.eventId);
    if (event == null) return 0.0;

    // Aktives Regelwerk laden
    final ruleset = await db.rulesetsRepository.getActive(participant.eventId);
    if (ruleset == null) return 0.0;

    // Alter berechnen
    final age = _calculateAge(participant.birthDate, event.startDate);

    // Rolle laden
    String? roleName;
    if (participant.roleId != null) {
      final role = await db.rolesRepository.getById(participant.roleId!);
      roleName = role?.name;
    }

    // Familien-Position ermitteln
    final familyPosition = await getFamilyChildPosition(participant, db);

    // Preis berechnen
    return calculatePrice(
      age: age,
      roleName: roleName,
      ruleset: {
        'age_groups': jsonDecode(ruleset.ageGroups),
        'role_discounts': ruleset.roleDiscounts != null
          ? jsonDecode(ruleset.roleDiscounts!)
          : null,
        'family_discount': ruleset.familyDiscount != null
          ? jsonDecode(ruleset.familyDiscount!)
          : null
      },
      familyChildPosition: familyPosition
    );
  }

  static int _calculateAge(DateTime birthDate, DateTime eventDate) {
    int age = eventDate.year - birthDate.year;

    // Geburtstag noch nicht gehabt?
    if (eventDate.month < birthDate.month ||
        (eventDate.month == birthDate.month && eventDate.day < birthDate.day)) {
      age--;
    }

    return age;
  }
}
```

---

## Zusammenfassung der fehlenden Features

**Priorität 1 (Kritisch)**:
1. ✅ Teilnehmer Excel-Import/Export
2. ✅ PDF-Rechnungsgenerierung mit SEPA-QR-Codes
3. ✅ Regelwerk GitHub-Import
4. ✅ Automatisches Aufgaben-System (14 Typen)
5. ✅ Beleg-Upload für Ausgaben
6. ✅ Dashboard-Diagramme (5 Charts)

**Priorität 2 (Wichtig)**:
7. ✅ Erweiterte Filter & Suche
8. ✅ Zuschuss-Berechnungen (Kassenstand)
9. ✅ Familien-Zahlungen
10. ✅ Kategorien-Management (Settings)
11. ✅ PDF-Export Teilnehmerliste

**Priorität 3 (Nice-to-have)**:
12. ✅ QR-Codes für Teilnehmer
13. ✅ Preis-Breakdown-Ansicht
14. ✅ Regelwerk YAML-Editor
15. ✅ Verzeichnis-Scanner für Regelwerke

---

**Dieses Dokument soll einer KI ermöglichen, ALLE fehlenden Features 1:1 zu implementieren.**

**Nächste Schritte**:
1. Features nach Priorität abarbeiten
2. Jeden Feature-Block einzeln implementieren
3. Tests für Berechnungen schreiben
4. UI/UX-Patterns aus Python-App übernehmen
5. Nach Fertigstellung: Vollständiger Feature-Vergleich

**Ende der Feature-Spezifikation**
