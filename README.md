# Freizeit-Kassen-System

Ein Web-basiertes Kassensystem für Kinder-, Jugend- und Familienfreizeiten mit Teilnehmerverwaltung, flexibler Preisgestaltung und Finanz-Tracking.

## Features

- **Teilnehmerverwaltung**: Erfassung von Teilnehmern mit allen relevanten Daten
- **Familienverwaltung**: Gruppierung von Teilnehmern zu Familien mit automatischer Preisberechnung
- **Regelwerk-System**: Flexible YAML-basierte Preisregeln für verschiedene Freizeiten
- **Finanz-Tracking**: Einnahmen und Ausgaben im Blick behalten
- **Responsive UI**: Modern mit Tailwind CSS und HTMX

## Tech-Stack

- **Backend**: Python 3.11+ mit FastAPI
- **Frontend**: HTMX + Tailwind CSS (Server-Side Rendering)
- **Datenbank**: SQLite mit SQLAlchemy ORM
- **Deployment**: Docker + Docker Compose

## Installation

### 🎯 Option 1: Standalone Version ⭐ **NEU** (Empfohlen für alle Benutzer)

**Komplett ohne Installation - Python ist bereits dabei!**

#### Windows
1. [Download Windows Standalone ZIP](../../releases) herunterladen (~60 MB)
2. ZIP entpacken
3. **Doppelklick auf `start_embedded.bat`**
4. Fertig! Browser öffnet sich automatisch unter http://localhost:8000

**Voraussetzungen:** KEINE! Alles ist enthalten.

#### macOS
1. [Download macOS Standalone ZIP](../../releases) herunterladen (~70 MB)
2. ZIP entpacken
3. **Doppelklick auf `start_embedded.sh`** (oder im Terminal: `./start_embedded.sh`)
4. Fertig! Browser öffnet sich automatisch unter http://localhost:8000

**Voraussetzungen:** KEINE! Alles ist enthalten.

#### Linux
1. [Download Linux Standalone ZIP](../../releases) herunterladen (~70 MB)
2. ZIP entpacken
3. Im Terminal: `./start_embedded.sh`
4. Fertig! Browser öffnet sich automatisch unter http://localhost:8000

**Voraussetzungen:** KEINE! Alles ist enthalten.

---

### 💾 Option 2: Portable Version (für Nutzer mit Python)

**Kleinere Download-Größe (~5 MB), aber Python muss vorinstalliert sein**

#### Windows
1. [Download Windows Portable ZIP](../../releases) herunterladen
2. ZIP entpacken
3. **Doppelklick auf `start.bat`** (oder `start.ps1` für PowerShell)
4. Fertig! Browser öffnet sich automatisch unter http://localhost:8000

**Voraussetzung:** Python 3.11+ von [python.org](https://www.python.org/downloads/) (bei Installation "Add Python to PATH" aktivieren!)

#### macOS / Linux
1. [Download Portable ZIP](../../releases) herunterladen
2. ZIP entpacken
3. **Ausführen:** `./start.sh`
4. Fertig! Browser öffnet sich automatisch unter http://localhost:8000

**Voraussetzung:** Python 3.11+ (macOS: `brew install python@3.11`, Linux: `apt install python3.11`)

---

### 🐳 Option 3: Mit Docker

**Für Server-Deployment oder Entwickler mit Docker-Erfahrung**

1. Repository klonen:
```bash
git clone <repository-url>
cd MGBFreizeitplaner
```

2. Docker Container starten:
```bash
docker-compose up -d
```

3. Anwendung aufrufen:
```
http://localhost:8000
```

---

### 💻 Option 4: Manuelle Installation (Entwickler)

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

## 📦 Releases erstellen

Für Maintainer:

**Standalone-Version (mit embedded Python - empfohlen):**
```bash
python build_portable_embedded.py
```
Erstellt vollständige Standalone-Pakete (~60-70 MB) - keine Python-Installation erforderlich!

**Portable-Version (ohne Python - kleiner):**
```bash
python build_portable.py
```
Erstellt kleinere Pakete (~5 MB) - Python-Installation erforderlich.

Beide Skripte erstellen ZIP-Archive im `releases/` Ordner.

## Projektstruktur

```
MGBFreizeitplaner/
├── app/
│   ├── models/          # SQLAlchemy Datenmodelle
│   ├── routers/         # FastAPI Router (Endpoints)
│   ├── services/        # Business Logic (Preisberechnung, etc.)
│   ├── templates/       # Jinja2 HTML-Templates
│   ├── static/          # CSS, JS, Bilder
│   ├── config.py        # Konfiguration
│   ├── database.py      # Datenbank-Setup
│   └── main.py          # FastAPI Hauptanwendung
├── rulesets/
│   └── examples/        # Beispiel-Regelwerke
├── tests/               # Tests (TODO)
├── docker-compose.yml   # Docker Compose Konfiguration
├── Dockerfile           # Docker Image Definition
├── requirements.txt     # Python Dependencies
└── README.md           # Diese Datei
```

## Datenmodell

- **Event**: Freizeit/Veranstaltung (z.B. Kinderfreizeit 2024)
- **Participant**: Teilnehmer mit allen persönlichen Daten
- **Family**: Familie zur Gruppierung von Teilnehmern
- **Role**: Rolle (Kind, Betreuer, Küche, etc.)
- **Ruleset**: Regelwerk für Preisberechnungen
- **Payment**: Zahlungen von Teilnehmern/Familien
- **Expense**: Ausgaben für die Freizeit

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

## API-Endpunkte

### Dashboard
- `GET /dashboard` - Hauptdashboard mit Statistiken

### Teilnehmer
- `GET /participants` - Liste aller Teilnehmer
- `GET /participants/{id}` - Teilnehmer-Details
- `GET /participants/create` - Formular für neuen Teilnehmer

### Familien
- `GET /families` - Liste aller Familien
- `GET /families/{id}` - Familien-Details

### Regelwerke
- `GET /rulesets` - Liste aller Regelwerke
- `GET /rulesets/{id}` - Regelwerk-Details

### System
- `GET /health` - Health-Check für Docker

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

## Roadmap / TODO

### Phase 1: Grundgerüst ✅
- [x] Projekt-Struktur
- [x] FastAPI-App mit Basis-Routing
- [x] SQLAlchemy-Modelle
- [x] Basis-Templates
- [x] Docker-Setup

### Phase 2: Teilnehmerverwaltung (TODO)
- [ ] CRUD für Teilnehmer
- [ ] Formular-Validierung
- [ ] Listen-Ansichten mit Filtern

### Phase 3: Regelwerk-System (TODO)
- [ ] YAML-Import-Funktion
- [ ] Validierungs-Logik
- [ ] Admin-Interface

### Phase 4: Preis-Kalkulation (TODO)
- [ ] Automatische Preisberechnung
- [ ] Familienpreis-Berechnung

### Phase 5: Finanz-Tracking (TODO)
- [ ] Zahlungserfassung
- [ ] Ausgaben-Verwaltung
- [ ] Export-Funktionen

### Phase 6: Familienverwaltung (TODO)
- [ ] Familien-CRUD
- [ ] Sammelrechnungen

## Lizenz

[Lizenz hier einfügen]

## Support

Bei Fragen oder Problemen bitte ein Issue erstellen.

## Version

**v0.1.0** - Grundgerüst (Phase 1)
