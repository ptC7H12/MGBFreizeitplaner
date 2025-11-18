# Freizeit-Kassen-System

Ein Web-basiertes Kassensystem für Kinder-, Jugend- und Familienfreizeiten mit Teilnehmerverwaltung, flexibler Preisgestaltung und Finanz-Tracking.

## Features

### Teilnehmerverwaltung
- **Vollständige CRUD-Operationen**: Erstellen, Anzeigen, Bearbeiten und Löschen von Teilnehmern
- **Umfassende Datenerfassung**: Persönliche Daten, medizinische Hinweise, Allergien, Bildung & Teilhabe
- **Live-Preisvorschau**: Automatische Preisberechnung beim Eingeben der Daten (HTMX)
- **Manuelle Preisanpassungen**: Rabatte und individuelle Preisüberschreibungen möglich
- **Pydantic-Validierung**: Automatische Validierung aller Eingaben (E-Mail, Datum, Beträge)

### Familienverwaltung
- **Familien-Gruppierung**: Mehrere Teilnehmer zu Familien zusammenfassen
- **Automatischer Familienrabatt**: Geschwisterrabatt wird automatisch berechnet
- **Sammelrechnungen**: Rechnungserstellung für ganze Familien
- **Zahlungsübersicht**: Gesamtübersicht über Familienzahlungen

### Regelwerk-System
- **YAML-basierte Preisregeln**: Flexible Definition von Preisstrukturen
- **Altersklassen**: Automatische Preiszuweisung nach Alter
- **Rollenrabatte**: Rabatte für Betreuer, Küchenpersonal, etc.
- **Familienrabatte**: Gestaffelte Rabatte für mehrere Kinder
- **YAML Export/Import**: Regelwerke exportieren, manuell bearbeiten und re-importieren
- **Live-Editor**: Regelwerke direkt im Browser als YAML bearbeiten

### Finanz-Tracking
- **Zahlungsverwaltung**: Erfassung von Teilnehmer- und Familienzahlungen
- **Ausgabenverwaltung**: Tracking aller Ausgaben mit Kategorien und Belegnummern
- **Dashboard**: Übersicht über Einnahmen, Ausgaben und offene Beträge
- **PDF-Rechnungen**: Automatische Rechnungsgenerierung mit ReportLab
- **Zahlungsstatus**: Echtzeit-Übersicht über bezahlte und offene Beträge

### Einstellungssystem
- **Event-spezifische Konfiguration**: Separate Einstellungen pro Veranstaltung
- **Bankdaten-Verwaltung**: Konfigurierbare IBAN, BIC, Kontoinhaber
- **Rechnungs-Anpassung**: Eigene Organisation, Adresse, Fußzeilen
- **IBAN/BIC-Validierung**: Automatische Prüfung der Bankdaten-Formate

### Fehlerbehandlung & Logging
- **Zentralisiertes Error-Handling**: Einheitliche Fehlerbehandlung über alle Router
- **Flash-Message-System**: Session-basierte Benutzer-Benachrichtigungen
- **Strukturiertes Logging**: Detailliertes Logging aller Operationen
- **Benutzerfreundliche Fehlermeldungen**: Verständliche Meldungen statt technischer Fehler

### Benutzeroberfläche
- **Responsive Design**: Tailwind CSS für mobile und Desktop-Nutzung
- **HTMX**: Dynamische Updates ohne Full-Page-Reload
- **Flash-Messages**: Visuelles Feedback für alle Aktionen (Erfolg, Fehler, Warnung)
- **Moderne Icons**: Heroicons für klare visuelle Kommunikation

## Tech-Stack

- **Backend**: Python 3.11+ mit FastAPI
- **Frontend**: HTMX + Tailwind CSS (Server-Side Rendering)
- **Datenbank**: SQLite mit SQLAlchemy ORM
- **Validierung**: Pydantic für Input-Validierung
- **PDF-Generierung**: ReportLab für Rechnungen

## Installation

### 🎯 Option 1: Standalone Version für Windows ⭐ **NEU** (Empfohlen für Windows-Benutzer)

