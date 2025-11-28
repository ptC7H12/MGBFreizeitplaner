# MGB Freizeitplaner - Flutter App

> **Standalone Multi-Platform App für iOS, macOS und Windows**

Eine komplette Neuentwicklung des MGB Freizeitplaners als native Cross-Platform-App mit Flutter. Alle Daten werden lokal gespeichert, kein Server oder Internet erforderlich.

## 📱 Unterstützte Plattformen

- ✅ **iOS** (iPhone & iPad)
- ✅ **macOS** (Desktop)
- ✅ **Windows** (Desktop)
- 🔄 **Linux** (optional, benötigt zusätzliche Config)
- 🔄 **Android** (optional, alle Dependencies vorhanden)

## 🎯 Features

### ✅ Bereits implementiert (MVP)

- **Event-Verwaltung**
  - Event-Auswahl (entspricht Login/Session)
  - Event-Info auf Dashboard

- **Dashboard**
  - Statistiken (Teilnehmer, Familien, Zahlungen, Ausgaben)
  - Schnellzugriff zu allen Funktionen
  - Navigation Drawer

- **Teilnehmer**
  - Liste aller Teilnehmer
  - Alter-Berechnung
  - Preis-Anzeige

- **Datenbank**
  - Komplett lokale SQLite-Datenbank (Drift ORM)
  - Alle Modelle portiert (Event, Participant, Family, Payment, etc.)
  - Migrations-System

- **Business Logic**
  - ✅ PriceCalculatorService (1:1 Port von Python)
  - ✅ RulesetParserService (YAML-Parsing & Validierung)

### 🔄 TODO (nächste Sprints)

- **Teilnehmer-Detail & Formular**
  - Teilnehmer erstellen/bearbeiten
  - Live-Preisberechnung (wie HTMX in Web-App)
  - Familienrabatt-Logik

- **Familien-Verwaltung**
  - CRUD für Familien
  - Familienmitglieder zuordnen

- **Zahlungen**
  - Zahlungen erfassen
  - Zahlungshistorie

- **Regelwerk-System**
  - YAML-Editor mit Syntax Highlighting
  - Regelwerk Import/Export
  - Live-Validierung

- **PDF-Generierung**
  - Rechnungen mit QR-Codes
  - Layout wie in Python-Version

- **Excel Import/Export**
  - Teilnehmer-Import aus Excel
  - Export-Funktionalität

- **Backup & Restore**
  - Datenbank-Backups
  - Wiederherstellung

## 🚀 Setup & Installation

### Voraussetzungen

1. **Flutter SDK** (3.2.0 oder höher)
   ```bash
   # Installation: https://docs.flutter.dev/get-started/install
   flutter --version
   ```

2. **Platform-spezifische Tools:**
   - **iOS/macOS**: Xcode (neueste Version)
   - **Windows**: Visual Studio 2022 mit "Desktop development with C++"
   - **Android** (optional): Android Studio

### 1. Flutter-Projekt einrichten

```bash
# In das Flutter-App-Verzeichnis wechseln
cd MGBFreizeitplaner/flutter_app

# Dependencies installieren
flutter pub get

# Code-Generierung ausführen (für Drift Database)
flutter pub run build_runner build --delete-conflicting-outputs
```

### 2. App starten

#### macOS Desktop
```bash
flutter run -d macos
```

#### Windows Desktop
```bash
flutter run -d windows
```

#### iOS Simulator (nur auf macOS)
```bash
# Liste verfügbare Simulatoren
flutter devices

# Starte auf Simulator
flutter run -d "iPhone 15 Pro"
```

### 3. Build für Production

#### macOS
```bash
flutter build macos --release
# Output: build/macos/Build/Products/Release/mgb_freizeitplaner.app
```

#### Windows
```bash
flutter build windows --release
# Output: build\windows\runner\Release\
```

#### iOS (erfordert Apple Developer Account)
```bash
flutter build ios --release
# Dann in Xcode öffnen und zu App Store hochladen
```

## 📂 Projektstruktur

