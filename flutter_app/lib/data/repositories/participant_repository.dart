import 'package:drift/drift.dart';
import '../database/app_database.dart';
import '../../services/price_calculator_service.dart';
import '../../utils/date_utils.dart';

/// Repository für Teilnehmer-CRUD-Operationen
///
/// Kapselt alle Datenbank-Zugriffe für Participants
class ParticipantRepository {
  final AppDatabase _db;

  ParticipantRepository(this._db);

  // ============================================================================
  // READ OPERATIONS
  // ============================================================================

  /// Alle aktiven Teilnehmer eines Events
  Stream<List<Participant>> watchParticipantsByEvent(int eventId) {
    return (_db.select(_db.participants)
          ..where((tbl) => tbl.eventId.equals(eventId))
          ..where((tbl) => tbl.isActive.equals(true))
          ..orderBy([(tbl) => OrderingTerm.asc(tbl.lastName)]))
        .watch();
  }

  /// Einzelner Teilnehmer nach ID
  Future<Participant?> getParticipantById(int id) {
    return (_db.select(_db.participants)..where((tbl) => tbl.id.equals(id)))
        .getSingleOrNull();
  }

  /// Stream für einzelnen Teilnehmer (reaktiv)
  Stream<Participant?> watchParticipantById(int id) {
    return (_db.select(_db.participants)..where((tbl) => tbl.id.equals(id)))
        .watchSingleOrNull();
  }

  /// Alle Teilnehmer einer Familie
  Future<List<Participant>> getParticipantsByFamily(int familyId) {
    return (_db.select(_db.participants)
          ..where((tbl) => tbl.familyId.equals(familyId))
          ..where((tbl) => tbl.isActive.equals(true))
          ..orderBy([(tbl) => OrderingTerm.asc(tbl.birthDate)]))
        .get();
  }

  /// Anzahl aktiver Teilnehmer eines Events
  Future<int> getParticipantCount(int eventId) async {
    final query = _db.selectOnly(_db.participants)
      ..addColumns([_db.participants.id.count()])
      ..where(_db.participants.eventId.equals(eventId))
      ..where(_db.participants.isActive.equals(true));

    final result = await query.getSingle();
    return result.read(_db.participants.id.count()) ?? 0;
  }

  /// Suche Teilnehmer nach Name
  Stream<List<Participant>> searchParticipants(int eventId, String query) {
    final searchLower = query.toLowerCase();
    return (_db.select(_db.participants)
          ..where((tbl) => tbl.eventId.equals(eventId))
          ..where((tbl) => tbl.isActive.equals(true))
          ..where(
            (tbl) =>
                tbl.firstName.lower().like('%$searchLower%') |
                tbl.lastName.lower().like('%$searchLower%'),
          )
          ..orderBy([(tbl) => OrderingTerm.asc(tbl.lastName)]))
        .watch();
  }

  // ============================================================================
  // CREATE OPERATION
  // ============================================================================

  /// Erstelle neuen Teilnehmer
  ///
  /// Berechnet automatisch den Preis basierend auf Event und Regelwerk
  Future<int> createParticipant({
    required int eventId,
    required String firstName,
    required String lastName,
    required DateTime birthDate,
    String? gender,
    String? street,
    String? postalCode,
    String? city,
    String? phone,
    String? email,
    String? emergencyContact,
    String? emergencyPhone,
    String? medicalNotes,
    String? allergies,
    String? dietaryRestrictions,
    bool bildungUndTeilhabe = false,
    int? roleId,
    int? familyId,
    double? manualPriceOverride,
    double discountPercent = 0.0,
    String? discountReason,
  }) async {
    // Preis berechnen
    final calculatedPrice = await _calculatePrice(
      eventId: eventId,
      birthDate: birthDate,
      roleId: roleId,
      familyId: familyId,
    );

    final companion = ParticipantsCompanion.insert(
      eventId: eventId,
      firstName: firstName,
      lastName: lastName,
      birthDate: birthDate,
      gender: Value(gender),
      street: Value(street),
      postalCode: Value(postalCode),
      city: Value(city),
      phone: Value(phone),
      email: Value(email),
      emergencyContact: Value(emergencyContact),
      emergencyPhone: Value(emergencyPhone),
      medicalNotes: Value(medicalNotes),
      allergies: Value(allergies),
      dietaryRestrictions: Value(dietaryRestrictions),
      bildungUndTeilhabe: Value(bildungUndTeilhabe),
      calculatedPrice: Value(calculatedPrice),
      manualPriceOverride: Value(manualPriceOverride),
      discountPercent: Value(discountPercent),
      discountReason: Value(discountReason),
      roleId: Value(roleId),
      familyId: Value(familyId),
    );

    return await _db.into(_db.participants).insert(companion);
  }

