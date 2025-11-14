# Regelwerk-Dokumentation

## Übersicht

Das Regelwerk-System ermöglicht die flexible Definition von Preisstrukturen für Freizeiten und Veranstaltungen. Regelwerke werden als YAML-Dateien definiert und in der Datenbank gespeichert.

## YAML-Struktur

### Vollständiges Beispiel

```yaml
name: "Kinderfreizeit 2024"
type: "kinder"
description: "Regelwerk für die Sommerfreizeit 2024"
valid_from: "2024-01-01"
valid_until: "2024-12-31"

age_groups:
  - min_age: 6
    max_age: 9
    price: 140.00
  - min_age: 10
    max_age: 12
    price: 150.00
  - min_age: 13
    max_age: 17
    price: 160.00

role_discounts:
  betreuer:
    discount_percent: 50
    max_count: 10
  kueche:
    discount_percent: 100
    max_count: 2
  techniker:
    discount_percent: 75
    max_count: 5

family_discount:
  enabled: true
  second_child_percent: 10
  third_plus_child_percent: 20
```

## Parameter-Referenz

### Pflichtfelder

#### `name` (String, erforderlich)
**Beschreibung**: Der Name des Regelwerks
**Format**: Beliebiger String
**Beispiel**: `"Kinderfreizeit 2024"`, `"Jugendfreizeit Sommer"`
**Verwendung**: Wird in der UI angezeigt und zur Identifikation verwendet

#### `type` (String, erforderlich)
**Beschreibung**: Der Typ der Freizeit
**Format**: Beliebiger String (empfohlen: lowercase)
**Beispiele**:
- `"kinder"` - Kinderfreizeit
- `"jugend"` - Jugendfreizeit
- `"familie"` - Familienfreizeit
- `"camp"` - Camp/Lager
**Verwendung**: Kategorisierung und Filterung von Regelwerken

#### `valid_from` (Datum, erforderlich)
**Beschreibung**: Startdatum der Gültigkeit
**Format**: `YYYY-MM-DD` (ISO 8601)
**Beispiel**: `"2024-01-01"`
**Validierung**: Muss gültiges Datum sein
**Verwendung**: Regelwerk wird nur für Events verwendet, deren Startdatum innerhalb des Gültigkeitszeitraums liegt

#### `valid_until` (Datum, erforderlich)
**Beschreibung**: Enddatum der Gültigkeit
**Format**: `YYYY-MM-DD` (ISO 8601)
**Beispiel**: `"2024-12-31"`
**Validierung**: Muss gültiges Datum sein, sollte >= `valid_from` sein
**Verwendung**: Regelwerk wird nur für Events verwendet, deren Startdatum innerhalb des Gültigkeitszeitraums liegt

#### `age_groups` (Array, erforderlich)
**Beschreibung**: Liste von Altersgruppen mit zugehörigen Preisen
**Format**: Array von Objekten
**Mindestanzahl**: 1
**Validierung**: Mindestens eine Altersgruppe muss definiert sein

##### Altersgruppen-Objekt

```yaml
age_groups:
  - min_age: 6        # Mindestalter (Integer, erforderlich)
    max_age: 9        # Höchstalter (Integer, erforderlich)
    price: 140.00     # Preis in Euro (Float, erforderlich)
```

**Parameter**:
- `min_age` (Integer, erforderlich): Mindestalter für diese Gruppe
- `max_age` (Integer, erforderlich): Höchstalter für diese Gruppe
- `price` (Float, erforderlich): Basispreis in Euro für diese Altersgruppe

**Hinweise**:
- Altersgruppen sollten überschneidungsfrei sein
- Das Alter wird zum Startdatum des Events berechnet
- Wenn ein Teilnehmer in keine Altersgruppe passt, ist der Preis 0.00€