**Komplett ohne Installation - Python ist bereits dabei!**

#### Windows
1. [Download Windows Standalone ZIP](../../releases) herunterladen (~60 MB)
2. ZIP entpacken
3. **Doppelklick auf `start.bat`**
4. Fertig! Browser öffnet sich automatisch unter http://localhost:8000

**Voraussetzungen:** KEINE! Python ist enthalten.

**Perfekt für:** Nicht-technische Benutzer, Jugendgruppen, schnelle Installation

---

**Hinweis für macOS/Linux:** Für diese Systeme empfehlen wir die Portable-Version (Option 2) - sie ist kleiner, schneller und diese Systeme haben oft Python bereits installiert.

---

### 💾 Option 2: Portable Version ⭐ (Empfohlen für macOS/Linux)

**Kleinere Download-Größe (~5 MB), Python muss vorinstalliert sein**

#### macOS
1. [Download macOS Portable ZIP](../../releases) herunterladen (~5 MB)
2. ZIP entpacken
3. **Doppelklick auf `start.sh`** (oder im Terminal: `./start.sh`)
4. Fertig! Browser öffnet sich automatisch unter http://localhost:8000

**Voraussetzung:** Python 3.11+ installieren via `brew install python@3.11`

#### Linux
1. [Download Linux Portable ZIP](../../releases) herunterladen (~5 MB)
2. ZIP entpacken
3. Im Terminal: `./start.sh`
4. Fertig! Browser öffnet sich automatisch unter http://localhost:8000

**Voraussetzung:** Python 3.11+ (z.B. `sudo apt install python3.11`)

#### Windows (Alternative zur Standalone-Version)
1. [Download Windows Portable ZIP](../../releases) herunterladen (~5 MB)
2. ZIP entpacken
3. **Doppelklick auf `start.bat`**
4. Fertig! Browser öffnet sich automatisch unter http://localhost:8000

