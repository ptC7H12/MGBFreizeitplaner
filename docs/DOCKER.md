# Docker Deployment Guide

## 🐳 Überblick

Diese Anwendung kann via Docker/Docker Compose deployed werden.

## 📋 Voraussetzungen

- Docker 20.10+
- Docker Compose 2.0+

## 🚀 Schnellstart

### 1. SECRET_KEY generieren

```bash
# Generiere einen sicheren SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Kopiere den Output und setze ihn als Umgebungsvariable:

```bash
export SECRET_KEY="dein-generierter-key"
```

### 2. Container starten

```bash
docker-compose up -d
```

Die Anwendung ist nun erreichbar unter: `http://localhost:8000`

### 3. Logs ansehen

```bash
docker-compose logs -f web
```

### 4. Container stoppen

```bash
docker-compose down
```

## 🔧 Konfiguration

### Umgebungsvariablen

Alle Umgebungsvariablen können in `docker-compose.yml` oder via `.env` Datei gesetzt werden:

```yaml
environment:
  - DATABASE_URL=sqlite:////app/data/freizeit_kassen.db
  - DEBUG=false
  - SECRET_KEY=${SECRET_KEY}
  - HOST=0.0.0.0
  - PORT=8000
```

### Volumes

Persistente Daten werden in Volumes gespeichert:

```yaml
volumes:
  # Datenbank (SQLite)
  - ./data:/app/data

  # Regelwerke (YAML-Dateien)
  - ./rulesets:/app/rulesets

  # Belege/Quittungen (Uploads)
  - ./uploads:/app/uploads
```

## 📊 Health Check

Der Container hat einen eingebauten Health Check:

```bash
# Status prüfen
docker inspect freizeit-kassen-system | grep -A 10 "Health"

# Oder via docker-compose
docker-compose ps
```

Der Health Check prüft alle 30s ob die Anwendung unter `/health` antwortet.

## 🔨 Build

### Image neu bauen

```bash
docker-compose build --no-cache
```

### Multi-Stage Build

Das Dockerfile nutzt ein **Multi-Stage Build** für optimale Image-Größe:

- **Stage 1 (builder)**: Installiert Dependencies mit gcc
- **Stage 2 (runtime)**: Schlankes finales Image ohne Build-Tools

**Ergebnis**: ~50% kleineres Image

## 🗄️ Datenbank

### Initiale Migration

Beim ersten Start wird die Datenbank automatisch erstellt.

Für Alembic-Migrationen:

```bash
# Container betreten
docker exec -it freizeit-kassen-system bash

# Migration ausführen
alembic upgrade head
```

### Backup erstellen

```bash
# Via Web-Interface: /backups/

# Oder manuell:
docker cp freizeit-kassen-system:/app/data/freizeit_kassen.db ./backup_$(date +%Y%m%d).db
```

### Backup wiederherstellen

```bash
docker cp ./backup.db freizeit-kassen-system:/app/data/freizeit_kassen.db
docker-compose restart
```

## 🔐 Sicherheit

### SECRET_KEY

**WICHTIG**: Setze IMMER einen eigenen SECRET_KEY in Production!

```bash
# Generieren
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# In docker-compose.yml oder .env setzen
echo "SECRET_KEY=$SECRET_KEY" >> .env
```

### DEBUG-Modus

**Production**: `DEBUG=false`
**Development**: `DEBUG=true`

### Netzwerk-Zugriff

**Nur lokal**: `HOST=127.0.0.1`
**Alle Interfaces**: `HOST=0.0.0.0` (Standard, nur für lokale Netzwerke!)

## 🧪 Development

### Mit Auto-Reload

Für Entwicklung kannst du den Code live mounten:

```yaml
volumes:
  - ./app:/app/app  # Live-Reload
  - ./data:/app/data
  - ./rulesets:/app/rulesets
  - ./uploads:/app/uploads
```

Dann restart mit `--reload`:

```yaml
command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Ohne Docker

```bash
# Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies
pip install -r requirements.txt

# Starten
uvicorn app.main:app --reload
```

## 📈 Production Deployment

### 1. Umgebungsvariablen setzen

```bash
# .env Datei erstellen
cp .env.example .env

# SECRET_KEY setzen
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
echo "SECRET_KEY=$SECRET_KEY" >> .env
echo "DEBUG=false" >> .env
```

### 2. Container starten

```bash
docker-compose up -d
```

### 3. Monitoring

```bash
# Logs überwachen
docker-compose logs -f

# Container-Status
docker-compose ps

# Health-Check
curl http://localhost:8000/health
```

### 4. Updates

```bash
# Code aktualisieren
git pull

# Image neu bauen
docker-compose build

# Container neu starten
docker-compose up -d
```

## 🆘 Troubleshooting

### Container startet nicht

```bash
# Logs prüfen
docker-compose logs web

# Container-Status
docker ps -a

# Health-Check prüfen
docker inspect freizeit-kassen-system
```

### Datenbank-Probleme

```bash
# Container betreten
docker exec -it freizeit-kassen-system bash

# Datenbank prüfen
sqlite3 /app/data/freizeit_kassen.db ".tables"

# Alembic-Status
alembic current
```

### Permission-Probleme

```bash
# Data-Verzeichnis Permissions
sudo chown -R $(id -u):$(id -g) ./data ./uploads
```

### Port bereits belegt

```bash
# Port in docker-compose.yml ändern
ports:
  - "8080:8000"  # Host:Container
```

## 📚 Weitere Informationen

- [Alembic Migrationen](../migrations/README.md)
- [Database Indexes](./DATABASE_INDEXES.md)
- [FastAPI Dokumentation](https://fastapi.tiangolo.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
