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

## Schnellstart

### Mit Docker (empfohlen)

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

### Ohne Docker

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
