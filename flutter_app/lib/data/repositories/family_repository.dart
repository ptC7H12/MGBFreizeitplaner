import 'package:drift/drift.dart';
import '../database/app_database.dart';

/// Repository für Familien-CRUD-Operationen
class FamilyRepository {
  final AppDatabase _db;

  FamilyRepository(this._db);

  // READ
  Stream<List<Family>> watchFamiliesByEvent(int eventId) {
    return (_db.select(_db.families)
          ..where((tbl) => tbl.eventId.equals(eventId))
          ..orderBy([(tbl) => OrderingTerm.asc(tbl.familyName)]))
        .watch();
  }

  Future<Family?> getFamilyById(int id) {
    return (_db.select(_db.families)..where((tbl) => tbl.id.equals(id)))
        .getSingleOrNull();
  }

  Future<int> getFamilyCount(int eventId) async {
    final query = _db.selectOnly(_db.families)
      ..addColumns([_db.families.id.count()])
      ..where(_db.families.eventId.equals(eventId));

    final result = await query.getSingle();
    return result.read(_db.families.id.count()) ?? 0;
  }

  // CREATE
  Future<int> createFamily({
    required int eventId,
    required String familyName,
    String? contactPerson,
    String? phone,
    String? email,
    String? street,
    String? postalCode,
    String? city,
  }) {
    return _db.into(_db.families).insert(
          FamiliesCompanion.insert(
            eventId: eventId,
            familyName: familyName,
            contactPerson: Value(contactPerson),
            phone: Value(phone),
            email: Value(email),
            street: Value(street),
            postalCode: Value(postalCode),
            city: Value(city),
          ),
        );
  }

  // UPDATE
  Future<bool> updateFamily({
    required int id,
    String? familyName,
    String? contactPerson,
    String? phone,
    String? email,
    String? street,
    String? postalCode,
    String? city,
  }) {
    return _db.update(_db.families).replace(
          FamiliesCompanion(
            id: Value(id),
            familyName:
                familyName != null ? Value(familyName) : const Value.absent(),
            contactPerson:
                contactPerson != null ? Value(contactPerson) : const Value.absent(),
            phone: phone != null ? Value(phone) : const Value.absent(),
            email: email != null ? Value(email) : const Value.absent(),
            street: street != null ? Value(street) : const Value.absent(),
            postalCode:
                postalCode != null ? Value(postalCode) : const Value.absent(),
            city: city != null ? Value(city) : const Value.absent(),
            updatedAt: Value(DateTime.now()),
          ),
        );
  }

  // DELETE
  Future<int> deleteFamily(int id) {
    return (_db.delete(_db.families)..where((tbl) => tbl.id.equals(id))).go();
  }

  // Get members of family
  Future<List<Participant>> getFamilyMembers(int familyId) {
    return (_db.select(_db.participants)
          ..where((tbl) => tbl.familyId.equals(familyId))
          ..where((tbl) => tbl.isActive.equals(true)))
        .get();
  }

  // Calculate total family price
  Future<double> getFamilyTotalPrice(int familyId) async {
    final members = await getFamilyMembers(familyId);
    return members.fold<double>(
      0.0,
      (sum, p) => sum + (p.manualPriceOverride ?? p.calculatedPrice),
    );
  }
}
