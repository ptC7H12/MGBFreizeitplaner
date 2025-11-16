# 📚 Dokumentation - MGBFreizeitplaner

## Übersicht

Diese Dokumentation beschreibt alle technischen Aspekte des Freizeit-Kassen-Systems.

---

## 📖 Dokumentations-Index

### 🤖 Für KI-Systeme

**[AI_UPDATE_GUIDE.md](./AI_UPDATE_GUIDE.md)**
- **Zielgruppe**: KI-Systeme (Claude, GPT, etc.)
- **Inhalt**: Schritt-für-Schritt Anleitung für Code-Updates
- **Wichtig**: Wie Alembic-Migrationen erstellt werden
- **Checkliste**: Was vor jedem Commit geprüft werden muss

### 🚀 Deployment & Updates

**[DEPLOYMENT_UPDATE.md](./DEPLOYMENT_UPDATE.md)**
- **Zielgruppe**: DevOps, Administratoren
- **Inhalt**: Update-Prozess für Production
- **Wichtig**: Automatische vs. manuelle Migrationen
- **Rollback**: Was tun bei Problemen

### 🐳 Docker

**[DOCKER.md](./DOCKER.md)**
- **Zielgruppe**: DevOps, Entwickler
- **Inhalt**: Docker-Deployment Guide
- **Wichtig**: SECRET_KEY, Health Checks, Volumes
- **Troubleshooting**: Häufige Docker-Probleme

### 🗄️ Datenbank

**[DATABASE_INDEXES.md](./DATABASE_INDEXES.md)**
- **Zielgruppe**: Entwickler, DB-Administratoren
- **Inhalt**: Index-Strategie & Query-Optimierung
- **Wichtig**: Welche Indexes existieren
- **Performance**: Best Practices für Queries

---

## 🗂️ Weitere Dokumentation

### Migrations-Dokumentation

**[../migrations/README.md](../migrations/README.md)**
- Alembic Migrations Guide
- Workflow für Schema-Änderungen
- Troubleshooting

### Code-Dokumentation

**[../README.md](../README.md)**
- Projekt-Übersicht
- Installation
- Erste Schritte

---

## 🎯 Quick Links

### Für Entwickler

1. **Start**: [../README.md](../README.md)
2. **Database**: [DATABASE_INDEXES.md](./DATABASE_INDEXES.md)
3. **Migrations**: [../migrations/README.md](../migrations/README.md)
4. **Docker**: [DOCKER.md](./DOCKER.md)

### Für KI-Updates

1. **AI Guide**: [AI_UPDATE_GUIDE.md](./AI_UPDATE_GUIDE.md)
2. **Migrations**: [../migrations/README.md](../migrations/README.md)
3. **Deployment**: [DEPLOYMENT_UPDATE.md](./DEPLOYMENT_UPDATE.md)

### Für Deployment

1. **Docker**: [DOCKER.md](./DOCKER.md)
2. **Updates**: [DEPLOYMENT_UPDATE.md](./DEPLOYMENT_UPDATE.md)
3. **Migrations**: [../migrations/README.md](../migrations/README.md)

---

## 🔍 Suche in Dokumentation

### Ich will...

**...die App mit Docker starten**
→ [DOCKER.md](./DOCKER.md) - Schnellstart-Sektion

**...ein Update deployen**
→ [DEPLOYMENT_UPDATE.md](./DEPLOYMENT_UPDATE.md) - Update-Prozess

**...eine Migration erstellen**
→ [../migrations/README.md](../migrations/README.md) - Workflow

**...Code mit KI updaten**
→ [AI_UPDATE_GUIDE.md](./AI_UPDATE_GUIDE.md) - Kompletter Workflow

**...Queries optimieren**
→ [DATABASE_INDEXES.md](./DATABASE_INDEXES.md) - Performance-Sektion

**...ein Problem beheben**
→ Jedes Dokument hat eine Troubleshooting-Sektion

---

## 📝 Dokumentations-Konventionen

### Symbole

- 🤖 KI-spezifisch
- 🐳 Docker-spezifisch
- 🗄️ Datenbank-spezifisch
- 🚀 Deployment-spezifisch
- ⚠️ Wichtig/Warnung
- ✅ Checklist-Item
- 🔍 Troubleshooting
- 📊 Monitoring

### Code-Beispiele

```bash
# Bash-Befehle
alembic upgrade head
```

```python
# Python-Code
from app.models import Participant
```

```yaml
# YAML-Konfiguration
environment:
  - DEBUG=false
```

---

## 🆘 Support

Bei Problemen:

1. **Logs prüfen**: `tail -f logs/app.log` oder `docker-compose logs -f`
2. **Dokumentation durchsuchen**: Troubleshooting-Sektionen
3. **GitHub Issues**: Fehler melden (falls Open Source)

---

## 📅 Letzte Updates

Dieses Dokumentations-Set wurde zuletzt aktualisiert: **Januar 2025**

**Version**: 0.1.0

**Änderungen**:
- ✅ AI Update Guide hinzugefügt
- ✅ Deployment Update Guide hinzugefügt
- ✅ Docker Guide erstellt
- ✅ Database Indexes dokumentiert
- ✅ Automatische Migrations-Prüfung implementiert
