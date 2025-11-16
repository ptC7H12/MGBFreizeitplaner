# Database Migrations mit Alembic

Diese Anwendung verwendet **Alembic** für Datenbank-Migrationen.

## 🎯 Zweck

Alembic ermöglicht:
- Versionskontrolle für das Datenbank-Schema
- Automatische Generierung von Migrations-Skripten
- Sichere Schema-Updates ohne Datenverlust
- Rollback-Möglichkeiten bei Fehlern
- **Essentiell für KI-gestützte Updates!**

## 📋 Voraussetzungen

```bash
pip install alembic
```

(Bereits in `requirements.txt` enthalten)

## 🚀 Erste Schritte

### Für neue Installationen

```bash
# Migration ausführen
alembic upgrade head
```

### Für bestehende Datenbanken

Wenn die Datenbank bereits existiert (via `Base.metadata.create_all()`):

```bash
# Markiere aktuelle Version als migriert (ohne Schema-Änderung)
alembic stamp head
```

## 🔧 Workflow für Schema-Änderungen

### 1. Model ändern

Bearbeite das entsprechende Model in `app/models/`:

```python
# Beispiel: Neue Spalte hinzufügen
class Participant(Base):
    ...
    emergency_contact = Column(String(200), nullable=True)  # NEU
```

### 2. Migration generieren

```bash
alembic revision --autogenerate -m "Add emergency_contact to participants"
```

Dies erstellt eine neue Datei in `migrations/versions/`.

### 3. Migration prüfen

Öffne die generierte Datei und prüfe:
- ✅ Korrekte `upgrade()` Funktion
- ✅ Korrekte `downgrade()` Funktion
- ⚠️ Alembic erkennt nicht alle Änderungen automatisch (z.B. Tabellen-Umbenennung)

### 4. Migration anwenden

```bash
alembic upgrade head
```

### 5. Rollback (bei Bedarf)

```bash
# Eine Version zurück
alembic downgrade -1

# Zu spezifischer Version
alembic downgrade <revision_id>
```

## 📊 Nützliche Befehle

```bash
# Aktuelle Version anzeigen
alembic current

# Migrations-Historie anzeigen
alembic history --verbose

# Nächste Migration anzeigen (ohne Ausführung)
alembic upgrade head --sql

# Neue leere Migration erstellen (manuell)
alembic revision -m "Custom migration"
```

## 🤖 KI-Update Strategie

Bei Updates durch KI-Systeme:

1. **KI muss IMMER eine Migration erstellen** wenn Models geändert werden
2. **Migration muss VOR dem Commit erstellt werden**
3. **Format**:
   ```bash
   alembic revision -m "AI: <Beschreibung der Änderung>"
   ```
4. **Versionscheck in `main.py`** (siehe Update-Strategie Dokumentation)

## ⚠️ Wichtige Hinweise

### Was Alembic NICHT automatisch erkennt:
- Tabellen-Umbenennung (sieht aus wie drop + create)
- Spalten-Umbenennung (sieht aus wie drop + add)
- Änderungen an `server_default` Werten

### Manuelle Anpassungen notwendig für:
```python
# NICHT autogeneriert - manuell hinzufügen:
op.rename_table('old_name', 'new_name')
op.alter_column('table', 'old_col', new_column_name='new_col')
```

### Daten-Migrationen:
```python
def upgrade():
    # Schema-Änderung
    op.add_column('participants', sa.Column('status', sa.String(20)))

    # Daten-Migration
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE participants SET status = 'active' WHERE is_active = 1")
    )
```

## 🔐 Backup-Empfehlung

Vor größeren Migrations IMMER Backup erstellen:
```bash
# Via App-Interface: /backups/
# Oder manuell:
cp freizeit_kassen.db freizeit_kassen_backup_$(date +%Y%m%d_%H%M%S).db
```

## 📁 Datei-Struktur

```
migrations/
├── env.py                 # Alembic-Konfiguration
├── script.py.mako         # Template für neue Migrations
├── README.md              # Diese Datei
└── versions/              # Migrations-Skripte
    └── 20250115_initial_schema.py  # Initiale Migration
```

## 🆘 Troubleshooting

### "Can't locate revision identified by 'xyz'"
```bash
# Datenbank-Zustand zurücksetzen
alembic stamp head
```

### "Target database is not up to date"
```bash
# Fehlende Migrationen anwenden
alembic upgrade head
```

### Migration schlägt fehl
```bash
# Rollback zur vorherigen Version
alembic downgrade -1

# Migration prüfen und manuell anpassen
```

## 📚 Weitere Informationen

- [Alembic Dokumentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Dokumentation](https://docs.sqlalchemy.org/)
