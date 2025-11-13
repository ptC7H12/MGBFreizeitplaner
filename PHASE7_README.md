# Phase 7: Multi-Freizeit-Verwaltung (Teil 1)

## Was wurde implementiert?

### 1. Datenmodell-Erweiterungen
- **Event Model**: Erweitert um `code` (eindeutiger Zugriffscode) und `is_active` Flag
- **Family Model**: Neues `event_id` Foreign Key hinzugefügt
- **Payment Model**: Neues `event_id` Foreign Key hinzugefügt

### 2. Session-Management
- **app/dependencies.py**: Neue Dependency-Functions für Event-Session-Management
  - `get_current_event_id()`: Holt Event-ID aus Session (mit Exception)
  - `get_current_event_id_optional()`: Holt Event-ID aus Session (ohne Exception)

### 3. Auth-System
- **app/routers/auth.py**: Neuer Router für Freizeit-Auswahl und -Erstellung
  - `/auth/`: Landing Page
  - `/auth/select`: Code eingeben für bestehende Freizeit
  - `/auth/create`: Neue Freizeit erstellen
  - `/auth/logout`: Session beenden und Freizeit wechseln

### 4. Landing Page
- **app/templates/auth/landing.html**: Neue Landing Page mit zwei Optionen:
  1. **Code eingeben**: Zugriff auf bestehende Freizeit
  2. **Neue Freizeit erstellen**: Formular für neue Freizeit

### 5. UI-Anpassungen
- **Navbar**: Zeigt jetzt aktive Freizeit und Code an
- **Logout-Button**: "Wechseln"-Button zum Freizeit-Wechsel
- **Mobile Menu**: Auch mit Freizeit-Anzeige und Wechsel-Button

### 6. Router-Anpassungen
- **dashboard.py**: ✅ Angepasst mit Event-Filtering

## ⚠️ WICHTIG: Datenbank-Reset erforderlich!

Da wir Schema-Änderungen an den Models vorgenommen haben (neue Spalten), muss die Datenbank zurückgesetzt werden:

```bash
# Datenbank zurücksetzen (löscht ALLE Daten!)
python reset_db.py

# Oder manuell:
rm data/freizeit_kassen.db
python -c "from app.database import init_db; init_db()"
```

## ⏳ Noch ausstehend (Teil 2)

Die folgenden Router müssen noch mit Event-Filtering angepasst werden:

- [ ] **participants.py**: Alle Queries müssen event_id filtern
- [ ] **families.py**: Alle Queries müssen event_id filtern
- [ ] **payments.py**: Alle Queries müssen event_id filtern + event_id bei CREATE setzen
- [ ] **expenses.py**: Bereits event_id, nur Queries anpassen
- [ ] **rulesets.py**: Bereits event_id, nur Queries anpassen

### Erforderliche Änderungen pro Router:

1. **Import hinzufügen**:
   ```python
   from app.dependencies import get_current_event_id
   ```

2. **Dependency zu jeder Route hinzufügen**:
   ```python
   async def route_name(
       ...,
       event_id: int = Depends(get_current_event_id)
   ):
   ```

3. **Alle Queries filtern**:
   ```python
   # Vorher:
   participants = db.query(Participant).all()

   # Nachher:
   participants = db.query(Participant).filter(Participant.event_id == event_id).all()
   ```

4. **Bei CREATE-Operationen event_id setzen**:
   ```python
   new_participant = Participant(
       ...,
       event_id=event_id  # <-- hinzufügen
   )
   ```

## Wie funktioniert das System jetzt?

### Flow:

1. **Benutzer öffnet `/`**
   - Keine Session → Redirect zu `/auth/` (Landing Page)
   - Session vorhanden → Redirect zu `/dashboard`

2. **Landing Page (`/auth/`)**
   - Option 1: Code eingeben (z.B. "ABC12345")
   - Option 2: Neue Freizeit erstellen

3. **Nach Login/Erstellung**
   - Event-ID wird in Session gespeichert
   - User wird zu `/dashboard` weitergeleitet
   - Alle Daten werden automatisch nach Event gefiltert

4. **Freizeit wechseln**
   - "Wechseln"-Button in Navbar klicken
   - Session wird gelöscht
   - Zurück zur Landing Page

### Code-Generierung:

- **Automatisch**: Beim Erstellen einer Freizeit wird ein 8-stelliger alphanumerischer Code generiert (z.B. "XY7K9M2A")
- **Manuell**: Optional kann ein eigener Code eingegeben werden
- **Eindeutigkeit**: Wird automatisch geprüft

### Session-Daten:

```python
request.session["event_id"]    # Event-ID
request.session["event_name"]  # Freizeit-Name
request.session["event_code"]  # Zugangscode
```

## Testing

Nach dem Reset sollte getestet werden:

1. ✅ Landing Page erreichbar
2. ✅ Neue Freizeit erstellen
3. ✅ Mit Code auf Freizeit zugreifen
4. ✅ Dashboard zeigt korrekte Daten
5. ✅ Freizeit wechseln funktioniert
6. ⏳ Teilnehmer erstellen (nach Router-Anpassung)
7. ⏳ Familien erstellen (nach Router-Anpassung)
8. ⏳ Zahlungen erfassen (nach Router-Anpassung)

## Nächste Schritte

1. **Restliche Router anpassen** (siehe oben)
2. **Testen** mit mehreren Freizeiten
3. **Optional**: Admin-Bereich für Freizeit-Verwaltung
4. **Optional**: Passwort-Schutz für Freizeiten
5. **Optional**: Freizeit archivieren/deaktivieren

## Sicherheitshinweise

⚠️ **Produktion**: Der Session-Secret-Key sollte aus einer Umgebungsvariable kommen:

```python
# In app/config.py hinzufügen:
secret_key: str = "your-secret-key-from-env"

# In .env:
SECRET_KEY=your-generated-secret-key-here
```

Generieren mit:
```python
import secrets
print(secrets.token_urlsafe(32))
```