**Beispiel - Komplexe Altersstruktur**:
```yaml
age_groups:
  - min_age: 0
    max_age: 5
    price: 100.00    # Kleinkinder
  - min_age: 6
    max_age: 9
    price: 140.00    # Grundschulalter
  - min_age: 10
    max_age: 12
    price: 150.00    # Mittelstufe
  - min_age: 13
    max_age: 15
    price: 160.00    # Jugendliche
  - min_age: 16
    max_age: 17
    price: 170.00    # Ältere Jugendliche
  - min_age: 18
    max_age: 99
    price: 180.00    # Erwachsene
```

### Optionale Felder

#### `description` (String, optional)
**Beschreibung**: Ausführliche Beschreibung des Regelwerks
**Format**: Beliebiger String, kann mehrzeilig sein
**Beispiel**: `"Regelwerk für die Sommerfreizeit 2024 mit Sonderkonditionen"`
**Standard**: `null`
**Verwendung**: Wird in der Detailansicht angezeigt

#### `role_discounts` (Object, optional)
**Beschreibung**: Rabatte für bestimmte Rollen (z.B. Betreuer, Küchenpersonal)
**Format**: Objekt mit Rollennamen als Keys
**Standard**: `{}` (keine Rollenrabatte)

##### Rollenrabatt-Objekt

```yaml
role_discounts:
  betreuer:                    # Rollenname (lowercase empfohlen)
    discount_percent: 50       # Rabatt in Prozent (Float, erforderlich)
    max_count: 10             # Max. Anzahl (Integer, optional)
```

**Parameter**:
- **Rollenname** (String): Name der Rolle (z.B. `betreuer`, `kueche`, `techniker`)
  - Wird case-insensitive verglichen
  - Muss mit einem Rollennamen in der Datenbank übereinstimmen

- `discount_percent` (Float, erforderlich): Rabatt in Prozent
  - Wertebereich: 0.0 bis 100.0
  - 50 = 50% Rabatt (halber Preis)
  - 100 = 100% Rabatt (kostenlos)

- `max_count` (Integer, optional): Maximale Anzahl von Personen mit diesem Rabatt
  - Wenn erreicht, erhalten weitere Personen dieser Rolle keinen Rabatt
  - **Hinweis**: Aktuell nicht implementiert, für zukünftige Versionen vorgesehen

**Beispiele**:

```yaml
# Einfaches Beispiel
role_discounts:
  betreuer:
    discount_percent: 50

# Mehrere Rollen mit unterschiedlichen Rabatten
role_discounts:
  betreuer:
    discount_percent: 50
    max_count: 10
  kueche:
    discount_percent: 100    # Küchenpersonal ist kostenlos
    max_count: 2
  techniker:
    discount_percent: 75
    max_count: 3
  fahrer:
    discount_percent: 60
```

**Berechnung**:
1. Basispreis wird aus Altersgruppe ermittelt
2. Alle Rabatte werden **vom Basispreis** berechnet (nicht gestapelt!)
3. `Endpreis = Basispreis - (Basispreis × Rollenrabatt/100) - (Basispreis × Familienrabatt/100)`

#### `family_discount` (Object, optional)
**Beschreibung**: Konfiguration für Geschwisterrabatte
**Format**: Objekt mit Rabatt-Konfiguration
**Standard**: `{ enabled: false }`

##### Familienrabatt-Objekt

```yaml
family_discount:
  enabled: true                    # Aktivierung (Boolean, erforderlich)
  first_child_percent: 0           # Rabatt 1. Kind (Float, optional, Standard: 0)
  second_child_percent: 10         # Rabatt 2. Kind (Float, erforderlich wenn enabled)
  third_plus_child_percent: 20     # Rabatt ab 3. Kind (Float, erforderlich wenn enabled)
```

**Parameter**:
- `enabled` (Boolean, erforderlich): Aktiviert/deaktiviert Familienrabatte
  - `true`: Familienrabatte werden angewendet
  - `false`: Keine Familienrabatte

