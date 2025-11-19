# Datenbank-Migrations Setup mit Alembic

## Warum Migrations?

Aktuell nutzt das Projekt `Base.metadata.create_all()`, was zwar funktioniert, aber:
- ❌ Keine Versionierung von Schema-Änderungen
- ❌ Kein Rollback bei Problemen möglich
- ❌ Schwierig Schema-Änderungen nachzuvollziehen
- ❌ Datenverlust bei Model-Änderungen (DROP + CREATE)

Mit Alembic Migrations:
- ✅ Versionierte Schema-Änderungen
- ✅ Rollback/Upgrade möglich
- ✅ Nachvollziehbare Historie
- ✅ Sichere Schema-Änderungen (ALTER statt DROP)
- ✅ Team-Zusammenarbeit erleichtert

## Installation

```bash
# Alembic installieren
pip install alembic

# In requirements.txt ergänzen:
echo "alembic==1.13.1" >> requirements.txt
```

## Einrichtung

### 1. Alembic initialisieren

```bash
alembic init migrations
```

### 2. Konfiguration anpassen

In `migrations/env.py`:

```python
from app.database import Base
from app.models import participant, family, role, ruleset, payment, expense, income, event, task
from app.config import settings

# Target Metadata setzen
target_metadata = Base.metadata

# SQLAlchemy URL aus Config laden
config.set_main_option("sqlalchemy.url", settings.database_url)
```

### 3. Initiale Migration erstellen

```bash
# Erstelle Migration aus aktuellem Schema
alembic revision --autogenerate -m "Initial schema"

# Migration anwenden
alembic upgrade head
```

## Verwendung

### Neue Migration erstellen

```bash
# Nach Model-Änderungen:
alembic revision --autogenerate -m "Add deleted_at to participants"
```

### Migrations anwenden

```bash
# Auf neueste Version upgraden
alembic upgrade head

# Eine Version zurück
alembic downgrade -1

# Zu spezifischer Revision
alembic upgrade <revision_id>
```

### Status prüfen

```bash
# Aktuelle Version
alembic current

# Historie anzeigen
alembic history --verbose
```

## Integration in Anwendung

In `app/main.py` im `lifespan()`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ===== STARTUP =====
    logger.info("Führe Datenbank-Migrations aus...")

    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    logger.info("Migrations erfolgreich angewendet!")

    # Rest der Startup-Logik...
    yield

    # ===== SHUTDOWN =====
    logger.info("Shutdown...")
```

## Bereits durchgeführte Schema-Änderungen

Die folgenden Änderungen wurden in diesem Code-Review implementiert und sollten
in der ersten Migration erfasst werden:

### Phase 2: Soft-Delete Pattern

**Participant Model:**
- `deleted_at`: DateTime, nullable, indexed

**Family Model:**
- `is_active`: Boolean, default=True, indexed
- `deleted_at`: DateTime, nullable, indexed

### Phase 2: Datenbank-Indizes

**Participant Model:**
- `email`: Index hinzugefügt
- `event_id`: Index hinzugefügt
- `role_id`: Index hinzugefügt
- `family_id`: Index hinzugefügt
- `is_active`: Index hinzugefügt
- `deleted_at`: Index hinzugefügt

**Family Model:**
- `event_id`: Index hinzugefügt
- `is_active`: Index hinzugefügt
- `deleted_at`: Index hinzugefügt

## Wichtige Hinweise

1. **Vor Production-Deployment**: Immer Backup der Datenbank erstellen
2. **Testing**: Migrations in Entwicklungsumgebung testen
3. **Autogenerate**: Immer die generierten Migrations prüfen (nicht blind vertrauen)
4. **Daten-Migrations**: Bei komplexen Änderungen ggf. manuelle Data-Migrations schreiben

## Beispiel: Migration für Soft-Delete

```python
"""Add soft delete to participants and families

Revision ID: abc123
Create Date: 2024-01-15 10:30:00
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Participant
    op.add_column('participants', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.create_index('ix_participants_deleted_at', 'participants', ['deleted_at'])

    # Family
    op.add_column('families', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))
    op.add_column('families', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.create_index('ix_families_is_active', 'families', ['is_active'])
    op.create_index('ix_families_deleted_at', 'families', ['deleted_at'])

def downgrade():
    # Rückgängig machen (Rollback)
    op.drop_index('ix_families_deleted_at', 'families')
    op.drop_index('ix_families_is_active', 'families')
    op.drop_column('families', 'deleted_at')
    op.drop_column('families', 'is_active')

    op.drop_index('ix_participants_deleted_at', 'participants')
    op.drop_column('participants', 'deleted_at')
```

## Weiterführende Ressourcen

- [Alembic Dokumentation](https://alembic.sqlalchemy.org/)
- [FastAPI + Alembic Tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/#alembic-note)
- [SQLAlchemy Migrations Best Practices](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
