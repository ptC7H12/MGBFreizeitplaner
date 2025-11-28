import 'package:yaml/yaml.dart';
import 'dart:developer' as developer;

/// YAML-Regelwerk-Parser Service
///
/// Portiert von Python (app/services/ruleset_parser.py)
/// Parst und validiert YAML-Regelwerke für Preisberechnungen
class RulesetParserService {
  /// Parst YAML-Regelwerk und konvertiert zu Map
  ///
  /// Args:
  ///   - yamlContent: YAML-String
  ///
  /// Returns:
  ///   Map mit geparsten Regelwerk-Daten
  ///
  /// Throws:
  ///   - FormatException wenn YAML ungültig ist
  static Map<String, dynamic> parseRuleset(String yamlContent) {
    try {
      final doc = loadYaml(yamlContent);

      if (doc is! YamlMap) {
        throw const FormatException('YAML muss ein Dictionary sein');
      }

      return {
        'name': doc['name'] as String? ?? 'Unnamed Ruleset',
        'valid_from': _parseDate(doc['valid_from']),
        'valid_until': _parseDate(doc['valid_until']),
        'age_groups': _parseAgeGroups(doc['age_groups']),
        'role_discounts': _parseRoleDiscounts(doc['role_discounts']),
        'family_discount': _parseFamilyDiscount(doc['family_discount']),
      };
    } catch (e) {
      developer.log(
        'Fehler beim Parsen des YAML: $e',
        name: 'RulesetParserService',
        level: 1000, // Error level
      );
      rethrow;
    }
  }

  /// Validiert YAML-Regelwerk und gibt Liste von Fehlern zurück
  ///
  /// Args:
  ///   - yamlContent: YAML-String
  ///
  /// Returns:
  ///   Liste von Fehlermeldungen (leer wenn valide)
  static List<String> validateRuleset(String yamlContent) {
    final errors = <String>[];

    try {
      final data = parseRuleset(yamlContent);

      // Pflichtfelder prüfen
      if (data['name'] == null || (data['name'] as String).isEmpty) {
        errors.add('Feld "name" ist erforderlich');
      }

      if (data['valid_from'] == null) {
        errors.add('Feld "valid_from" ist erforderlich (Format: YYYY-MM-DD)');
      }

      if (data['valid_until'] == null) {
        errors.add('Feld "valid_until" ist erforderlich (Format: YYYY-MM-DD)');
      }

      // Datumsbereich prüfen
      if (data['valid_from'] != null && data['valid_until'] != null) {
        final from = data['valid_from'] as DateTime;
        final until = data['valid_until'] as DateTime;
        if (from.isAfter(until)) {
          errors.add(
            'valid_from (${from.toIso8601String()}) muss vor valid_until (${until.toIso8601String()}) liegen',
          );
        }
      }

      // Age Groups validieren
      final ageGroups = data['age_groups'] as List?;
      if (ageGroups == null || ageGroups.isEmpty) {
        errors.add('Mindestens eine age_group ist erforderlich');
      } else {
        errors.addAll(_validateAgeGroups(ageGroups));
      }

      // Role Discounts validieren (optional)
      final roleDiscounts = data['role_discounts'] as Map<String, dynamic>?;
      if (roleDiscounts != null && roleDiscounts.isNotEmpty) {
        errors.addAll(_validateRoleDiscounts(roleDiscounts));
      }

      // Family Discount validieren (optional)
      final familyDiscount = data['family_discount'] as Map<String, dynamic>?;
      if (familyDiscount != null && familyDiscount.isNotEmpty) {
        errors.addAll(_validateFamilyDiscount(familyDiscount));
      }
    } catch (e) {
      errors.add('YAML-Parsing-Fehler: $e');
    }

    return errors;
  }

  // ============================================================================
  // PRIVATE HELPER METHODS
  // ============================================================================

  static DateTime? _parseDate(dynamic value) {
    if (value == null) return null;

    try {
      if (value is DateTime) {
        return value;
      }
      return DateTime.parse(value.toString());
    } catch (e) {
      throw FormatException('Ungültiges Datum: $value');
    }
  }

