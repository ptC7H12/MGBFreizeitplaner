import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../services/price_calculator_service.dart';
import '../../providers/database_provider.dart';
import '../../providers/current_event_provider.dart';
import '../../data/database/app_database.dart';
import '../../utils/date_utils.dart';

/// Live-Preisberechnung Widget
///
/// Entspricht der HTMX-basierten Live-Berechnung in der Web-App
/// Berechnet den Preis reaktiv basierend auf Eingaben
class PricePreviewWidget extends ConsumerStatefulWidget {
  final DateTime? birthDate;
  final int? roleId;
  final int? familyId;
  final double? manualPriceOverride;
  final double discountPercent;
  final String? discountReason;

  const PricePreviewWidget({
    super.key,
    this.birthDate,
    this.roleId,
    this.familyId,
    this.manualPriceOverride,
    this.discountPercent = 0.0,
    this.discountReason,
  });

  @override
  ConsumerState<PricePreviewWidget> createState() => _PricePreviewWidgetState();
}

class _PricePreviewWidgetState extends ConsumerState<PricePreviewWidget> {
  Map<String, dynamic>? _priceBreakdown;
  bool _isCalculating = false;
  String? _error;

  @override
  void didUpdateWidget(PricePreviewWidget oldWidget) {
    super.didUpdateWidget(oldWidget);

    // Neu berechnen wenn sich relevante Parameter ändern
    if (oldWidget.birthDate != widget.birthDate ||
        oldWidget.roleId != widget.roleId ||
        oldWidget.familyId != widget.familyId ||
        oldWidget.manualPriceOverride != widget.manualPriceOverride ||
        oldWidget.discountPercent != widget.discountPercent) {
      _calculatePrice();
    }
  }

  @override
  void initState() {
    super.initState();
    _calculatePrice();
  }

  Future<void> _calculatePrice() async {
    if (widget.birthDate == null) {
      setState(() {
        _priceBreakdown = null;
        _error = 'Bitte Geburtsdatum auswählen';
      });
      return;
    }

    setState(() {
      _isCalculating = true;
      _error = null;
    });

    try {
      final database = ref.read(databaseProvider);
      final eventId = ref.read(currentEventIdProvider);

      if (eventId == null) {
        throw Exception('Kein Event ausgewählt');
      }

      // Event laden
      final event = await (database.select(database.events)
            ..where((tbl) => tbl.id.equals(eventId)))
          .getSingleOrNull();

      if (event == null) {
        throw Exception('Event nicht gefunden');
      }

      // Aktives Regelwerk laden
      final ruleset = await (database.select(database.rulesets)
            ..where((tbl) => tbl.eventId.equals(eventId))
            ..where((tbl) => tbl.isActive.equals(true))
            ..where((tbl) => tbl.validFrom.isSmallerOrEqualValue(event.startDate))
            ..where((tbl) => tbl.validUntil.isBiggerOrEqualValue(event.startDate)))
          .getSingleOrNull();

      if (ruleset == null) {
        setState(() {
          _error = 'Kein aktives Regelwerk für dieses Event';
          _isCalculating = false;
        });
        return;
      }

      // Alter zum Event-Start berechnen
      final age = AppDateUtils.calculateAgeAtEventStart(
        widget.birthDate!,
        event.startDate,
      );

      // Rolle laden
      String? roleName;
      String roleDisplayName = 'Keine Rolle';
      if (widget.roleId != null) {
        final role = await (database.select(database.roles)
              ..where((tbl) => tbl.id.equals(widget.roleId!)))
            .getSingleOrNull();
        if (role != null) {
          roleName = role.name.toLowerCase();
          roleDisplayName = role.displayName;
        }
      }

      // Position in Familie ermitteln
      int familyChildrenCount = 1;
      if (widget.familyId != null) {
        final siblings = await (database.select(database.participants)
              ..where((tbl) => tbl.familyId.equals(widget.familyId!))
              ..where((tbl) => tbl.isActive.equals(true))
              ..orderBy([(tbl) => OrderingTerm.asc(tbl.birthDate)]))
            .get();

        // TODO: Korrekte Position basierend auf Geburtsdatum berechnen
        familyChildrenCount = siblings.length + 1;
      }

      // Regelwerk-Daten parsen (vereinfacht, da JSON-Parsing noch fehlt)
      final rulesetData = {
        'age_groups': _parseAgeGroups(ruleset.ageGroups),
        'role_discounts': _parseRoleDiscounts(ruleset.roleDiscounts),
        'family_discount': _parseFamilyDiscount(ruleset.familyDiscount),
      };

      // Preis mit Breakdown berechnen
      final breakdown = PriceCalculatorService.calculateParticipantPriceWithBreakdown(
        age: age,
        roleName: roleName ?? '',
        roleDisplayName: roleDisplayName,
        rulesetData: rulesetData,
        familyChildrenCount: familyChildrenCount,
        discountPercent: widget.discountPercent,
        discountReason: widget.discountReason,
        manualPriceOverride: widget.manualPriceOverride,
      );

      setState(() {
        _priceBreakdown = breakdown;
        _isCalculating = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Fehler bei Preisberechnung: $e';
        _isCalculating = false;
      });
    }
  }