- `first_child_percent` (Float, optional): Rabatt für das erste Kind
  - Wertebereich: 0.0 bis 100.0
  - **Standard**: 0.0 (kein Rabatt für erstes Kind)
  - **Neu ab Version 1.1**: Ermöglicht Rabatt bereits ab dem ersten Kind

- `second_child_percent` (Float, erforderlich wenn enabled): Rabatt für das zweite Kind
  - Wertebereich: 0.0 bis 100.0
  - Wird auf das bereits nach Altersgruppe und Rolle berechnete Kind angewendet

- `third_plus_child_percent` (Float, erforderlich wenn enabled): Rabatt für das dritte und alle weiteren Kinder
  - Wertebereich: 0.0 bis 100.0
  - Gilt für alle Kinder ab dem dritten

**Hinweise**:
- Die Reihenfolge wird nach Geburtsdatum bestimmt (ältestes = erstes Kind)
- Familienrabatt wird **vom Basispreis** berechnet (nicht vom bereits reduzierten Preis!)
- Nur Teilnehmer derselben Familie profitieren
- **Rückwärtskompatibilität**: Bestehende Regelwerke ohne `first_child_percent` funktionieren weiterhin (Standard: 0%)

**Beispiele**:

```yaml
# Standard-Staffelung (ab 2. Kind)
family_discount:
  enabled: true
  second_child_percent: 10      # 2. Kind: 10% Rabatt
  third_plus_child_percent: 20  # ab 3. Kind: 20% Rabatt

# Mit Rabatt ab 1. Kind (NEU)
family_discount:
  enabled: true
  first_child_percent: 5        # 1. Kind: 5% Rabatt
  second_child_percent: 15      # 2. Kind: 15% Rabatt
  third_plus_child_percent: 25  # ab 3. Kind: 25% Rabatt

# Großzügige Staffelung
family_discount:
  enabled: true
  second_child_percent: 15
  third_plus_child_percent: 30

# Deaktiviert
family_discount:
  enabled: false
```

**Berechnungsbeispiel 1 - Standard (ohne first_child_percent)**:
```
Familie mit 3 Kindern, alle 10 Jahre alt, Basispreis 150€:

Kind 1 (ältestes): 150€ - 0% Familienrabatt = 150€
Kind 2:            150€ - 10% Familienrabatt = 135€
Kind 3:            150€ - 20% Familienrabatt = 120€

Gesamt: 405€ statt 450€ (Ersparnis: 45€)
```

**Berechnungsbeispiel 2 - Mit Rabatt ab 1. Kind (NEU)**:
```
Familie mit 3 Kindern, alle 10 Jahre alt, Basispreis 140€:
(first_child_percent: 5, second_child_percent: 15, third_plus_child_percent: 25)

Kind 1 (ältestes): 140€ - 5% Familienrabatt = 133€
Kind 2:            140€ - 15% Familienrabatt = 119€
Kind 3:            140€ - 25% Familienrabatt = 105€

Gesamt: 357€ statt 420€ (Ersparnis: 63€)
```

## Preisberechnung

### Berechnungsreihenfolge

Die Preisberechnung erfolgt in folgender Reihenfolge:

1. **Basispreis ermitteln** (aus Altersgruppe)
2. **Rollenrabatt vom Basispreis berechnen** (falls vorhanden)
3. **Familienrabatt vom Basispreis berechnen** (falls aktiviert und anwendbar)
4. **Alle Rabatte vom Basispreis abziehen**
5. **Manuelle Rabatte/Überschreibungen** (in der UI)

### Formel

**WICHTIG**: Alle Rabatte werden vom Basispreis berechnet, nicht gestapelt!

```
Rollenrabatt_Betrag = Basispreis × (Rollenrabatt/100)
Familienrabatt_Betrag = Basispreis × (Familienrabatt/100)
Manueller_Rabatt_Betrag = Basispreis × (Manueller_Rabatt/100)

Endpreis = Basispreis - Rollenrabatt_Betrag - Familienrabatt_Betrag - Manueller_Rabatt_Betrag
```

