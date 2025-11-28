import 'package:drift/drift.dart';
import '../database/app_database.dart';

/// Repository für Zahlungen-CRUD-Operationen
class PaymentRepository {
  final AppDatabase _db;

  PaymentRepository(this._db);

  // READ
  Stream<List<Payment>> watchPaymentsByEvent(int eventId) {
    return (_db.select(_db.payments)
          ..where((tbl) => tbl.eventId.equals(eventId))
          ..orderBy([(tbl) => OrderingTerm.desc(tbl.paymentDate)]))
        .watch();
  }

  Stream<List<Payment>> watchPaymentsByParticipant(int participantId) {
    return (_db.select(_db.payments)
          ..where((tbl) => tbl.participantId.equals(participantId))
          ..orderBy([(tbl) => OrderingTerm.desc(tbl.paymentDate)]))
        .watch();
  }

  Stream<List<Payment>> watchPaymentsByFamily(int familyId) {
    return (_db.select(_db.payments)
          ..where((tbl) => tbl.familyId.equals(familyId))
          ..orderBy([(tbl) => OrderingTerm.desc(tbl.paymentDate)]))
        .watch();
  }

  Future<Payment?> getPaymentById(int id) {
    return (_db.select(_db.payments)..where((tbl) => tbl.id.equals(id)))
        .getSingleOrNull();
  }

  // CREATE
  Future<int> createPayment({
    required int eventId,
    int? participantId,
    int? familyId,
    required double amount,
    required DateTime paymentDate,
    String? paymentMethod,
    String? notes,
  }) {
    return _db.into(_db.payments).insert(
          PaymentsCompanion.insert(
            eventId: eventId,
            participantId: Value(participantId),
            familyId: Value(familyId),
            amount: amount,
            paymentDate: paymentDate,
            paymentMethod: Value(paymentMethod),
            notes: Value(notes),
          ),
        );
  }

  // UPDATE
  Future<bool> updatePayment({
    required int id,
    double? amount,
    DateTime? paymentDate,
    String? paymentMethod,
    String? notes,
  }) {
    return _db.update(_db.payments).replace(
          PaymentsCompanion(
            id: Value(id),
            amount: amount != null ? Value(amount) : const Value.absent(),
            paymentDate:
                paymentDate != null ? Value(paymentDate) : const Value.absent(),
            paymentMethod:
                paymentMethod != null ? Value(paymentMethod) : const Value.absent(),
            notes: notes != null ? Value(notes) : const Value.absent(),
            updatedAt: Value(DateTime.now()),
          ),
        );
  }

  // DELETE
  Future<int> deletePayment(int id) {
    return (_db.delete(_db.payments)..where((tbl) => tbl.id.equals(id))).go();
  }

  // CALCULATIONS
  Future<double> getTotalPayments(int eventId) async {
    final payments = await (_db.select(_db.payments)
          ..where((tbl) => tbl.eventId.equals(eventId)))
        .get();

    return payments.fold<double>(0.0, (sum, p) => sum + p.amount);
  }

  Future<double> getTotalPaymentsForParticipant(int participantId) async {
    final payments = await (_db.select(_db.payments)
          ..where((tbl) => tbl.participantId.equals(participantId)))
        .get();

    return payments.fold<double>(0.0, (sum, p) => sum + p.amount);
  }

  Future<double> getTotalPaymentsForFamily(int familyId) async {
    final payments = await (_db.select(_db.payments)
          ..where((tbl) => tbl.familyId.equals(familyId)))
        .get();

    return payments.fold<double>(0.0, (sum, p) => sum + p.amount);
  }

  // Get outstanding amount for participant
  Future<double> getOutstandingAmount(int participantId) async {
    final participant = await (_db.select(_db.participants)
          ..where((tbl) => tbl.id.equals(participantId)))
        .getSingleOrNull();

    if (participant == null) return 0.0;

    final expectedPrice =
        participant.manualPriceOverride ?? participant.calculatedPrice;
    final totalPaid = await getTotalPaymentsForParticipant(participantId);

    return expectedPrice - totalPaid;
  }
}