```
flutter_app/
├── lib/
│   ├── main.dart                      # App Entry Point
│   │
│   ├── data/                          # Daten-Layer
│   │   ├── database/
│   │   │   ├── app_database.dart      # Drift Database Definition
│   │   │   └── app_database.g.dart    # Generiert von build_runner
│   │   ├── models/                    # (Optional: Pydantic-ähnliche Models)
│   │   └── repositories/              # Data Access Layer
│   │
│   ├── services/                      # Business Logic (von Python portiert)
│   │   ├── price_calculator_service.dart    # ✅ Portiert (412 Zeilen)
│   │   ├── ruleset_parser_service.dart      # ✅ Portiert
│   │   ├── invoice_generator_service.dart   # TODO
│   │   ├── excel_service.dart               # TODO
│   │   └── backup_service.dart              # TODO
│   │
│   ├── providers/                     # State Management (Riverpod)
│   │   ├── database_provider.dart     # Singleton DB-Instanz
│   │   └── current_event_provider.dart # Aktuelles Event (Session-Ersatz)
│   │
│   ├── screens/                       # UI Screens
│   │   ├── auth/
│   │   │   └── event_selection_screen.dart  # ✅ Event-Auswahl
│   │   ├── dashboard/
│   │   │   └── dashboard_screen.dart        # ✅ Hauptübersicht
│   │   ├── participants/
│   │   │   └── participants_list_screen.dart # ✅ Teilnehmer-Liste
│   │   ├── families/                        # TODO
│   │   ├── payments/                        # TODO
│   │   ├── expenses/                        # TODO
│   │   ├── incomes/                         # TODO
│   │   ├── rulesets/                        # TODO
│   │   └── cash_status/                     # TODO
│   │
│   ├── widgets/                       # Wiederverwendbare Widgets
│   │   ├── forms/                     # Form-Widgets
│   │   ├── charts/                    # Charts (fl_chart)
│   │   └── common/                    # Common Widgets
│   │
│   └── utils/                         # Helper-Funktionen
│       ├── validators.dart            # Validierungen (IBAN, Email, etc.)
│       └── datetime_utils.dart        # Datum-Utilities
│
├── ios/                               # iOS-spezifische Config
├── macos/                             # macOS-spezifische Config
├── windows/                           # Windows-spezifische Config
│
├── pubspec.yaml                       # Dependencies
└── README.md                          # Diese Datei
```

## 🔧 Dependencies

### Datenbank & Persistence
- **drift** (^2.25.0) - Type-safe SQL ORM für Dart
- **drift_flutter** - Flutter-Integration für Drift
- **sqlite3_flutter_libs** - SQLite Natives für alle Plattformen
- **path_provider** - Zugriff auf App-Verzeichnisse

### State Management
- **flutter_riverpod** (^2.6.1) - Modernes State Management

### Business Logic
- **yaml** (^3.1.2) - YAML-Parsing für Regelwerke
- **pdf** (^3.11.1) - PDF-Generierung (lokal!)
- **printing** (^5.13.4) - PDF-Druck & -Vorschau
- **excel** (^4.0.6) - Excel Import/Export
- **qr_flutter** (^4.1.0) - QR-Code-Generierung

### UI Components
- **fl_chart** (^0.70.4) - Charts für Dashboard
- **flutter_form_builder** (^10.1.0) - Formular-Handling
- **form_builder_validators** (^11.1.0) - Validierungen
- **file_picker** (^8.1.6) - Datei-Auswahl

### Development
- **drift_dev** - Code-Generator für Drift
- **build_runner** - Dart Code-Generation
- **flutter_lints** - Linting Rules

## 💾 Datenbank

### SQLite-Datei Location

Die Datenbank `freizeit_kassen.db` wird automatisch erstellt in:

- **macOS**: `~/Library/Containers/<app-id>/Data/Documents/`
- **Windows**: `C:\Users\<username>\AppData\Roaming\<app-name>\`
- **iOS**: App Sandbox (nicht direkt zugreifbar)

### Migrations

Drift unterstützt Schema-Migrationen ähnlich wie Alembic:

```dart
@override
int get schemaVersion => 1; // Erhöhen bei Schema-Änderungen

@override
MigrationStrategy get migration {
  return MigrationStrategy(
    onCreate: (Migrator m) async {
      await m.createAll();
    },
    onUpgrade: (Migrator m, int from, int to) async {
      // Migration-Logik hier
      if (from == 1 && to == 2) {
        // Schema-Änderungen
      }
    },
  );
}
```

### Code-Generierung

Nach Änderungen an `app_database.dart`:

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

## 🧪 Testing

```bash
# Alle Tests ausführen
flutter test

