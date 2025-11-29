import 'package:drift/drift.dart';
import '../database/app_database.dart';
import '../../services/ruleset_parser_service.dart';

class RulesetRepository {
  final AppDatabase _database;

  RulesetRepository(this._database);

  /// Get all rulesets for a specific event
  Stream<List<Ruleset>> watchRulesetsByEvent(int eventId) {
    return (_database.select(_database.rulesets)
          ..where((t) => t.eventId.equals(eventId) & t.isActive.equals(true))
          ..orderBy([
            (t) => OrderingTerm(expression: t.validFrom, mode: OrderingMode.desc),
          ]))
        .watch();
  }

  /// Get a single ruleset by ID
  Future<Ruleset?> getRulesetById(int id) async {
    return await (_database.select(_database.rulesets)
          ..where((t) => t.id.equals(id) & t.isActive.equals(true)))
        .getSingleOrNull();
  }

  /// Get all rulesets for an event (one-time fetch)
  Future<List<Ruleset>> getRulesetsByEvent(int eventId) async {
    return await (_database.select(_database.rulesets)
          ..where((t) => t.eventId.equals(eventId) & t.isActive.equals(true))
          ..orderBy([
            (t) => OrderingTerm(expression: t.validFrom, mode: OrderingMode.desc),
          ]))
        .get();
  }

  /// Get the active ruleset for a given date
  Future<Ruleset?> getActiveRuleset(int eventId, DateTime date) async {
    final rulesets = await (_database.select(_database.rulesets)
          ..where((t) =>
              t.eventId.equals(eventId) &
              t.isActive.equals(true) &
              t.validFrom.isSmallerOrEqualValue(date))
          ..orderBy([
            (t) => OrderingTerm(expression: t.validFrom, mode: OrderingMode.desc),
          ])
          ..limit(1))
        .get();

    return rulesets.isEmpty ? null : rulesets.first;
  }

  /// Get the current active ruleset for an event
  Future<Ruleset?> getCurrentRuleset(int eventId) async {
    return getActiveRuleset(eventId, DateTime.now());
  }

  /// Create a new ruleset
  Future<int> createRuleset({
    required int eventId,
    required String name,
    required String yamlContent,
    required DateTime validFrom,
    String? description,
  }) async {
    // Validate YAML content
    try {
      RulesetParserService.parseRuleset(yamlContent);
    } catch (e) {
      throw Exception('Ungültiger YAML-Inhalt: $e');
    }

    final companion = RulesetsCompanion(
      eventId: Value(eventId),
      name: Value(name),
      yamlContent: Value(yamlContent),
      validFrom: Value(validFrom),
      description: Value(description),
      isActive: const Value(true),
      createdAt: Value(DateTime.now()),
      updatedAt: Value(DateTime.now()),
    );

    return await _database.into(_database.rulesets).insert(companion);
  }

  /// Update an existing ruleset
  Future<bool> updateRuleset({
    required int id,
    String? name,
    String? yamlContent,
    DateTime? validFrom,
    String? description,
  }) async {
    final existing = await getRulesetById(id);
    if (existing == null) return false;

    // If YAML content is being updated, validate it
    if (yamlContent != null) {
      try {
        RulesetParserService.parseRuleset(yamlContent);
      } catch (e) {
        throw Exception('Ungültiger YAML-Inhalt: $e');
      }
    }

    final companion = RulesetsCompanion(
      id: Value(id),
      name: name != null ? Value(name) : const Value.absent(),
      yamlContent: yamlContent != null ? Value(yamlContent) : const Value.absent(),
      validFrom: validFrom != null ? Value(validFrom) : const Value.absent(),
      description: description != null ? Value(description) : const Value.absent(),
      updatedAt: Value(DateTime.now()),
    );

    return await _database.update(_database.rulesets).replace(companion);
  }

  /// Soft delete a ruleset
  Future<bool> deleteRuleset(int id) async {
    final existing = await getRulesetById(id);
    if (existing == null) return false;

    return await (_database.update(_database.rulesets)
          ..where((t) => t.id.equals(id)))
        .write(
      RulesetsCompanion(
        isActive: const Value(false),
        updatedAt: Value(DateTime.now()),
      ),
    ) >
        0;
  }

  /// Permanently delete a ruleset (hard delete)
  Future<bool> permanentlyDeleteRuleset(int id) async {
    return await (_database.delete(_database.rulesets)
          ..where((t) => t.id.equals(id)))
        .go() >
        0;
  }

  /// Parse and validate a ruleset's YAML content
  Map<String, dynamic> parseRulesetYaml(String yamlContent) {
    return RulesetParserService.parseRuleset(yamlContent);
  }

  /// Get a ruleset with parsed data
  Future<Map<String, dynamic>?> getRulesetWithParsedData(int id) async {
    final ruleset = await getRulesetById(id);
    if (ruleset == null) return null;

    try {
      final parsedData = RulesetParserService.parseRuleset(ruleset.yamlContent);
      return {
        'ruleset': ruleset,
        'parsed': parsedData,
      };
    } catch (e) {
      return {
        'ruleset': ruleset,
        'error': e.toString(),
      };
    }
  }

  /// Clone a ruleset with a new valid_from date
  Future<int> cloneRuleset({
    required int sourceId,
    required DateTime newValidFrom,
    String? newName,
  }) async {
    final source = await getRulesetById(sourceId);
    if (source == null) throw Exception('Quell-Regelwerk nicht gefunden');

    final name = newName ?? '${source.name} (Kopie)';

    return createRuleset(
      eventId: source.eventId,
      name: name,
      yamlContent: source.yamlContent,
      validFrom: newValidFrom,
      description: source.description,
    );
  }

  /// Get ruleset statistics
  Future<Map<String, dynamic>> getRulesetStatistics(int rulesetId) async {
    final ruleset = await getRulesetById(rulesetId);
    if (ruleset == null) {
      return {
        'error': 'Regelwerk nicht gefunden',
      };
    }

    try {
      final parsed = RulesetParserService.parseRuleset(ruleset.yamlContent);

      return {
        'name': ruleset.name,
        'validFrom': ruleset.validFrom,
        'ageGroupCount': (parsed['age_groups'] as List).length,
        'roleDiscountCount': (parsed['role_discounts'] as List).length,
        'hasFamilyDiscount': parsed['family_discount'] != null,
        'parsed': parsed,
      };
    } catch (e) {
      return {
        'error': 'Fehler beim Parsen: $e',
      };
    }
  }

  /// Create a default ruleset template
  String getDefaultRulesetTemplate() {
    return '''name: "Neues Regelwerk"
valid_from: ${DateTime.now().toIso8601String().split('T')[0]}

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
    - children_count: 4
      discount_percent: 20.0
''';
  }
}