**Voraussetzung:** Python 3.11+ von [python.org](https://www.python.org/downloads/)
⚠️ Bei Installation "Add Python to PATH" aktivieren!

---

### 💻 Option 3: Manuelle Installation (Entwickler)

**Für Entwickler die am Code arbeiten möchten**

1. Repository klonen und in Verzeichnis wechseln:
```bash
git clone <repository-url>
cd MGBFreizeitplaner
```

2. Virtual Environment erstellen und aktivieren:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows
```

3. Dependencies installieren:
```bash
pip install -r requirements.txt
```

4. Umgebungsvariablen konfigurieren:
```bash
cp .env.example .env
# .env bei Bedarf anpassen
```

5. Anwendung starten:
```bash
python -m app.main
# oder
uvicorn app.main:app --reload
```

6. Anwendung aufrufen:
```
http://localhost:8000
```

---

## Erste Schritte

Nach der Installation:

1. **Regelwerk erstellen**: Navigiere zu "Regelwerke" und importiere ein YAML-Regelwerk oder erstelle ein neues
2. **Event anlegen**: Erstelle deine erste Veranstaltung (z.B. "Kinderfreizeit 2024")
3. **Einstellungen konfigurieren**: Unter "Einstellungen" Bankdaten und Organisation eingeben
4. **Teilnehmer erfassen**: Füge Teilnehmer hinzu - Preise werden automatisch berechnet
5. **Zahlungen erfassen**: Verfolge eingehende Zahlungen und erstelle Rechnungen

## Projektstruktur

```
MGBFreizeitplaner/
├── app/
│   ├── models/              # SQLAlchemy Datenmodelle
│   │   ├── event.py         # Veranstaltungen
│   │   ├── participant.py   # Teilnehmer
│   │   ├── family.py        # Familien
│   │   ├── payment.py       # Zahlungen
│   │   ├── expense.py       # Ausgaben
│   │   ├── ruleset.py       # Regelwerke
│   │   └── setting.py       # Einstellungen
│   ├── routers/             # FastAPI Router (Endpoints)
│   │   ├── participants.py  # Teilnehmer-Verwaltung
│   │   ├── families.py      # Familien-Verwaltung
│   │   ├── payments.py      # Zahlungs-Verwaltung
│   │   ├── expenses.py      # Ausgaben-Verwaltung
│   │   ├── rulesets.py      # Regelwerk-Verwaltung
│   │   └── settings.py      # Einstellungs-Verwaltung
│   ├── services/            # Business Logic
│   │   ├── price_calculator.py    # Preisberechnung
│   │   ├── ruleset_parser.py      # YAML-Parsing
│   │   └── invoice_generator.py   # PDF-Rechnungen
│   ├── utils/               # Hilfsfunktionen
│   │   ├── error_handler.py # Zentrales Error-Handling
│   │   └── flash.py         # Flash-Message-System
│   ├── templates/           # Jinja2 HTML-Templates
│   │   ├── base.html        # Basis-Layout
│   │   ├── components/      # Wiederverwendbare Komponenten
│   │   ├── participants/    # Teilnehmer-Templates
│   │   ├── families/        # Familien-Templates
│   │   ├── payments/        # Zahlungs-Templates
│   │   ├── expenses/        # Ausgaben-Templates
│   │   ├── rulesets/        # Regelwerk-Templates
│   │   └── settings/        # Einstellungs-Templates
│   ├── static/              # CSS, JS, Bilder
│   ├── schemas.py           # Pydantic Validierungs-Schemas
│   ├── config.py            # Konfiguration
│   ├── database.py          # Datenbank-Setup
│   └── main.py              # FastAPI Hauptanwendung
├── rulesets/
│   └── examples/            # Beispiel-Regelwerke
├── tests/                   # Tests
├── requirements.txt         # Python Dependencies
└── README.md               # Diese Datei
```

## Datenmodell

- **Event**: Freizeit/Veranstaltung (z.B. Kinderfreizeit 2024)
- **Participant**: Teilnehmer mit allen persönlichen Daten, Rolle und berechneten Preisen
- **Family**: Familie zur Gruppierung von Teilnehmern mit automatischem Familienrabatt
- **Role**: Rolle (Kind, Betreuer, Küche, etc.) mit optionalen Rabatten
- **Ruleset**: Regelwerk für Preisberechnungen (YAML-basiert)
- **Payment**: Zahlungen von Teilnehmern oder Familien
- **Expense**: Ausgaben für die Freizeit mit Kategorien
- **Setting**: Event-spezifische Einstellungen (Bankdaten, Rechnungs-Layout)

Beziehungen:
- Ein Event hat viele Participants, Families, Payments, Expenses und ein Setting
- Ein Participant gehört zu einem Event, einer Role und optional einer Family
- Eine Family hat viele Participants und Payments
- Payments können zu Participants oder Families gehören

## Regelwerk-System

Regelwerke werden als YAML-Dateien definiert und legen fest:
- Preise nach Altersklassen
- Rabatte nach Rollen
- Familienrabatte
- Gültigkeitszeitraum

### Beispiel-Regelwerk

```yaml
name: "Kinderfreizeit 2024"
type: "kinder"
valid_from: "2024-01-01"
valid_until: "2024-12-31"

age_groups:
  - min_age: 6
    max_age: 9
    price: 140.00
  - min_age: 10
    max_age: 12
    price: 150.00

role_discounts:
  betreuer:
    discount_percent: 50
    max_count: 10
  kueche:
    discount_percent: 100
    max_count: 2

family_discount:
  enabled: true
  second_child_percent: 10
  third_plus_child_percent: 20
```

### Regelwerk-Operationen

- **Import**: YAML-Datei hochladen und importieren
- **Export**: Regelwerk als YAML-Datei exportieren
- **Edit**: Regelwerk direkt im Browser als YAML bearbeiten
- **Validierung**: Automatische Prüfung der YAML-Struktur beim Import/Edit

## API-Endpunkte

### Dashboard
- `GET /` - Hauptdashboard mit Statistiken

### Teilnehmer
- `GET /participants` - Liste aller Teilnehmer (mit Filter)
- `GET /participants/{id}` - Teilnehmer-Details
- `GET /participants/create` - Formular für neuen Teilnehmer
- `POST /participants/create` - Teilnehmer erstellen
- `GET /participants/{id}/edit` - Teilnehmer bearbeiten
- `POST /participants/{id}/edit` - Teilnehmer aktualisieren
- `POST /participants/{id}/delete` - Teilnehmer löschen
- `POST /participants/calculate-price` - HTMX-Preisvorschau

### Familien
- `GET /families` - Liste aller Familien
- `GET /families/{id}` - Familien-Details
- `GET /families/create` - Formular für neue Familie
- `POST /families/create` - Familie erstellen
- `GET /families/{id}/edit` - Familie bearbeiten
- `POST /families/{id}/edit` - Familie aktualisieren
- `POST /families/{id}/delete` - Familie löschen
- `GET /families/{id}/invoice` - Familien-Rechnung generieren

### Zahlungen
- `GET /payments` - Liste aller Zahlungen (mit Filter)
- `GET /payments/create` - Formular für neue Zahlung
- `POST /payments/create` - Zahlung erfassen
- `POST /payments/{id}/delete` - Zahlung löschen

### Ausgaben
- `GET /expenses` - Liste aller Ausgaben (mit Filter)
- `GET /expenses/create` - Formular für neue Ausgabe
- `POST /expenses/create` - Ausgabe erfassen
- `GET /expenses/{id}/edit` - Ausgabe bearbeiten
- `POST /expenses/{id}/edit` - Ausgabe aktualisieren
- `POST /expenses/{id}/delete` - Ausgabe löschen

### Regelwerke
- `GET /rulesets` - Liste aller Regelwerke
- `GET /rulesets/{id}` - Regelwerk-Details
- `GET /rulesets/import` - Import-Formular
- `POST /rulesets/import` - YAML-Regelwerk importieren
- `GET /rulesets/{id}/export` - Regelwerk als YAML exportieren
- `GET /rulesets/{id}/edit` - Regelwerk-Editor
- `POST /rulesets/{id}/edit` - Regelwerk aktualisieren
- `POST /rulesets/{id}/delete` - Regelwerk löschen

### Einstellungen
- `GET /settings` - Einstellungen anzeigen
- `GET /settings/edit` - Einstellungen bearbeiten
- `POST /settings/edit` - Einstellungen aktualisieren

### System
- `GET /health` - Health-Check

## Validierung

Das System verwendet Pydantic für umfassende Input-Validierung:

### Teilnehmer
- Namen dürfen nicht leer sein
- E-Mail-Adressen werden auf korrektes Format geprüft
- Geburtsdatum muss zwischen 1900 und heute liegen
- Rabatte müssen zwischen 0% und 100% liegen
- Manuelle Preise müssen >= 0 sein

### Familien
- Familienname darf nicht leer sein
- E-Mail-Validierung wie bei Teilnehmern

### Zahlungen
- Betrag muss > 0 sein
- Datum darf nicht in der Zukunft liegen
- Entweder Teilnehmer ODER Familie muss ausgewählt sein

### Ausgaben
- Titel darf nicht leer sein
- Betrag muss > 0 sein
- Datum darf nicht in der Zukunft liegen

### Einstellungen
- IBAN: 15-34 Zeichen, muss mit Ländercode beginnen
- BIC: 8 oder 11 Zeichen, korrektes Format
- Organisation und Kontoinhaber dürfen nicht leer sein

## Entwicklung

### Entwicklungsmodus starten

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Datenbank zurücksetzen

```bash
rm freizeit_kassen.db
python -m app.main  # Startet die App und erstellt neue DB
```

### Tests ausführen

```bash
pytest
```

### Code-Qualität prüfen

```bash
# Linting
flake8 app/

# Type-Checking
mypy app/
```

## 📦 Releases erstellen

Für Maintainer:

**Windows Standalone-Version (mit embedded Python):**
```bash
python build_standalone_windows.py
```
Erstellt Windows-Standalone-Paket (~60 MB) - keine Python-Installation erforderlich!

**Portable-Version (für alle Plattformen):**
```bash
python build_portable.py
```
Erstellt Portable-Pakete (~5 MB) - Python-Installation erforderlich.

Beide Skripte erstellen ZIP-Archive im `releases/` Ordner.

**Empfehlung:**
- Windows: Beide Versionen bereitstellen (Standalone für Endanwender, Portable für Tech-Savvy)
- macOS/Linux: Nur Portable-Version (kleiner, Python meist vorhanden)

## Changelog

### v1.0.0 - Produktiv-Release
- ✅ Vollständige Teilnehmerverwaltung mit CRUD
- ✅ Familienverwaltung mit Gruppenrabatt
- ✅ YAML-basiertes Regelwerk-System mit Import/Export/Edit
- ✅ Automatische Preisberechnung mit Live-Preview
- ✅ Zahlungsverwaltung für Teilnehmer und Familien
- ✅ Ausgabenverwaltung mit Kategorien
- ✅ PDF-Rechnungsgenerierung
- ✅ Konfigurierbares Einstellungssystem
- ✅ Zentralisiertes Error-Handling mit Flash-Messages
- ✅ Pydantic Input-Validierung über alle Formulare
- ✅ Responsive UI mit Tailwind CSS und HTMX
- ✅ Logging-System

### v0.1.0 - Grundgerüst
- Projekt-Struktur
- FastAPI-App mit Basis-Routing
- SQLAlchemy-Modelle
- Basis-Templates

## Backup & Restore

**Backup erstellen:**
Die Datenbank ist in einer einzelnen SQLite-Datei gespeichert:
```bash
# Datei kopieren
cp freizeit_kassen.db freizeit_kassen_backup_$(date +%Y%m%d).db
```

**Backup wiederherstellen:**
```bash
# Alte Datenbank durch Backup ersetzen
cp freizeit_kassen_backup_YYYYMMDD.db freizeit_kassen.db
```

**Empfehlung:** Erstelle regelmäßige Backups (z.B. täglich während der Anmeldephase)!

## Troubleshooting

### Problem: Port 8000 bereits belegt
**Lösung:** Ändere den Port in der `.env` Datei oder starte mit:
```bash
uvicorn app.main:app --port 8001
```

### Problem: Datenbank-Fehler nach Update
**Lösung:** Führe Datenbankmigrationen aus:
```bash
alembic upgrade head
```

### Problem: Regelwerk wird nicht importiert
**Lösung:** Überprüfe die YAML-Syntax:
- Korrekte Einrückung (2 Leerzeichen)
- Gültige Datumsformate (YYYY-MM-DD)
- Pflichtfelder vorhanden (name, type, valid_from, valid_until, age_groups)

### Problem: Preise werden nicht korrekt berechnet
**Lösung:**
1. Stelle sicher, dass ein aktives Regelwerk für das Event-Datum existiert
2. Prüfe, ob Altersgruppen den Teilnehmer abdecken
3. Achte auf Familienrabatt-Reihenfolge (nach Geburtsdatum)

## Bekannte Einschränkungen

- SQLite ist für einzelne Events ausreichend, bei sehr großen Freizeiten (>1000 Teilnehmer) sollte PostgreSQL in Betracht gezogen werden
- Keine Multi-User-Authentifizierung (geplant für v2.0)
- Keine Backup-Automatisierung (manuelle Datenbank-Sicherung empfohlen)

## Geplante Features (v2.0)

- [ ] Benutzer-Authentifizierung und Rollen
- [ ] Multi-Tenancy (mehrere Organisationen)
- [ ] Email-Benachrichtigungen
- [ ] CSV/Excel Import/Export
- [ ] Erweiterte Statistiken und Reports
- [ ] Mahnwesen für offene Zahlungen
- [ ] API für externe Integrationen

## Lizenz

[Lizenz hier einfügen]

## Support

Bei Fragen oder Problemen bitte ein Issue erstellen.

## Mitwirken

Contributions sind willkommen! Bitte:
1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## Autoren

MGBFreizeitplaner wurde entwickelt für Kinder-, Jugend- und Familienfreizeiten.
