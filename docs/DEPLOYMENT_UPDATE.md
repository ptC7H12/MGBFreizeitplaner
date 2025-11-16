# 🚀 Deployment & Update Guide

## Überblick

Dieser Guide beschreibt wie Updates deployed werden, wenn Schema-Änderungen enthalten sind.

---

## 🔄 Update-Strategie

### Automatisch (empfohlen)

Die App prüft beim Start **automatisch** ob Migrationen ausstehen und führt diese aus.

**Ablauf**:
1. Code aktualisieren (`git pull`)
2. App neu starten
3. Migrationen werden automatisch ausgeführt ✓

### Manuell

Falls Auto-Migration fehlschlägt oder du mehr Kontrolle möchtest.

**Ablauf**:
1. Code aktualisieren
2. **VOR** App-Start: Migrationen manuell ausführen
3. App starten

---

## 📋 Update-Prozess (Docker)

### Standard-Update (mit Schema-Änderungen)

```bash
# 1. Backup erstellen (KRITISCH!)
docker exec freizeit-kassen-system \
  cp /app/data/freizeit_kassen.db \
     /app/data/freizeit_kassen_backup_$(date +%Y%m%d_%H%M%S).db

# 2. Code aktualisieren
git pull

# 3. Image neu bauen
docker-compose build

# 4. Container stoppen
docker-compose down

# 5. Container starten (Migrationen laufen automatisch!)
docker-compose up -d

# 6. Logs prüfen
docker-compose logs -f web
```

**Erwartete Log-Ausgabe**:
```
INFO: Prüfe Alembic-Migrationen...
INFO: Führe Alembic-Migrationen aus...
INFO: Running upgrade XXXXX -> YYYYY, AI: Add emergency_contact
INFO: ✓ Migrationen erfolgreich ausgeführt!
INFO: ✓ Datenbank ist auf dem neuesten Stand
```

---

## 📋 Update-Prozess (Nativ)

### Standard-Update

```bash
# 1. Backup erstellen
cp freizeit_kassen.db freizeit_kassen_backup_$(date +%Y%m%d_%H%M%S).db

# 2. Code aktualisieren
git pull

# 3. Dependencies aktualisieren (falls requirements.txt geändert)
pip install -r requirements.txt

# 4. App neu starten (Migrationen laufen automatisch!)
systemctl restart freizeit-kassen-system
# ODER
uvicorn app.main:app --reload

# 5. Logs prüfen
tail -f logs/app.log
```

---

## 🔧 Manuelle Migration (bei Bedarf)

### Warum manuell?

- Auto-Migration ist deaktiviert
- Du möchtest Migrations-Output sehen
- Du möchtest mehr Kontrolle

### Vor App-Start

```bash
# Migration prüfen
alembic current  # Aktuelle Version
alembic heads    # Neueste Version

# Ausstehende Migrationen anzeigen
alembic history

# Migration ausführen
alembic upgrade head

# Prüfen
alembic current  # Sollte jetzt neueste Version zeigen
```

### Bei laufender App (Docker)

```bash
# Container betreten
docker exec -it freizeit-kassen-system bash

# Migrationen ausführen
alembic upgrade head

# Container verlassen
exit

# App neu starten
docker-compose restart
```

---

## 🧪 Testing nach Update

### Checklist

- [ ] App startet ohne Fehler
- [ ] Logs zeigen keine Errors
- [ ] Login funktioniert
- [ ] Dashboard lädt
- [ ] Neue Features funktionieren (falls vorhanden)
- [ ] Bestehende Daten sind intakt

### Schnelltest

```bash
# Health-Check
curl http://localhost:8000/health

# Sollte returnen:
# {"status":"healthy","app":"Freizeit-Kassen-System","version":"0.2.0"}

# Alembic-Status
alembic current

# Sollte zeigen: neueste Migration mit (head)
```

---

## 🚨 Rollback bei Problemen

### Szenario: Migration schlägt fehl