Oder bei manueller Preisüberschreibung:
```
Endpreis = Manuell_gesetzter_Preis
```

### Berechnungsbeispiele

#### Beispiel 1: Einfache Berechnung
```yaml
age_groups:
  - min_age: 10
    max_age: 12
    price: 150.00
```

**Teilnehmer**: 11 Jahre alt, Rolle "Kind"
**Berechnung**:
- Basispreis: 150€
- Kein Rollenrabatt (Kind ist nicht in role_discounts)
- Kein Familienrabatt (erstes Kind)
- **Endpreis: 150€**

#### Beispiel 2: Mit Rollenrabatt
```yaml
age_groups:
  - min_age: 18
    max_age: 99
    price: 180.00

role_discounts:
  betreuer:
    discount_percent: 50
```

**Teilnehmer**: 25 Jahre alt, Rolle "Betreuer"
**Berechnung**:
- Basispreis: 180€
- Rollenrabatt: 50% = 180€ × (1 - 0.5) = 90€
- Kein Familienrabatt
- **Endpreis: 90€**

#### Beispiel 3: Mit Familienrabatt
```yaml
age_groups:
  - min_age: 6
    max_age: 12
    price: 140.00

family_discount:
  enabled: true
  second_child_percent: 10
  third_plus_child_percent: 20
```

**Familie mit 3 Kindern** (alle 6-12 Jahre):
- Kind 1: 140€ × (1 - 0) = **140€**
- Kind 2: 140€ × (1 - 0.1) = **126€**
- Kind 3: 140€ × (1 - 0.2) = **112€**
- **Gesamt: 378€** (statt 420€)

#### Beispiel 4: Kombination Rollen- und Familienrabatt
```yaml
age_groups:
  - min_age: 10
    max_age: 15
    price: 150.00

role_discounts:
  betreuer:
    discount_percent: 50

family_discount:
  enabled: true
  second_child_percent: 10
  third_plus_child_percent: 20
```

**Szenario**: Jugendlicher Betreuer (14 Jahre), zweites Kind in der Familie
**Berechnung**:
1. Basispreis: 150€
2. Rollenrabatt-Betrag: 150€ × 50% = 75€
3. Familienrabatt-Betrag: 150€ × 10% = 15€
4. **Endpreis: 150€ - 75€ - 15€ = 60€**

#### Beispiel 5: Komplexe Familie
```yaml
age_groups:
  - min_age: 6
    max_age: 9
    price: 140.00
  - min_age: 10
    max_age: 15
    price: 150.00

role_discounts:
  betreuer:
    discount_percent: 50

family_discount:
  enabled: true
  second_child_percent: 10
  third_plus_child_percent: 20
```

**Familie**:
- Kind 1: 14 Jahre, Betreuer
  - Basis: 150€, Rollenrabatt: 150€ × 50% = 75€, Familienrabatt: 0€
  - **Endpreis: 150€ - 75€ = 75€**
- Kind 2: 12 Jahre, Teilnehmer
  - Basis: 150€, Rollenrabatt: 0€, Familienrabatt: 150€ × 10% = 15€
  - **Endpreis: 150€ - 15€ = 135€**
- Kind 3: 8 Jahre, Teilnehmer
  - Basis: 140€, Rollenrabatt: 0€, Familienrabatt: 140€ × 20% = 28€
  - **Endpreis: 140€ - 28€ = 112€**

**Familiengesamtpreis: 322€** (statt 440€ ohne Rabatte)

## Import und Export

### Import

**Via Web-Interface**:
1. Navigiere zu "Regelwerke" → "Regelwerk importieren"
2. Wähle YAML-Datei aus
3. System validiert automatisch die Struktur
4. Bei Erfolg wird das Regelwerk in der Datenbank gespeichert

**Validierung beim Import**:
- Alle Pflichtfelder vorhanden?
- Datumsformat korrekt?
- Altersgruppen korrekt definiert?
- Bei Fehler: Detaillierte Fehlermeldung

### Export

