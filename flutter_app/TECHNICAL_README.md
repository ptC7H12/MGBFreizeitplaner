# MGBFreizeitplaner - Technical Documentation for AI Assistants

## Project Overview

**MGBFreizeitplaner** is a comprehensive event management application for youth camps and retreats, built with Flutter for cross-platform deployment (iOS, macOS, Windows). It manages participants, families, payments, expenses, incomes, tasks, roles, and pricing rulesets.

**Original Stack:** Python/FastAPI + Jinja2 + HTMX + SQLite (web app)
**Current Stack:** Flutter + Dart + Drift ORM + Riverpod + SQLite (standalone desktop/mobile app)

**Key Domain:** German youth camp financial management with complex pricing rules based on age groups, family discounts, and role-based discounts.

---

## Architecture Overview

### Technology Stack

- **Framework:** Flutter 3.x
- **Language:** Dart
- **Database:** SQLite with Drift ORM (type-safe SQL)
- **State Management:** Riverpod (Provider pattern)
- **UI Framework:** Material Design 3
- **Charts:** fl_chart for financial visualizations
- **PDF Generation:** pdf package
- **Excel:** excel package for import/export
- **Localization:** German (de_DE)

### Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                         UI Layer                             │
│              (Screens + Widgets)                             │
│         lib/screens/* + lib/widgets/*                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    State Management                          │
│                  (Riverpod Providers)                        │
│                   lib/providers/*                            │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic                             │
│          (Services + Repositories)                           │
│      lib/services/* + lib/data/repositories/*                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│              (Drift Database + Models)                       │
│                lib/data/database/*                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
flutter_app/
├── lib/
│   ├── data/
│   │   ├── database/
│   │   │   └── app_database.dart          # Main database definition (10 tables)
│   │   └── repositories/
│   │       ├── participant_repository.dart # Participant CRUD + price calculation
│   │       ├── family_repository.dart      # Family CRUD
│   │       ├── payment_repository.dart     # Payment CRUD
│   │       ├── expense_repository.dart     # Expense CRUD + category stats
│   │       ├── income_repository.dart      # Income CRUD + source stats
│   │       ├── ruleset_repository.dart     # Ruleset CRUD + YAML validation
│   │       ├── role_repository.dart        # Role CRUD + usage tracking
│   │       └── task_repository.dart        # Task CRUD + status tracking
│   │
│   ├── providers/
│   │   ├── database_provider.dart          # Database singleton
│   │   ├── current_event_provider.dart     # Current selected event state
│   │   ├── participant_provider.dart       # Participant state + streams
│   │   ├── family_provider.dart            # Family state
│   │   ├── payment_provider.dart           # Payment state
│   │   ├── expense_provider.dart           # Expense state + statistics
│   │   ├── income_provider.dart            # Income state + statistics
│   │   ├── ruleset_provider.dart           # Ruleset state
│   │   ├── role_provider.dart              # Role state + counts
│   │   ├── task_provider.dart              # Task state + filters
│   │   ├── excel_import_provider.dart      # Excel import service
│   │   └── pdf_export_provider.dart        # PDF export service
│   │
│   ├── screens/
│   │   ├── auth/
│   │   │   └── event_selection_screen.dart # Event selection (replaces login)
│   │   ├── dashboard/
│   │   │   └── dashboard_screen.dart       # Main overview with statistics
│   │   ├── participants/
│   │   │   ├── participants_list_screen.dart   # List with search/filters
│   │   │   ├── participant_form_screen.dart    # Create/Edit form (700+ lines)
│   │   │   └── participant_import_screen.dart  # Excel import UI
│   │   ├── families/
│   │   │   ├── families_list_screen.dart       # Family list
│   │   │   └── family_form_screen.dart         # Family create/edit
│   │   ├── payments/
│   │   │   ├── payments_list_screen.dart       # Payment list
│   │   │   └── payment_form_screen.dart        # Payment create/edit
│   │   ├── expenses/
│   │   │   ├── expenses_list_screen.dart       # Expense list with categories
│   │   │   └── expense_form_screen.dart        # Expense create/edit
│   │   ├── incomes/
│   │   │   ├── incomes_list_screen.dart        # Income list with sources
│   │   │   └── income_form_screen.dart         # Income create/edit
│   │   ├── rulesets/
│   │   │   ├── rulesets_list_screen.dart       # Ruleset list with active indicator
│   │   │   └── ruleset_form_screen.dart        # YAML editor with validation
│   │   ├── roles/
│   │   │   ├── roles_list_screen.dart          # Role list with participant counts
│   │   │   └── role_form_screen.dart           # Role create/edit
│   │   ├── tasks/
│   │   │   └── tasks_screen.dart               # Task management (integrated form)
│   │   └── cash_status/
│   │       └── cash_status_screen.dart         # Financial overview with charts
│   │
│   ├── widgets/
│   │   └── forms/
│   │       └── price_preview_widget.dart       # Live price calculation (reactive)
│   │
│   ├── services/
│   │   ├── price_calculator_service.dart       # Price calculation logic
│   │   ├── ruleset_parser_service.dart         # YAML parsing & validation
│   │   ├── excel_import_service.dart           # Excel import logic
│   │   └── pdf_export_service.dart             # PDF generation
│   │
│   ├── utils/
│   │   ├── validators.dart                     # Form validators (email, IBAN, etc.)
│   │   └── date_utils.dart                     # German date formatting + age calc
│   │
│   └── main.dart                               # App entry point
│
├── pubspec.yaml                                # Dependencies
└── TECHNICAL_README.md                         # This file
```

---

## Database Schema (10 Tables)

All tables are defined in `lib/data/database/app_database.dart` using Drift annotations.

### Core Tables

1. **Events** - Veranstaltungen
   - `id`, `name`, `start_date`, `end_date`, `location`, `description`
   - One event active per session (selected in `current_event_provider`)

2. **Participants** - Teilnehmer (Main entity)
   - `id`, `event_id`, `first_name`, `last_name`, `birth_date`, `gender`
   - Address: `street`, `house_number`, `postal_code`, `city`, `country`
   - Contact: `email`, `phone`, `mobile`
   - Emergency: `emergency_contact_name`, `emergency_contact_phone`
   - Medical: `medical_info`, `allergies`, `medications`, `dietary_restrictions`, `swim_ability`
   - Pricing: `calculated_price`, `manual_price_override`, `discount_percent`
   - Relations: `family_id`, `role_id`
   - Soft delete: `is_active`

3. **Families** - Familien
   - `id`, `event_id`, `family_name`, contact info, address
   - Used for family discount calculations

4. **Payments** - Zahlungen
   - `id`, `event_id`, `amount`, `payment_date`, `payment_method`
   - Can be linked to `participant_id` OR `family_id` (not both)
   - Soft delete: `is_active`

5. **Expenses** - Ausgaben
   - `id`, `event_id`, `category`, `amount`, `expense_date`
   - Optional: `description`, `vendor`, `receipt_number`, `payment_method`
   - Categories: Verpflegung, Unterkunft, Transport, Material, Personal, Versicherung, Sonstiges
   - Soft delete: `is_active`

6. **Incomes** - Einnahmen
   - `id`, `event_id`, `source`, `amount`, `income_date`
   - Optional: `description`, `reference_number`, `payment_method`
   - Sources: Teilnehmerbeitrag, Spende, Zuschuss, Sponsoring, Merchandise, Sonstiges
   - Soft delete: `is_active`

7. **Rulesets** - Regelwerke (Pricing rules)
   - `id`, `event_id`, `name`, `yaml_content`, `valid_from`, `description`
   - Contains YAML definition of age groups, role discounts, family discounts
   - Active ruleset determined by `valid_from` date
   - Soft delete: `is_active`

8. **Roles** - Rollen
   - `id`, `event_id`, `name`, `description`
   - Examples: Mitarbeiter, Leitung, Küche, Technik
   - Used in rulesets for role-based discounts

9. **Tasks** - Aufgaben
   - `id`, `event_id`, `title`, `description`, `status`, `priority`, `due_date`
   - Optional: `assigned_to` (participant_id)
   - Status: pending, in_progress, completed
   - Priority: 1 (low), 2 (medium), 3 (high)

10. **Settings** - Einstellungen
    - `id`, `key`, `value`
    - App-wide configuration

---

## Key Business Logic

### Price Calculation (`price_calculator_service.dart`)

**Location:** `lib/services/price_calculator_service.dart` (~350 lines)

**Purpose:** Calculate participant price based on age, role, and family status.

**Algorithm:**
1. Get base price from age group in ruleset
2. Apply role discount (if participant has role)
3. Apply family discount (based on number of children in family)
4. Discounts are NON-STACKING (both calculated from base price, not cumulative)

**Key Method:**
```dart
static double calculateParticipantPrice({
  required int age,
  String? roleName,
  required Map<String, dynamic> rulesetData,
  int familyChildrenCount = 1,
})
```

**Called by:** `participant_repository.dart` on create/update

### Ruleset YAML Structure

**Location:** `lib/services/ruleset_parser_service.dart` (~400 lines)

**YAML Format:**
```yaml
name: "Sommerfreizeit 2024"
valid_from: 2024-01-01

age_groups:
  - name: "Kinder"
    min_age: 0
    max_age: 12
    base_price: 150.00
  - name: "Jugendliche"
    min_age: 13
    max_age: 17
    base_price: 180.00
  - name: "Erwachsene"
    min_age: 18
    max_age: 999
    base_price: 200.00

role_discounts:
  - role_name: "Mitarbeiter"
    discount_percent: 50.0
  - role_name: "Leitung"
    discount_percent: 100.0

family_discount:
  min_children: 2
  discount_percent_per_child:
    - children_count: 2
      discount_percent: 10.0
    - children_count: 3
      discount_percent: 15.0
```

**Validation:** Performed in `ruleset_repository.dart` before save

---

## State Management Patterns

### Riverpod Provider Types Used

1. **Provider** - For singletons (services, repositories)
   ```dart
   final databaseProvider = Provider<AppDatabase>((ref) => AppDatabase());
   ```

2. **StateNotifier + StateNotifierProvider** - For mutable state
   ```dart
   final currentEventProvider = StateNotifierProvider<CurrentEventNotifier, Event?>(...)
   ```

3. **StreamProvider** - For reactive data (database streams)
   ```dart
   final participantsProvider = StreamProvider<List<Participant>>((ref) {
     return repository.watchParticipantsByEvent(eventId);
   });
   ```

4. **FutureProvider** - For async data fetching
   ```dart
   final totalExpensesProvider = FutureProvider<double>((ref) async {...});
   ```

### Common Pattern

```dart
// In screen:
final participantsAsync = ref.watch(participantsProvider);

participantsAsync.when(
  data: (participants) => /* Build UI with data */,
  loading: () => CircularProgressIndicator(),
  error: (error, stack) => Text('Error: $error'),
);
```

---

## Repository Pattern

### Standard Repository Methods

All repositories in `lib/data/repositories/*` follow this pattern:

```dart
class XxxRepository {
  final AppDatabase _database;

  // Stream (reactive)
  Stream<List<Xxx>> watchXxxByEvent(int eventId)

  // Single fetch
  Future<Xxx?> getXxxById(int id)
  Future<List<Xxx>> getXxxByEvent(int eventId)

  // CRUD
  Future<int> createXxx({required params...})
  Future<bool> updateXxx({required int id, optional params...})
  Future<bool> deleteXxx(int id)  // Usually soft delete

  // Statistics/Aggregations
  Future<Map<String, dynamic>> getXxxStatistics(int eventId)
}
```

### Special Repository Features

**participant_repository.dart:**
- Auto-calculates price on create/update
- Validates age against event dates
- Handles family member count for discounts

**expense_repository.dart & income_repository.dart:**
- Category/Source aggregations
- Date range filtering
- Search by description/vendor/notes

**ruleset_repository.dart:**
- YAML validation before save
- Active ruleset determination by date
- Template generation

**role_repository.dart:**
- Prevents deletion if role is in use
- Tracks participant counts

**task_repository.dart:**
- Overdue task detection
- Upcoming tasks (next 7 days)
- Status and priority filtering

---

## UI Patterns

### Form Screens

**Pattern:** All form screens follow this structure:

```dart
class XxxFormScreen extends ConsumerStatefulWidget {
  final int? xxxId; // null = create, value = edit

  @override
  ConsumerState<XxxFormScreen> createState() => _XxxFormScreenState();
}

class _XxxFormScreenState extends ConsumerState<XxxFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _controller = TextEditingController();

  @override
  void initState() {
    if (widget.xxxId != null) {
      _loadXxx(); // Load existing data
    }
  }

  Future<void> _saveXxx() {
    if (!_formKey.currentState!.validate()) return;

    final repository = ref.read(xxxRepositoryProvider);
    if (widget.xxxId == null) {
      await repository.createXxx(...);
    } else {
      await repository.updateXxx(id: widget.xxxId!, ...);
    }
  }
}
```

### List Screens

**Pattern:** List screens with search/filter:

```dart
class XxxListScreen extends ConsumerStatefulWidget {
  @override
  ConsumerState<XxxListScreen> createState() => _XxxListScreenState();
}

class _XxxListScreenState extends ConsumerState<XxxListScreen> {
  String _searchQuery = '';
  String? _filter;

  List<Xxx> _filterItems(List<Xxx> items) {
    // Apply search and filters
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final itemsAsync = ref.watch(xxxProvider);

    return Scaffold(
      appBar: AppBar(
        actions: [
          IconButton(icon: Icon(Icons.filter_list), onPressed: _showFilter),
          IconButton(icon: Icon(Icons.add), onPressed: () => navigate to form),
        ],
      ),
      body: Column([
        SearchBar(...),
        FilterChips(...),
        Expanded(
          child: itemsAsync.when(
            data: (items) => ListView.builder(...),
            loading: () => CircularProgressIndicator(),
            error: (e, _) => Text('Error: $e'),
          ),
        ),
      ]),
    );
  }
}
```

---

## Navigation Structure

```
EventSelectionScreen (/)
  └─> DashboardScreen
       ├─> ParticipantsListScreen
       │    ├─> ParticipantFormScreen (create/edit)
       │    └─> ParticipantImportScreen (Excel)
       ├─> FamiliesListScreen
       │    └─> FamilyFormScreen
       ├─> PaymentsListScreen
       │    └─> PaymentFormScreen
       ├─> ExpensesListScreen
       │    └─> ExpenseFormScreen
       ├─> IncomesListScreen
       │    └─> IncomeFormScreen
       ├─> RulesetsListScreen
       │    └─> RulesetFormScreen (YAML editor)
       ├─> RolesListScreen
       │    └─> RoleFormScreen
       ├─> TasksScreen (integrated form dialog)
       └─> CashStatusScreen (charts + PDF export)
```

**Navigation Pattern:**
```dart
Navigator.push(
  context,
  MaterialPageRoute(builder: (context) => XxxScreen()),
);
```

---

## Important Conventions

### Naming Patterns

- **Repositories:** `{entity}_repository.dart` → `XxxRepository` class
- **Providers:** `{entity}_provider.dart` → Multiple providers exported
- **Screens:** `{entity}_list_screen.dart` / `{entity}_form_screen.dart`
- **Services:** `{purpose}_service.dart` → Static methods or singleton

### Database Conventions

- **Table names:** Plural (participants, families, payments)
- **Class names:** Singular (Participant, Family, Payment)
- **Soft delete:** `is_active` boolean (default true)
- **Timestamps:** `created_at`, `updated_at` (auto-managed)
- **Foreign keys:** `{entity}_id` (e.g., `event_id`, `family_id`)

### German Terminology

- **Teilnehmer** = Participant
- **Familie** = Family
- **Zahlung** = Payment
- **Ausgabe** = Expense
- **Einnahme** = Income
- **Regelwerk** = Ruleset
- **Rolle** = Role
- **Aufgabe** = Task
- **Kassenstand** = Cash balance

---

## Common Tasks Guide

### Adding a New Field to Participant

1. **Database:** Update `Participants` table in `app_database.dart`
2. **Generate:** Run `flutter pub run build_runner build`
3. **Repository:** Update `createParticipant` and `updateParticipant` in `participant_repository.dart`
4. **Form:** Add field to `participant_form_screen.dart`
5. **Display:** Update `participants_list_screen.dart` if needed

### Creating a New CRUD Entity

1. **Database table:** Add to `app_database.dart`
2. **Repository:** Create `{entity}_repository.dart` with standard methods
3. **Provider:** Create `{entity}_provider.dart` with StreamProvider
4. **List screen:** Create `{entity}_list_screen.dart`
5. **Form screen:** Create `{entity}_form_screen.dart`
6. **Navigation:** Add to `dashboard_screen.dart` drawer

### Modifying Price Calculation

**File:** `lib/services/price_calculator_service.dart`

**Note:** Price is recalculated on every participant create/update in `participant_repository.dart`

**Affected areas:**
- `calculateParticipantPrice()` - Main calculation
- `_getBasePriceByAge()` - Age group lookup
- `_getRoleDiscount()` - Role discount lookup
- `_getFamilyDiscount()` - Family discount calculation

### Adding New Report/Export

1. **PDF:** Add method to `pdf_export_service.dart`
2. **Excel:** Add method to `excel_import_service.dart`
3. **UI:** Add export button to relevant screen
4. **Provider:** Use `pdfExportServiceProvider` or `excelImportServiceProvider`

---

## Testing the App

### Run on Windows (IntelliJ/VS Code)

```bash
cd flutter_app
flutter pub get
flutter pub run build_runner build
flutter run -d windows
```

### Run on macOS

```bash
flutter run -d macos
```

### Run on iOS Simulator

```bash
flutter run -d "iPhone 14 Pro"
```

### Database Location

- **Windows:** `%APPDATA%\com.example\mgbfreizeitplaner\databases\`
- **macOS:** `~/Library/Application Support/com.example.mgbfreizeitplaner/databases/`
- **iOS:** App sandbox documents directory

### Reset Database

Delete the database file and restart the app. Database will be recreated with schema.

---

## Performance Considerations

### Reactive Updates

All list screens use `StreamProvider` which automatically updates UI when database changes. No manual refresh needed.

### Price Recalculation

Participant prices are recalculated on:
1. Participant create/update
2. Family assignment change
3. Role assignment change
4. Manual price override

**NOT recalculated when:**
- Ruleset changes (would need manual migration)
- Family member count changes (would need batch update)

### Pagination

Currently NOT implemented. All lists load full data. If lists grow large (>1000 items), consider:
- Adding pagination to repositories
- Using `limit` and `offset` in Drift queries
- Implementing infinite scroll in list screens

---

## Error Handling Patterns

### Repository Level

```dart
Future<int> createXxx(...) async {
  try {
    // Validation
    if (invalidCondition) {
      throw Exception('Validation error message');
    }

    // Database operation
    return await _database.into(_database.xxxs).insert(...);
  } catch (e) {
    rethrow; // Let UI handle it
  }
}
```

### UI Level

```dart
try {
  await repository.createXxx(...);
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text('Erfolg!')),
  );
  Navigator.pop(context);
} catch (e) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text('Fehler: $e')),
  );
}
```

---

## Dependencies (pubspec.yaml)

### Core
- `flutter_riverpod` - State management
- `drift` - SQLite ORM
- `sqlite3_flutter_libs` - SQLite binaries
- `path_provider` - File system paths

### UI
- `intl` - Internationalization & formatting
- `fl_chart` - Charts
- `file_picker` - File selection dialogs

### Data
- `excel` - Excel import/export
- `pdf` - PDF generation
- `yaml` - YAML parsing

### Dev
- `build_runner` - Code generation
- `drift_dev` - Drift code generator

---

## Quick Reference: Finding Files

**"I need to modify participant price calculation"**
→ `lib/services/price_calculator_service.dart`

**"I need to add a field to participant form"**
→ `lib/screens/participants/participant_form_screen.dart`

**"I need to change database schema"**
→ `lib/data/database/app_database.dart` → then run `build_runner`

**"I need to add financial statistics"**
→ `lib/data/repositories/expense_repository.dart` or `income_repository.dart`

**"I need to modify dashboard stats"**
→ `lib/screens/dashboard/dashboard_screen.dart`

**"I need to change PDF export format"**
→ `lib/services/pdf_export_service.dart`

**"I need to add Excel import column"**
→ `lib/services/excel_import_service.dart` → `_parseRow()` method

**"I need to modify YAML ruleset structure"**
→ `lib/services/ruleset_parser_service.dart`

**"I need to add new chart to cash status"**
→ `lib/screens/cash_status/cash_status_screen.dart`

**"I need to change participant search logic"**
→ `lib/screens/participants/participants_list_screen.dart` → `_filterParticipants()`

---

## Migration Notes (Python → Flutter)

### Equivalent Concepts

| Python/FastAPI | Flutter/Dart |
|----------------|--------------|
| SQLAlchemy models | Drift tables |
| Jinja2 templates | Flutter widgets |
| HTMX live updates | StreamBuilder + Riverpod |
| Flask sessions | StateNotifier (current event) |
| Pydantic validation | Form validators |
| FastAPI routes | Screen navigation |
| Background tasks | Isolates (not yet used) |

### Key Differences

- **No server:** All logic runs locally
- **No authentication:** Event selection replaces login
- **Real-time UI:** Streams auto-update, no manual refresh
- **Type safety:** Drift provides compile-time SQL safety
- **Cross-platform:** Single codebase for iOS/macOS/Windows

---

## AI Assistant Tips

1. **Always check current_event_provider** - Most operations require an active event
2. **Use existing patterns** - Follow repository/provider/screen patterns shown above
3. **Database changes require build_runner** - Run after modifying `app_database.dart`
4. **German terminology** - UI strings are in German, keep consistency
5. **Soft delete pattern** - Most entities use `is_active` instead of hard delete
6. **Price calculation is automatic** - Don't manually set `calculated_price`
7. **Streams are reactive** - No manual refresh needed in UI
8. **Check for null safety** - Dart null safety is enforced
9. **Material Design 3** - Use Material 3 widgets (FilledButton, etc.)
10. **Context.mounted checks** - Always check `if (mounted)` or `if (context.mounted)` before async operations

---

**Last Updated:** Sprint 4 Complete (All features implemented)
**Total Lines of Code:** ~8,000+ Dart
**Total Files:** 60+ files
**Database Tables:** 10 tables
**Screens:** 30+ screens and forms