```bash
# 1. Container stoppen
docker-compose down

# 2. Backup wiederherstellen
cp freizeit_kassen_backup_XXXXXX.db freizeit_kassen.db

# 3. Zu vorheriger Code-Version zurück
git log  # Finde vorherige Version
git checkout <commit-hash>

# 4. Image neu bauen
docker-compose build

# 5. Container starten
docker-compose up -d

# 6. Problem analysieren und beheben
```

### Szenario: App läuft aber Fehler aufgetreten

```bash
# Option 1: Einzelne Migration rückgängig machen
alembic downgrade -1

# Option 2: Zu spezifischer Version zurück
alembic downgrade <revision_id>

# App neu starten
docker-compose restart
```

---

## 🔍 Troubleshooting

### Problem: "Can't locate revision"

```bash
# Datenbank-Zustand mit Code synchronisieren
alembic stamp head
```

### Problem: "Target database is not up to date"

```bash
# Fehlende Migrationen ausführen
alembic upgrade head
```

### Problem: Migration läuft aber App crasht

```bash
# 1. Logs prüfen
docker-compose logs web

# 2. Migration-Datei prüfen
cat migrations/versions/XXXXXX_*.py

# 3. Daten-Migration könnte fehlgeschlagen sein
#    → Backup wiederherstellen
#    → Migration korrigieren
#    → Erneut versuchen
```

### Problem: Auto-Migration disabled

Auto-Migration kann in `main.py` deaktiviert werden:

```python
# app/main.py
check_and_run_migrations(auto_upgrade=False)  # Deaktiviert
```

Dann Migrationen manuell ausführen:
```bash
alembic upgrade head
```

---

## 📊 Monitoring

### Logs überwachen

```bash
# Docker
docker-compose logs -f web | grep -i migration

# Nativ
tail -f logs/app.log | grep -i migration
```

### Erwartete Log-Muster

**Erfolg**:
```
INFO: Prüfe Alembic-Migrationen...
INFO: ✓ Datenbank ist auf dem neuesten Stand
```

**Migrationen ausstehend**:
```
WARNING: ⚠️  Ausstehende Migrationen gefunden!
INFO: Starte automatisches Upgrade...
INFO: Running upgrade XXXXX -> YYYYY
INFO: ✓ Auto-Upgrade erfolgreich abgeschlossen
```

**Fehler**:
```
ERROR: ✗ Migrationen fehlgeschlagen!
ERROR: App wird NICHT gestartet - bitte Migrationen manuell prüfen!
```

---

## 🎯 Best Practices

### Vor jedem Update

1. **Backup erstellen** (IMMER!)
2. **Changelog lesen** (Was wurde geändert?)
3. **Testumgebung prüfen** (Falls vorhanden)
4. **Wartungsfenster planen** (Bei kritischen Updates)

### Nach jedem Update

1. **Logs prüfen** (Fehler suchen)
2. **Health-Check** (App erreichbar?)
3. **Funktionstest** (Features testen)
4. **Backup behalten** (Mindestens 7 Tage)

### Automatisierung

Für regelmäßige Updates kannst du ein Skript erstellen:

```bash
#!/bin/bash
# update.sh

set -e  # Stop bei Fehler

echo "🚀 Starting update..."

# Backup
echo "📦 Creating backup..."
docker exec freizeit-kassen-system \
  cp /app/data/freizeit_kassen.db \
     /app/data/freizeit_kassen_backup_$(date +%Y%m%d_%H%M%S).db

# Update
echo "⬇️  Pulling code..."
git pull

# Rebuild
echo "🔨 Rebuilding image..."
docker-compose build

# Restart
echo "🔄 Restarting app..."
docker-compose down
docker-compose up -d

# Check
echo "✅ Checking health..."
sleep 5
curl -f http://localhost:8000/health || exit 1

echo "✓ Update completed successfully!"
```

---

## 📚 Weitere Informationen

- [KI-Update-Guide](./AI_UPDATE_GUIDE.md) - Für KI-Systeme
- [Alembic Migrations](../migrations/README.md) - Migration-Dokumentation
- [Docker Guide](./DOCKER.md) - Docker-Deployment