  // ============================================================================
  // UPDATE OPERATION
  // ============================================================================

  /// Aktualisiere Teilnehmer
  ///
  /// Berechnet Preis neu wenn sich relevante Felder ändern
  Future<bool> updateParticipant({
    required int id,
    String? firstName,
    String? lastName,
    DateTime? birthDate,
    String? gender,
    String? street,
    String? postalCode,
    String? city,
    String? phone,
    String? email,
    String? emergencyContact,
    String? emergencyPhone,
    String? medicalNotes,
    String? allergies,
    String? dietaryRestrictions,
    bool? bildungUndTeilhabe,
    int? roleId,
    int? familyId,
    double? manualPriceOverride,
    double? discountPercent,
    String? discountReason,
    bool recalculatePrice = true,
  }) async {
    final existing = await getParticipantById(id);
    if (existing == null) return false;

    double? newCalculatedPrice;

    // Preis neu berechnen wenn sich relevante Felder ändern
    if (recalculatePrice &&
        manualPriceOverride == null &&
        (birthDate != null ||
            roleId != null ||
            familyId != null ||
            roleId != existing.roleId ||
            familyId != existing.familyId)) {
      newCalculatedPrice = await _calculatePrice(
        eventId: existing.eventId,
        birthDate: birthDate ?? existing.birthDate,
        roleId: roleId ?? existing.roleId,
        familyId: familyId ?? existing.familyId,
      );
    }

    final companion = ParticipantsCompanion(
      id: Value(id),
      firstName: firstName != null ? Value(firstName) : const Value.absent(),
      lastName: lastName != null ? Value(lastName) : const Value.absent(),
      birthDate: birthDate != null ? Value(birthDate) : const Value.absent(),
      gender: gender != null ? Value(gender) : const Value.absent(),
      street: street != null ? Value(street) : const Value.absent(),
      postalCode: postalCode != null ? Value(postalCode) : const Value.absent(),
      city: city != null ? Value(city) : const Value.absent(),
      phone: phone != null ? Value(phone) : const Value.absent(),
      email: email != null ? Value(email) : const Value.absent(),
      emergencyContact:
          emergencyContact != null ? Value(emergencyContact) : const Value.absent(),
      emergencyPhone:
          emergencyPhone != null ? Value(emergencyPhone) : const Value.absent(),
      medicalNotes:
          medicalNotes != null ? Value(medicalNotes) : const Value.absent(),
      allergies: allergies != null ? Value(allergies) : const Value.absent(),
      dietaryRestrictions: dietaryRestrictions != null
          ? Value(dietaryRestrictions)
          : const Value.absent(),
      bildungUndTeilhabe: bildungUndTeilhabe != null
          ? Value(bildungUndTeilhabe)
          : const Value.absent(),
      roleId: Value(roleId),
      familyId: Value(familyId),
      manualPriceOverride: Value(manualPriceOverride),
      discountPercent:
          discountPercent != null ? Value(discountPercent) : const Value.absent(),
      discountReason:
          discountReason != null ? Value(discountReason) : const Value.absent(),
      calculatedPrice:
          newCalculatedPrice != null ? Value(newCalculatedPrice) : const Value.absent(),
      updatedAt: Value(DateTime.now()),
    );

    return await _db.update(_db.participants).replace(companion);
  }

  // ============================================================================
  // DELETE OPERATION (Soft Delete)
  // ============================================================================

