# Database Index Optimierung

## Übersicht

Diese Dokumentation beschreibt die Datenbank-Indexes und Query-Optimierungsstrategien.

## Bestehende Indexes

### Events Tabelle
- ✅ `ix_events_code` (UNIQUE) - Event-Code für Login/Auswahl
- ✅ `ix_events_is_active` - Filter für aktive Events

### Participants Tabelle
- ✅ `ix_participants_event_id` - Foreign Key (häufigste Query)
- ✅ `ix_participants_role_id` - Foreign Key
- ✅ `ix_participants_family_id` - Foreign Key
- ✅ `ix_participants_is_active` - Filter für aktive Teilnehmer
- ✅ `ix_participants_email` - Suche nach Email
- ✅ `ix_participants_last_name` - Suche nach Nachname
- ✅ `ix_participants_deleted_at` - Soft-Delete Queries

### Families Tabelle
- ✅ `ix_families_event_id` - Foreign Key
- ✅ `ix_families_is_active` - Filter
- ✅ `ix_families_email` - Suche
- ✅ `ix_families_deleted_at` - Soft-Delete

### Roles Tabelle
- ✅ `ix_roles_event_id` - Foreign Key
- ✅ `ix_roles_is_active` - Filter

### Payments Tabelle
- ✅ `ix_payments_event_id` - Foreign Key
- ✅ `ix_payments_participant_id` - Foreign Key
- ✅ `ix_payments_family_id` - Foreign Key

### Expenses Tabelle
- ✅ `ix_expenses_event_id` - Foreign Key

### Incomes Tabelle
- ✅ `ix_incomes_event_id` - Foreign Key
- ✅ `ix_incomes_role_id` - Foreign Key

### Tasks Tabelle
- ✅ `ix_tasks_event_id` - Foreign Key
- ✅ `ix_tasks_is_completed` - Filter

### Settings Tabelle
- ✅ `ix_settings_event_id` (UNIQUE) - One-to-One Relationship

### Rulesets Tabelle
- ✅ `ix_rulesets_event_id` - Foreign Key
- ✅ `ix_rulesets_is_active` - Filter

## Bewertung

### ✅ Gut abgedeckt
- Alle Foreign Keys haben Indexes
- Filter-Felder (is_active, deleted_at) sind indiziert
- Häufige Suchen (email, last_name) haben Indexes
- Composite Queries werden durch Single-Column Indexes unterstützt

### 💡 Mögliche Optimierungen (Optional)

#### Composite Indexes für häufige Query-Kombinationen:

```python
# participants: event_id + is_active (häufige Kombination)
Index('ix_participants_event_active', 'event_id', 'is_active')

# participants: event_id + family_id (Familienansicht)
Index('ix_participants_event_family', 'event_id', 'family_id')

# payments: event_id + payment_date (Timeline)
Index('ix_payments_event_date', 'event_id', 'payment_date')

# expenses: event_id + expense_date (Timeline)
Index('ix_expenses_event_date', 'event_id', 'expense_date')
```

**Entscheidung**: Für lokalen Single-User Betrieb NICHT notwendig.
- Datenvolumen bleibt klein (< 10.000 Records)
- Single-Column Indexes sind ausreichend
- Overhead von Composite Indexes nicht gerechtfertigt

## Query-Optimierungs-Guidelines

### 1. N+1 Query Problem vermeiden

❌ **Schlecht**:
```python
participants = db.query(Participant).all()
for p in participants:
    print(p.role.name)  # Lädt role für jeden Participant einzeln
```

✅ **Gut**:
```python
from sqlalchemy.orm import joinedload

participants = db.query(Participant).options(
    joinedload(Participant.role),
    joinedload(Participant.family)
).all()
```

### 2. Select Only What You Need

❌ **Schlecht**:
```python
participants = db.query(Participant).all()  # Lädt alle Spalten
names = [p.full_name for p in participants]
```

✅ **Gut**:
```python
names = db.query(Participant.first_name, Participant.last_name).all()
```

### 3. Use Pagination für große Listen

```python
# Mit Limit/Offset
participants = db.query(Participant).limit(50).offset(0).all()

# Oder: Cursor-Based Pagination
participants = db.query(Participant).filter(
    Participant.id > last_seen_id
).limit(50).all()
```

### 4. Filter so früh wie möglich

✅ **Gut**:
```python
# Filter auf DB-Ebene
active_participants = db.query(Participant).filter(
    Participant.event_id == event_id,
    Participant.is_active == True
).all()
```

❌ **Schlecht**:
```python
# Filter in Python (lädt ALLE Participants)
all_participants = db.query(Participant).all()
active = [p for p in all_participants if p.is_active and p.event_id == event_id]
```

### 5. Bulk Operations verwenden

✅ **Gut**:
```python
# Bulk Insert
db.bulk_insert_mappings(Participant, participant_dicts)

# Bulk Update
db.query(Participant).filter(
    Participant.event_id == event_id
).update({"is_active": False})
```

## Query Profiling

### SQLite EXPLAIN QUERY PLAN

```bash
sqlite3 freizeit_kassen.db
sqlite> EXPLAIN QUERY PLAN
        SELECT * FROM participants
        WHERE event_id = 1 AND is_active = 1;
```

Erwartete Ausgabe:
```
SEARCH TABLE participants USING INDEX ix_participants_event_id (event_id=?)
```

### SQLAlchemy Echo Mode

```python
# In database.py:
engine = create_engine(
    settings.database_url,
    echo=True  # Zeigt alle SQL-Queries
)
```

## Performance Benchmarks (Referenz)

Für lokalen Single-User Betrieb mit < 10.000 Records:

| Operation | Akzeptable Zeit | Anmerkungen |
|-----------|----------------|-------------|
| List Participants (50) | < 50ms | Mit Joins |
| Create Participant | < 20ms | Single Insert |
| Update Participant | < 20ms | Single Update |
| Dashboard Stats | < 100ms | Multiple Queries |
| Invoice Generation | < 500ms | PDF Rendering |

## Maintenance

### Index Rebuild (bei Bedarf)

SQLite:
```bash
sqlite3 freizeit_kassen.db "VACUUM;"
```

PostgreSQL:
```sql
REINDEX TABLE participants;
```

### Statistiken aktualisieren

SQLite:
```bash
sqlite3 freizeit_kassen.db "ANALYZE;"
```

PostgreSQL:
```sql
ANALYZE participants;
```

## Fazit

✅ **Aktuelle Index-Strategie ist optimal** für:
- Lokalen Single-User Betrieb
- Datenvolumen < 10.000 Records
- Typische Query-Patterns

❌ **Keine weiteren Indexes notwendig** weil:
- Overhead würde Performance verschlechtern
- Write-Performance würde leiden
- Datenbank-Größe würde unnötig wachsen

📊 **Empfehlung**: Indexes unverändert lassen, Query-Optimierung über SQLAlchemy-Best-Practices.