**Via Web-Interface**:
1. Navigiere zu Regelwerk-Details
2. Klicke auf "Exportieren"
3. YAML-Datei wird heruntergeladen

**Export-Format**:
- Identisch zum Import-Format
- Kann direkt wieder importiert werden
- Optional: Manuell bearbeiten und re-importieren

### Manuelles Bearbeiten

**Via Web-Interface**:
1. Navigiere zu Regelwerk-Details
2. Klicke auf "Bearbeiten"
3. YAML direkt im Browser bearbeiten
4. Speichern → automatische Validierung

**Hinweise**:
- Tab-Taste fügt 2 Leerzeichen ein (YAML-konform)
- Syntax-Fehler werden beim Speichern angezeigt
- Bei Fehler: Änderungen nicht gespeichert

## Best Practices

### 1. Altersgruppen sinnvoll definieren

✅ **Gut**:
```yaml
age_groups:
  - min_age: 6
    max_age: 9
    price: 140.00
  - min_age: 10
    max_age: 12
    price: 150.00
```

❌ **Vermeiden**:
```yaml
age_groups:
  - min_age: 6
    max_age: 8
    price: 140.00
  # Lücke zwischen 9 und 10!
  - min_age: 10
    max_age: 12
    price: 150.00
```

### 2. Überschneidungen vermeiden

❌ **Problematisch**:
```yaml
age_groups:
  - min_age: 6
    max_age: 10
    price: 140.00
  - min_age: 10  # Überschneidung bei 10 Jahren!
    max_age: 12
    price: 150.00
```

✅ **Besser**:
```yaml
age_groups:
  - min_age: 6
    max_age: 9
    price: 140.00
  - min_age: 10
    max_age: 12
    price: 150.00
```

### 3. Gültigkeitszeitraum großzügig wählen

✅ **Empfohlen**:
```yaml
valid_from: "2024-01-01"
valid_until: "2024-12-31"  # Ganzes Jahr
```

### 4. Rollenrabatte dokumentieren

✅ **Gut dokumentiert**:
```yaml
name: "Kinderfreizeit 2024"
description: |
  Regelwerk mit Rabatten:
  - Betreuer: 50% Rabatt (max. 10 Personen)
  - Küche: 100% Rabatt (max. 2 Personen)

role_discounts:
  betreuer:
    discount_percent: 50
    max_count: 10
  kueche:
    discount_percent: 100
    max_count: 2
```

### 5. Familienrabatte staffeln

✅ **Empfohlene Staffelung**:
```yaml
family_discount:
  enabled: true
  second_child_percent: 10
  third_plus_child_percent: 20
```

Alternative für kleinere Budgets:
```yaml
family_discount:
  enabled: true
  second_child_percent: 5
  third_plus_child_percent: 15
```

## Häufige Fehler

### Fehler 1: Fehlende Pflichtfelder
```yaml
# ❌ FEHLER: 'valid_from' fehlt
name: "Test"
type: "kinder"
age_groups:
  - min_age: 6
    max_age: 12
    price: 140.00
```

**Lösung**: Alle Pflichtfelder angeben

### Fehler 2: Falsches Datumsformat
```yaml
# ❌ FEHLER: Falsches Format
valid_from: "01.01.2024"
```

✅ **Korrekt**:
```yaml
valid_from: "2024-01-01"
```

### Fehler 3: Leere Altersgruppen
```yaml
# ❌ FEHLER: Keine Altersgruppen
age_groups: []
```

✅ **Korrekt**:
```yaml
age_groups:
  - min_age: 0
    max_age: 99
    price: 150.00
```

### Fehler 4: Unvollständige Altersgruppen
```yaml
# ❌ FEHLER: 'price' fehlt
age_groups:
  - min_age: 6
    max_age: 12
```

✅ **Korrekt**:
```yaml
age_groups:
  - min_age: 6
    max_age: 12
    price: 140.00
```

## Versionierung

Es wird empfohlen, für jede Saison ein neues Regelwerk anzulegen:

```yaml
# Frühling 2024
name: "Osterfreizeit 2024"
valid_from: "2024-03-01"
valid_until: "2024-04-30"

# Sommer 2024
name: "Sommerfreizeit 2024"
valid_from: "2024-06-01"
valid_until: "2024-09-01"
```

## Erweiterte Beispiele

### Beispiel 1: Kinderfreizeit mit Betreuern

```yaml
name: "Kinderfreizeit Sommer 2024"
type: "kinder"
description: "Regelwerk für die Sommerfreizeit mit gestaffelten Preisen"
valid_from: "2024-06-01"
valid_until: "2024-09-01"

age_groups:
  - min_age: 6
    max_age: 7
    price: 135.00
  - min_age: 8
    max_age: 9
    price: 140.00
  - min_age: 10
    max_age: 12
    price: 150.00

role_discounts:
  betreuer:
    discount_percent: 50
    max_count: 12
  kueche:
    discount_percent: 100
    max_count: 2

family_discount:
  enabled: true
  second_child_percent: 10
  third_plus_child_percent: 20
```

### Beispiel 2: Jugendfreizeit ohne Familienrabatt

```yaml
name: "Jugendfreizeit 2024"
type: "jugend"
description: "Regelwerk für Jugendliche ab 13 Jahren"
valid_from: "2024-01-01"
valid_until: "2024-12-31"

age_groups:
  - min_age: 13
    max_age: 15
    price: 160.00
  - min_age: 16
    max_age: 17
    price: 170.00

role_discounts:
  betreuer:
    discount_percent: 40
    max_count: 8

family_discount:
  enabled: false  # Kein Familienrabatt für Jugendliche
```

### Beispiel 3: Familienfreizeit

```yaml
name: "Familienfreizeit 2024"
type: "familie"
description: "Regelwerk für Familien mit Kindern und Erwachsenen"
valid_from: "2024-01-01"
valid_until: "2024-12-31"

age_groups:
  - min_age: 0
    max_age: 5
    price: 100.00    # Kleinkinder
  - min_age: 6
    max_age: 12
    price: 140.00    # Kinder
  - min_age: 13
    max_age: 17
    price: 160.00    # Jugendliche
  - min_age: 18
    max_age: 99
    price: 200.00    # Erwachsene

role_discounts:
  betreuer:
    discount_percent: 30
  kueche:
    discount_percent: 50

family_discount:
  enabled: true
  second_child_percent: 15
  third_plus_child_percent: 25
```

## Troubleshooting

### Problem: Regelwerk wird nicht angewendet

**Mögliche Ursachen**:
1. Gültigkeitszeitraum passt nicht zum Event-Datum
2. Regelwerk ist nicht aktiv gesetzt
3. Falsches Regelwerk wurde dem Event zugeordnet

**Lösung**:
- Prüfe `valid_from` und `valid_until`
- Stelle sicher, dass `is_active = true` in der Datenbank
- Überprüfe die Event-Regelwerk-Zuordnung

### Problem: Preis wird nicht korrekt berechnet

**Debugging-Schritte**:
1. Prüfe, ob Teilnehmeralter in eine Altersgruppe fällt
2. Prüfe Rollennamen (case-insensitive, aber exakte Schreibweise)
3. Prüfe Familienposition (Reihenfolge nach Geburtsdatum)
4. Überprüfe manuelle Rabatte/Überschreibungen

### Problem: Import schlägt fehl

**Häufige Ursachen**:
- YAML-Syntax-Fehler (Einrückung!)
- Fehlende Pflichtfelder
- Falsches Datumsformat
- Ungültige Altersgruppen

**Lösung**: Verwende Online-YAML-Validator oder Export-Datei als Vorlage

## Support und Feedback

Bei Fragen oder Problemen mit Regelwerken:
1. Prüfe diese Dokumentation
2. Schaue dir die Beispiel-Regelwerke an
3. Erstelle ein Issue im Repository