# Nur Unit Tests
flutter test test/unit/

# Nur Widget Tests
flutter test test/widget/

# Mit Coverage
flutter test --coverage
```

## 🐛 Debugging

### Drift SQL-Queries loggen

```dart
// In app_database.dart
@DriftDatabase(/* ... */)
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  @override
  QueryExecutor get executor => super.executor
    ..setLogListener((sql, params) {
      developer.log('SQL: $sql | Params: $params');
    });
}
```

### Flutter DevTools

```bash
# Öffne DevTools im Browser
flutter pub global run devtools
```

## 📊 Migration Status

### Portiert von Python → Dart

| Python-Modul | Dart-Äquivalent | Status | Zeilen |
|--------------|-----------------|--------|--------|
| `models/*.py` | `database/app_database.dart` | ✅ | ~500 |
| `price_calculator.py` | `services/price_calculator_service.dart` | ✅ | ~350 |
| `ruleset_parser.py` | `services/ruleset_parser_service.dart` | ✅ | ~400 |
| `invoice_generator.py` | `services/invoice_generator_service.dart` | ⏳ TODO | ~300 |
| `excel_service.py` | `services/excel_service.dart` | ⏳ TODO | ~200 |
| `backup_service.py` | `services/backup_service.dart` | ⏳ TODO | ~100 |

**Gesamt portiert: ~40% der Backend-Logik**

### UI-Screens

| Python-Template | Flutter-Screen | Status |
|----------------|----------------|--------|
| `auth/landing.html` | `event_selection_screen.dart` | ✅ |
| `dashboard.html` | `dashboard_screen.dart` | ✅ |
| `participants/list.html` | `participants_list_screen.dart` | ✅ (Basic) |
| `participants/form.html` | `participant_form_screen.dart` | ⏳ TODO |
| `families/list.html` | `families_list_screen.dart` | ⏳ TODO |
| `payments/list.html` | `payments_list_screen.dart` | ⏳ TODO |
| `rulesets/editor.html` | `ruleset_editor_screen.dart` | ⏳ TODO |
| `cash_status/main.html` | `cash_status_screen.dart` | ⏳ TODO |

**Gesamt: ~20% der UI fertig**

## 🎨 Design

### Theme

Die App nutzt Material Design 3 mit deutscher Lokalisierung:

```dart
ThemeData(
  colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
  useMaterial3: true,
)
```

### Lokalisierung

Aktuell: Deutsch (hardcoded)
TODO: `flutter_localizations` für i18n

## 📝 Nächste Schritte

### Sprint 1 (2-3 Wochen)
- [ ] Teilnehmer-Formular (Create/Edit)
- [ ] Live-Preisberechnung im Formular
- [ ] Familien-Verwaltung (CRUD)
- [ ] Zahlungen (CRUD)

### Sprint 2 (2-3 Wochen)
- [ ] Regelwerk-Editor (YAML)
- [ ] Regelwerk Import/Export
- [ ] Ausgaben/Einnahmen (CRUD)
- [ ] Kassenstand-Übersicht

### Sprint 3 (2-3 Wochen)
- [ ] PDF-Generierung (Rechnungen)
- [ ] Excel Import/Export
- [ ] Backup/Restore-Funktionalität
- [ ] Settings-Screen

### Sprint 4 (1-2 Wochen)
- [ ] Testing (Unit, Widget, Integration)
- [ ] Platform-spezifische Anpassungen
- [ ] App Icons & Splash Screens
- [ ] App Store Vorbereitung

## 🔗 Ressourcen

- [Flutter Dokumentation](https://docs.flutter.dev/)
- [Drift Dokumentation](https://drift.simonbinder.eu/)
- [Riverpod Dokumentation](https://riverpod.dev/)
- [Original Python-Projekt](../app/)

## 📄 Lizenz

Gleiche Lizenz wie das Original-Projekt.

## 👤 Autor

Migration durchgeführt von Claude (Anthropic) im Auftrag des Projekt-Owners.

---

**Status:** 🟡 MVP Ready (~40% Complete)
**Letzte Aktualisierung:** 2025-01-28
