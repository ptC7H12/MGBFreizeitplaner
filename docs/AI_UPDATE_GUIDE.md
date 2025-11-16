# 🤖 KI-Update-Guide für MGBFreizeitplaner

**Zielgruppe**: KI-Systeme (Claude, GPT, etc.) die Code-Updates durchführen

## 📋 Überblick

Dieser Guide stellt sicher, dass DB-Schema-Änderungen korrekt über Alembic-Migrationen verwaltet werden.

---

## ⚠️ KRITISCHE REGEL

**IMMER wenn du ein Model in `app/models/` änderst, MUSST du eine Alembic-Migration erstellen!**

Models sind Dateien in:
- `app/models/participant.py`
- `app/models/family.py`
- `app/models/event.py`
- `app/models/role.py`
- `app/models/payment.py`
- `app/models/expense.py`
- `app/models/income.py`
- `app/models/ruleset.py`
- `app/models/setting.py`
- `app/models/task.py`

---

## 🔄 Update-Workflow (SCHRITT FÜR SCHRITT)

### Phase 1: Analyse

**1.1 Prüfe was geändert werden soll**
```
- Welche Dateien müssen geändert werden?
- Betrifft es Models (app/models/*.py)?
- Betrifft es das DB-Schema?
```

**1.2 Wenn Models NICHT betroffen sind**
```
→ Normale Code-Änderungen durchführen
→ Testen
→ Committen
→ FERTIG
```

**1.3 Wenn Models BETROFFEN sind**
```
→ Weiter zu Phase 2
```

---

### Phase 2: Model-Änderungen + Migration

**2.1 Backup erstellen (KRITISCH!)**
```bash
# Datenbank-Backup
cp freizeit_kassen.db freizeit_kassen_backup_$(date +%Y%m%d_%H%M%S).db

# Oder via App-Interface: /backups/
```

**2.2 Model ändern**

Beispiel: Neue Spalte in Participant hinzufügen
```python
# app/models/participant.py
class Participant(Base):
    # ... bestehende Felder ...

    # NEU
    emergency_contact = Column(String(200), nullable=True)
```

**2.3 Migration generieren**

```bash
# Automatisch generieren (empfohlen)
alembic revision --autogenerate -m "AI: Add emergency_contact to participants"

# ODER manuell erstellen
alembic revision -m "AI: Add emergency_contact to participants"
```

**Format für Commit-Message**: Immer mit `"AI: "` präfixen!

**2.4 Migration prüfen**

Öffne die generierte Datei in `migrations/versions/XXXXXX_*.py`:

```python
def upgrade() -> None:
    # Prüfe: Ist die Änderung korrekt?
    op.add_column('participants', sa.Column('emergency_contact', sa.String(200), nullable=True))

def downgrade() -> None:
    # Prüfe: Ist der Rollback korrekt?
    op.drop_column('participants', 'emergency_contact')
```

**WICHTIG**: Alembic erkennt NICHT automatisch:
- Tabellen-Umbenennung (sieht aus wie drop + create)
- Spalten-Umbenennung (sieht aus wie drop + add)
- Änderungen an `server_default` Werten

Für diese Fälle: Manuelle Migration schreiben!

**2.5 Migration testen (lokal)**

```bash
# Migration anwenden
alembic upgrade head

# Prüfen ob alles funktioniert
# App starten und testen

# Bei Problemen: Rollback
alembic downgrade -1
```

**2.6 App-Version aktualisieren**

```python
# app/config.py
class Settings(BaseSettings):
    app_version: str = "0.2.0"  # Version erhöhen!
```

**Versioning-Schema**:
- Major: Breaking Changes (z.B. 1.0.0 → 2.0.0)
- Minor: Neue Features (z.B. 0.1.0 → 0.2.0)
- Patch: Bugfixes (z.B. 0.1.0 → 0.1.1)

---

### Phase 3: Commit & Push

**3.1 Git Status prüfen**
```bash
git status
```

Sollte zeigen:
- Geänderte Model-Datei(en)
- Neue Migration in `migrations/versions/`
- `app/config.py` (neue Version)

**3.2 Commit erstellen**

```bash
git add -A
git commit -m "AI: Add emergency_contact field to participants

- Add emergency_contact column to Participant model
- Create Alembic migration: XXXXXX_add_emergency_contact
- Update app version to 0.2.0

Migration tested locally ✓
"
```

**3.3 Push**
```bash
git push
```

---

### Phase 4: Deployment

**4.1 Auf Production-Server**

```bash
# Code aktualisieren
git pull

# Migration ausführen (automatisch oder manuell)
alembic upgrade head

# App neu starten
docker-compose restart
# ODER
systemctl restart freizeit-kassen-system
```

**4.2 Prüfen**

```bash
# Alembic-Version prüfen
alembic current

# Sollte zeigen: die neueste Migration

# Logs prüfen
tail -f logs/app.log
# ODER
docker-compose logs -f web
```