  /// Soft-Delete: Setzt isActive=false und deletedAt
  Future<bool> deleteParticipant(int id) async {
    final companion = ParticipantsCompanion(
      id: Value(id),
      isActive: const Value(false),
      deletedAt: Value(DateTime.now()),
      updatedAt: Value(DateTime.now()),
    );

    return await _db.update(_db.participants).replace(companion);
  }

  /// Hard-Delete: Löscht tatsächlich aus DB (nur für Tests!)
  Future<int> hardDeleteParticipant(int id) {
    return (_db.delete(_db.participants)..where((tbl) => tbl.id.equals(id)))
        .go();
  }

  /// Reaktiviere gelöschten Teilnehmer
  Future<bool> restoreParticipant(int id) async {
    final companion = ParticipantsCompanion(
      id: Value(id),
      isActive: const Value(true),
      deletedAt: const Value(null),
      updatedAt: Value(DateTime.now()),
    );

    return await _db.update(_db.participants).replace(companion);
  }

  // ============================================================================
  // HELPER METHODS
  // ============================================================================

  /// Berechnet Preis für Teilnehmer
  Future<double> _calculatePrice({
    required int eventId,
    required DateTime birthDate,
    int? roleId,
    int? familyId,
  }) async {
    // Event laden
    final event = await (_db.select(_db.events)
          ..where((tbl) => tbl.id.equals(eventId)))
        .getSingleOrNull();

    if (event == null) return 0.0;

    // Aktives Regelwerk für Event finden
    final ruleset = await (_db.select(_db.rulesets)
          ..where((tbl) => tbl.eventId.equals(eventId))
          ..where((tbl) => tbl.isActive.equals(true))
          ..where((tbl) => tbl.validFrom.isSmallerOrEqualValue(event.startDate))
          ..where((tbl) => tbl.validUntil.isBiggerOrEqualValue(event.startDate)))
        .getSingleOrNull();

    if (ruleset == null) return 0.0;

    // Alter zum Event-Start berechnen
    final age = AppDateUtils.calculateAgeAtEventStart(birthDate, event.startDate);

    // Rolle laden (falls vorhanden)
    String? roleName;
    if (roleId != null) {
      final role = await (_db.select(_db.roles)
            ..where((tbl) => tbl.id.equals(roleId)))
          .getSingleOrNull();
      roleName = role?.name.toLowerCase();
    }

    // Position in Familie ermitteln
    int familyChildrenCount = 1;
    if (familyId != null) {
      final siblings = await (_db.select(_db.participants)
            ..where((tbl) => tbl.familyId.equals(familyId))
            ..where((tbl) => tbl.isActive.equals(true))
            ..orderBy([(tbl) => OrderingTerm.asc(tbl.birthDate)]))
          .get();

      familyChildrenCount = siblings.length + 1;
    }

    // Preis berechnen mit PriceCalculatorService
    final rulesetData = {
      'age_groups': _parseJsonField(ruleset.ageGroups),
      'role_discounts': _parseJsonField(ruleset.roleDiscounts),
      'family_discount': _parseJsonField(ruleset.familyDiscount),
    };

    return PriceCalculatorService.calculateParticipantPrice(
      age: age,
      roleName: roleName,
      rulesetData: rulesetData,
      familyChildrenCount: familyChildrenCount,
    );
  }

  /// Parse JSON-String zu Map/List (Drift speichert JSON als TEXT)
  dynamic _parseJsonField(String jsonString) {
    try {
      // TODO: Implement JSON parsing
      // Für jetzt: Return leere Struktur
      return {};
    } catch (e) {
      return {};
    }
  }

  /// Gibt den finalen Anzeigepreis zurück (manualPriceOverride oder calculatedPrice)
  double getDisplayPrice(Participant participant) {
    return participant.manualPriceOverride ?? participant.calculatedPrice;
  }

  /// Berechnet Gesamtsumme aller Teilnehmerpreise eines Events
  Future<double> getTotalRevenue(int eventId) async {
    final participants = await (_db.select(_db.participants)
          ..where((tbl) => tbl.eventId.equals(eventId))
          ..where((tbl) => tbl.isActive.equals(true)))
        .get();

    return participants.fold<double>(
      0.0,
      (sum, p) => sum + getDisplayPrice(p),
    );
  }
}