  // Vereinfachtes JSON-Parsing (TODO: Proper JSON parsing)
  List<dynamic> _parseAgeGroups(String jsonString) {
    // Dummy-Daten für Demo
    return [
      {'min_age': 0, 'max_age': 5, 'base_price': 50.0},
      {'min_age': 6, 'max_age': 12, 'base_price': 100.0},
      {'min_age': 13, 'max_age': 17, 'base_price': 150.0},
      {'min_age': 18, 'max_age': 999, 'base_price': 200.0},
    ];
  }

  Map<String, dynamic> _parseRoleDiscounts(String jsonString) {
    // Dummy-Daten für Demo
    return {
      'betreuer': {'discount_percent': 100.0},
      'küchenteam': {'discount_percent': 50.0},
    };
  }

  Map<String, dynamic> _parseFamilyDiscount(String jsonString) {
    // Dummy-Daten für Demo
    return {
      'enabled': true,
      'first_child_percent': 0.0,
      'second_child_percent': 25.0,
      'third_plus_child_percent': 50.0,
    };
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return Card(
        color: Colors.red.shade50,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(Icons.error_outline, color: Colors.red.shade700),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  _error!,
                  style: TextStyle(color: Colors.red.shade700),
                ),
              ),
            ],
          ),
        ),
      );
    }

    if (_isCalculating) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Row(
            children: [
              SizedBox(
                height: 20,
                width: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
              SizedBox(width: 12),
              Text('Berechne Preis...'),
            ],
          ),
        ),
      );
    }

    if (_priceBreakdown == null) {
      return Card(
        color: Colors.grey.shade100,
        child: const Padding(
          padding: EdgeInsets.all(16),
          child: Text('Geburtsdatum eingeben für Preisberechnung'),
        ),
      );
    }

    final breakdown = _priceBreakdown!;
    final finalPrice = breakdown['final_price'] as double;
    final hasDiscounts = breakdown['has_discounts'] as bool;
    final discountReasons = breakdown['discount_reasons'] as List;

    return Card(
      color: Colors.blue.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Berechneter Preis',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                Text(
                  '${finalPrice.toStringAsFixed(2)} €',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade700,
                  ),
                ),
              ],
            ),
            if (hasDiscounts) ...[
              const SizedBox(height: 12),
              const Divider(),
              const SizedBox(height: 8),
              const Text(
                'Rabatte:',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 4),
              ...discountReasons.map((reason) => Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Row(
                      children: [
                        Icon(Icons.check_circle, size: 16, color: Colors.green.shade700),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            reason as String,
                            style: TextStyle(color: Colors.grey.shade700),
                          ),
                        ),
                      ],
                    ),
                  )),
              const SizedBox(height: 8),
              const Divider(),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Basispreis:',
                    style: TextStyle(color: Colors.grey.shade700),
                  ),
                  Text(
                    '${(breakdown['base_price'] as double).toStringAsFixed(2)} €',
                    style: TextStyle(
                      color: Colors.grey.shade700,
                      decoration: TextDecoration.lineThrough,
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}