  static List<Map<String, dynamic>> _parseAgeGroups(dynamic ageGroups) {
    if (ageGroups is! YamlList) {
      throw const FormatException('age_groups muss eine Liste sein');
    }

    final result = <Map<String, dynamic>>[];

    for (var group in ageGroups) {
      if (group is! YamlMap) {
        throw FormatException('Jede age_group muss ein Dictionary sein: $group');
      }

      result.add({
        'min_age': group['min_age'] as int? ?? 0,
        'max_age': group['max_age'] as int? ?? 999,
        'base_price': (group['base_price'] as num?)?.toDouble() ??
            (group['price'] as num?)?.toDouble() ??
            0.0,
        'description': group['description'] as String?,
      });
    }

    return result;
  }

  static Map<String, dynamic> _parseRoleDiscounts(dynamic roleDiscounts) {
    if (roleDiscounts == null) return {};
    if (roleDiscounts is! YamlMap) {
      throw const FormatException('role_discounts muss ein Dictionary sein');
    }

    final result = <String, dynamic>{};

    for (var entry in roleDiscounts.entries) {
      final key = entry.key.toString();
      final value = entry.value;

      if (value is! YamlMap) {
        throw FormatException(
          'Rollenrabatt für "$key" muss ein Dictionary sein',
        );
      }

      result[key] = {
        'discount_percent': (value['discount_percent'] as num?)?.toDouble() ?? 0.0,
        'max_count': value['max_count'] as int?,
        'description': value['description'] as String?,
      };
    }

    return result;
  }

  static Map<String, dynamic> _parseFamilyDiscount(dynamic familyDiscount) {
    if (familyDiscount == null) return {'enabled': false};
    if (familyDiscount is! YamlMap) {
      throw const FormatException('family_discount muss ein Dictionary sein');
    }

    return {
      'enabled': familyDiscount['enabled'] as bool? ?? false,
      'first_child_percent':
          (familyDiscount['first_child_percent'] as num?)?.toDouble() ?? 0.0,
      'second_child_percent':
          (familyDiscount['second_child_percent'] as num?)?.toDouble() ?? 0.0,
      'third_plus_child_percent':
          (familyDiscount['third_plus_child_percent'] as num?)?.toDouble() ??
              0.0,
    };
  }

  static List<String> _validateAgeGroups(List ageGroups) {
    final errors = <String>[];

    for (var i = 0; i < ageGroups.length; i++) {
      final group = ageGroups[i];

      // Prüfe ob base_price vorhanden und > 0
      final basePrice = group['base_price'] as double?;
      if (basePrice == null || basePrice < 0) {
        errors.add(
          'age_group[$i]: base_price muss >= 0 sein (aktuell: $basePrice)',
        );
      }

      // Prüfe min_age <= max_age
      final minAge = group['min_age'] as int?;
      final maxAge = group['max_age'] as int?;
      if (minAge != null && maxAge != null && minAge > maxAge) {
        errors.add(
          'age_group[$i]: min_age ($minAge) muss <= max_age ($maxAge) sein',
        );
      }
    }

    // Prüfe auf Überschneidungen
    for (var i = 0; i < ageGroups.length; i++) {
      for (var j = i + 1; j < ageGroups.length; j++) {
        final group1 = ageGroups[i];
        final group2 = ageGroups[j];

        final min1 = group1['min_age'] as int? ?? 0;
        final max1 = group1['max_age'] as int? ?? 999;
        final min2 = group2['min_age'] as int? ?? 0;
        final max2 = group2['max_age'] as int? ?? 999;

        // Prüfe auf Überschneidung
        if ((min1 <= max2 && max1 >= min2)) {
          errors.add(
            'age_group[$i] ($min1-$max1) überschneidet sich mit age_group[$j] ($min2-$max2)',
          );
        }
      }
    }

    return errors;
  }

