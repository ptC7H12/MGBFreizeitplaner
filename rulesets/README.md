# Regelwerke (Rulesets)

Dieses Verzeichnis enthält YAML-Dateien mit Regelwerken für die Preisberechnung von Freizeiten.

**Für detaillierte Dokumentation siehe**: [REGELWERK_DOKUMENTATION.md](../docs/REGELWERK_DOKUMENTATION.md)

## Schnellstart

### Minimales Beispiel

```yaml
name: "Kinderfreizeit 2024"
type: "kinder"
valid_from: "2024-01-01"
valid_until: "2024-12-31"

age_groups:
  - min_age: 6
    max_age: 12
    price: 140.00

family_discount:
  enabled: true
  second_child_percent: 10
  third_plus_child_percent: 20
```

### Mit Rabatt ab 1. Kind (NEU)

```yaml
family_discount:
  enabled: true
  first_child_percent: 5       # Optional: Rabatt bereits beim ersten Kind
  second_child_percent: 15
  third_plus_child_percent: 25
```

## Verfügbare Beispiele

- **kinder_2024.yaml**: Standard-Kinderfreizeit
- **familie_rabatt_2024.yaml**: Mit Rabatt ab 1. Kind

## Verwendung

1. YAML-Datei in `rulesets/` erstellen
2. In der Anwendung unter "Regelwerke" importieren
3. Als aktives Regelwerk für ein Event festlegen

**Vollständige Dokumentation**: [REGELWERK_DOKUMENTATION.md](../docs/REGELWERK_DOKUMENTATION.md)