---

## 🔍 Spezialfälle

### Fall 1: Spalte umbenennen

❌ **Alembic erkennt dies NICHT automatisch!**

✅ **Manuelle Migration**:
```python
def upgrade():
    # Umbenennen statt drop + add
    op.alter_column('participants', 'old_name', new_column_name='new_name')

def downgrade():
    op.alter_column('participants', 'new_name', new_column_name='old_name')
```

### Fall 2: Tabelle umbenennen

❌ **Alembic erkennt dies NICHT automatisch!**

✅ **Manuelle Migration**:
```python
def upgrade():
    op.rename_table('old_table', 'new_table')

def downgrade():
    op.rename_table('new_table', 'old_table')
```

### Fall 3: Daten-Migration

Wenn bestehende Daten aktualisiert werden müssen:

```python
def upgrade():
    # Schema-Änderung
    op.add_column('participants', sa.Column('status', sa.String(20)))

    # Daten-Migration
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE participants SET status = 'active' WHERE is_active = 1")
    )
    connection.execute(
        sa.text("UPDATE participants SET status = 'inactive' WHERE is_active = 0")
    )

def downgrade():
    op.drop_column('participants', 'status')
```

### Fall 4: Mehrere Schema-Änderungen

Erstelle **EINE Migration pro logische Änderung**:

✅ **Gut**:
```
- Migration 1: Add emergency_contact field
- Migration 2: Add consent_given field
```

❌ **Schlecht**:
```
- Migration 1: Add emergency_contact AND consent_given AND refactor payments table
```

---

## 🚨 Error Handling

### Problem: Migration schlägt fehl

```bash
# 1. Rollback zur vorherigen Version
alembic downgrade -1

# 2. Migration-Datei prüfen und korrigieren
nano migrations/versions/XXXXXX_*.py

# 3. Erneut versuchen
alembic upgrade head
```

### Problem: "Can't locate revision identified by 'xyz'"

```bash
# Datenbank-Zustand zurücksetzen
alembic stamp head

# Migrations erneut anwenden
alembic upgrade head
```

### Problem: "Target database is not up to date"

```bash
# Fehlende Migrationen anwenden
alembic upgrade head
```

### Problem: Daten gehen verloren

```bash
# Backup wiederherstellen
cp freizeit_kassen_backup_XXXXXX.db freizeit_kassen.db

# Migration überarbeiten
# Erneut versuchen
```

---

## ✅ Checkliste vor dem Commit

**Für JEDE Model-Änderung**:

- [ ] Backup erstellt? (`/backups/` oder manuell)
- [ ] Model geändert?
- [ ] Migration generiert? (`alembic revision --autogenerate`)
- [ ] Migration geprüft? (upgrade + downgrade korrekt?)
- [ ] Migration getestet? (`alembic upgrade head`)
- [ ] App-Version erhöht? (`app/config.py`)
- [ ] Commit-Message korrekt? (mit `AI:` Präfix)
- [ ] Alle Änderungen staged? (`git status`)

**Wenn alle Punkte ✅ sind → Committen!**

---

## 🔄 Rollback-Strategie

### Szenario 1: Migration ist fehlerhaft (vor Production)

```bash
# Rollback zur vorherigen Version
alembic downgrade -1

# Migration-Datei löschen
rm migrations/versions/XXXXXX_fehlerhafte_migration.py

# Neue Migration erstellen
alembic revision --autogenerate -m "AI: Corrected migration"
```

### Szenario 2: Migration ist deployed (Production)

```bash
# NIEMALS Migration-Dateien löschen die deployed wurden!

# Stattdessen: Neue Migration erstellen die Änderung rückgängig macht
alembic revision -m "AI: Revert emergency_contact changes"

# In der neuen Migration:
def upgrade():
    op.drop_column('participants', 'emergency_contact')

def downgrade():
    op.add_column('participants', sa.Column('emergency_contact', sa.String(200)))
```

---

## 📚 Referenzen

- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Alembic Auto-Generate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [SQLAlchemy Column Types](https://docs.sqlalchemy.org/en/20/core/type_basics.html)
- [Projekt-spezifische Migrations-Dokumentation](../migrations/README.md)

---

## 🎯 Zusammenfassung

**3 Goldene Regeln**:

1. **IMMER** Backup vor Schema-Änderungen
2. **IMMER** Migration erstellen bei Model-Änderungen
3. **IMMER** Migration testen vor Commit

**Bei Unsicherheit**:
- Lieber eine Migration zu viel als zu wenig
- Lieber kleine Migrations als große
- Lieber testen als hoffen

---

## 🤝 Support

Bei Problemen:
1. Prüfe die Logs: `tail -f logs/app.log`
2. Prüfe Alembic-Status: `alembic current`
3. Prüfe Migration-Historie: `alembic history --verbose`
4. Konsultiere die Dokumentation: `migrations/README.md`