  static List<String> _validateRoleDiscounts(Map<String, dynamic> roleDiscounts) {
    final errors = <String>[];

    for (var entry in roleDiscounts.entries) {
      final key = entry.key;
      final value = entry.value as Map<String, dynamic>;

      final discountPercent = value['discount_percent'] as double?;
      if (discountPercent == null || discountPercent < 0 || discountPercent > 100) {
        errors.add(
          'role_discount["$key"]: discount_percent muss zwischen 0 und 100 liegen (aktuell: $discountPercent)',
        );
      }

      final maxCount = value['max_count'] as int?;
      if (maxCount != null && maxCount < 0) {
        errors.add(
          'role_discount["$key"]: max_count muss >= 0 sein (aktuell: $maxCount)',
        );
      }
    }

    return errors;
  }

  static List<String> _validateFamilyDiscount(
    Map<String, dynamic> familyDiscount,
  ) {
    final errors = <String>[];

    final enabled = familyDiscount['enabled'] as bool? ?? false;
    if (!enabled) {
      return errors; // Wenn disabled, keine weitere Validierung
    }

    final firstChildPercent = familyDiscount['first_child_percent'] as double?;
    final secondChildPercent = familyDiscount['second_child_percent'] as double?;
    final thirdPlusChildPercent =
        familyDiscount['third_plus_child_percent'] as double?;

    if (firstChildPercent != null &&
        (firstChildPercent < 0 || firstChildPercent > 100)) {
      errors.add(
        'family_discount: first_child_percent muss zwischen 0 und 100 liegen (aktuell: $firstChildPercent)',
      );
    }

    if (secondChildPercent != null &&
        (secondChildPercent < 0 || secondChildPercent > 100)) {
      errors.add(
        'family_discount: second_child_percent muss zwischen 0 und 100 liegen (aktuell: $secondChildPercent)',
      );
    }

    if (thirdPlusChildPercent != null &&
        (thirdPlusChildPercent < 0 || thirdPlusChildPercent > 100)) {
      errors.add(
        'family_discount: third_plus_child_percent muss zwischen 0 und 100 liegen (aktuell: $thirdPlusChildPercent)',
      );
    }

    return errors;
  }

  /// Konvertiert Map zurück zu YAML-String
  ///
  /// Args:
  ///   - data: Regelwerk-Daten als Map
  ///
  /// Returns:
  ///   YAML-String
  static String toYaml(Map<String, dynamic> data) {
    final buffer = StringBuffer();

    buffer.writeln('name: ${data['name']}');
    buffer.writeln('valid_from: ${(data['valid_from'] as DateTime).toIso8601String().split('T')[0]}');
    buffer.writeln('valid_until: ${(data['valid_until'] as DateTime).toIso8601String().split('T')[0]}');
    buffer.writeln();

    buffer.writeln('age_groups:');
    for (var group in data['age_groups'] as List) {
      buffer.writeln('  - min_age: ${group['min_age']}');
      buffer.writeln('    max_age: ${group['max_age']}');
      buffer.writeln('    base_price: ${group['base_price']}');
      if (group['description'] != null) {
        buffer.writeln('    description: "${group['description']}"');
      }
    }

    buffer.writeln();
    buffer.writeln('role_discounts:');
    final roleDiscounts = data['role_discounts'] as Map<String, dynamic>;
    for (var entry in roleDiscounts.entries) {
      buffer.writeln('  ${entry.key}:');
      final value = entry.value as Map<String, dynamic>;
      buffer.writeln('    discount_percent: ${value['discount_percent']}');
      if (value['max_count'] != null) {
        buffer.writeln('    max_count: ${value['max_count']}');
      }
      if (value['description'] != null) {
        buffer.writeln('    description: "${value['description']}"');
      }
    }

    buffer.writeln();
    final familyDiscount = data['family_discount'] as Map<String, dynamic>;
    buffer.writeln('family_discount:');
    buffer.writeln('  enabled: ${familyDiscount['enabled']}');
    buffer.writeln('  first_child_percent: ${familyDiscount['first_child_percent']}');
    buffer.writeln('  second_child_percent: ${familyDiscount['second_child_percent']}');
    buffer.writeln('  third_plus_child_percent: ${familyDiscount['third_plus_child_percent']}');

    return buffer.toString();
  }
}
