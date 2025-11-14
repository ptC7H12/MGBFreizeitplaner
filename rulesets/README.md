# Regelwerke (Rulesets)

Dieses Verzeichnis enthält YAML-Dateien mit Regelwerken für die Preisberechnung von Freizeiten.

## Struktur eines Regelwerks

```yaml
name: "Name des Regelwerks"
type: "kinder|jugend|familie|erwachsene"
valid_from: "2024-01-01"
valid_until: "2024-12-31"

age_groups:
  - min_age: 6
    max_age: 11
    price: 140.00
  - min_age: 12
    max_age: 17
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
  first_child_percent: 0       # Optional, Standard: 0%
  second_child_percent: 10
  third_plus_child_percent: 20
```

## Altersgruppen (age_groups)

Definiert Preise basierend auf dem Alter des Teilnehmers.

- **min_age**: Mindestalter für diese Preisgruppe (inklusive)
- **max_age**: Höchstalter für diese Preisgruppe (inklusive)
- **price**: Basispreis in Euro

Das System ermittelt automatisch die passende Altersgruppe basierend auf dem Alter des Teilnehmers zum Zeitpunkt der Freizeit.

## Rollenrabatte (role_discounts)

Rabatte für bestimmte Rollen (z.B. Betreuer, Küchenpersonal).

- **discount_percent**: Rabatt in Prozent (0-100)
- **max_count**: Maximale Anzahl an Personen mit diesem Rabatt (optional)

Beispiel:
```yaml
role_discounts:
  betreuer:
    discount_percent: 50  # Betreuer zahlen 50% vom Basispreis
    max_count: 10
  kueche:
    discount_percent: 100  # Küchenpersonal ist kostenlos
    max_count: 2
```

## Familienrabatte (family_discount)

Rabatte für Familien mit mehreren Kindern.

### Optionen

- **enabled**: `true` oder `false` - Aktiviert/Deaktiviert Familienrabatte
- **first_child_percent**: Rabatt für das erste Kind (optional, Standard: 0%)
- **second_child_percent**: Rabatt für das zweite Kind
- **third_plus_child_percent**: Rabatt für das dritte und alle weiteren Kinder

### Beispiele

**Standard-Familienrabatt (ab 2. Kind):**
```yaml
family_discount:
  enabled: true
  second_child_percent: 10
  third_plus_child_percent: 20
```
- 1. Kind: 140€ (kein Rabatt)
- 2. Kind: 126€ (10% Rabatt)
- 3. Kind: 112€ (20% Rabatt)

**Familienrabatt ab 1. Kind:**
```yaml
family_discount:
  enabled: true
  first_child_percent: 5
  second_child_percent: 15
  third_plus_child_percent: 25
```
- 1. Kind: 133€ (5% Rabatt)
- 2. Kind: 119€ (15% Rabatt)
- 3. Kind: 105€ (25% Rabatt)

## Preisberechnung

Die Endpreisberechnung erfolgt in dieser Reihenfolge:

1. **Basispreis** aus Altersgruppe ermitteln
2. **Rollenrabatt** anwenden (falls vorhanden)
3. **Familienrabatt** anwenden (falls vorhanden)
4. **Manuelle Rabatte** anwenden (falls vom Nutzer gesetzt)

**Wichtig:** Rabatte werden vom Basispreis berechnet und dann addiert, nicht gestapelt!

### Beispiel

Teilnehmer: 8 Jahre alt, Rolle: Kind, 2. Kind in Familie

```
Basispreis (6-11 Jahre):     140,00 €
Rollenrabatt (0%):             0,00 €
Familienrabatt (10%):        -14,00 €
─────────────────────────────────────
Endpreis:                    126,00 €
```

## Verwendung

1. YAML-Datei im Ordner `rulesets/` erstellen
2. In der Anwendung unter "Regelwerke" importieren
3. Als aktives Regelwerk für ein Event festlegen

Die Anwendung wendet das Regelwerk automatisch bei der Preisberechnung an.

## Beispiele

Siehe `examples/` Ordner für vorkonfigurierte Regelwerke:

- **kinder_2024.yaml**: Standard-Kinderfreizeit mit Familienrabatt ab 2. Kind
- **familie_rabatt_2024.yaml**: Familienfreizeit mit Rabatt ab 1. Kind
