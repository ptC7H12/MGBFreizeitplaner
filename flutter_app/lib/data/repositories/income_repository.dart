import 'package:drift/drift.dart';
import '../database/app_database.dart';

class IncomeRepository {
  final AppDatabase _database;

  IncomeRepository(this._database);

  /// Get all incomes for a specific event
  Stream<List<Income>> watchIncomesByEvent(int eventId) {
    return (_database.select(_database.incomes)
          ..where((t) => t.eventId.equals(eventId) & t.isActive.equals(true))
          ..orderBy([
            (t) => OrderingTerm(expression: t.incomeDate, mode: OrderingMode.desc),
          ]))
        .watch();
  }

  /// Get a single income by ID
  Future<Income?> getIncomeById(int id) async {
    return await (_database.select(_database.incomes)
          ..where((t) => t.id.equals(id) & t.isActive.equals(true)))
        .getSingleOrNull();
  }

  /// Get all incomes for an event (one-time fetch)
  Future<List<Income>> getIncomesByEvent(int eventId) async {
    return await (_database.select(_database.incomes)
          ..where((t) => t.eventId.equals(eventId) & t.isActive.equals(true))
          ..orderBy([
            (t) => OrderingTerm(expression: t.incomeDate, mode: OrderingMode.desc),
          ]))
        .get();
  }

  /// Get total incomes for an event
  Future<double> getTotalIncomes(int eventId) async {
    final result = await _database.customSelect(
      'SELECT COALESCE(SUM(amount), 0) as total FROM incomes WHERE event_id = ? AND is_active = 1',
      variables: [Variable.withInt(eventId)],
      readsFrom: {_database.incomes},
    ).getSingle();

    return result.read<double>('total');
  }

  /// Get incomes by source
  Future<Map<String, double>> getIncomesBySource(int eventId) async {
    final results = await _database.customSelect(
      'SELECT source, SUM(amount) as total FROM incomes WHERE event_id = ? AND is_active = 1 GROUP BY source',
      variables: [Variable.withInt(eventId)],
      readsFrom: {_database.incomes},
    ).get();

    return {
      for (final row in results)
        row.read<String>('source'): row.read<double>('total')
    };
  }

  /// Get incomes within a date range
  Future<List<Income>> getIncomesByDateRange(
    int eventId,
    DateTime startDate,
    DateTime endDate,
  ) async {
    return await (_database.select(_database.incomes)
          ..where((t) =>
              t.eventId.equals(eventId) &
              t.isActive.equals(true) &
              t.incomeDate.isBiggerOrEqualValue(startDate) &
              t.incomeDate.isSmallerOrEqualValue(endDate))
          ..orderBy([
            (t) => OrderingTerm(expression: t.incomeDate, mode: OrderingMode.desc),
          ]))
        .get();
  }

  /// Create a new income
  Future<int> createIncome({
    required int eventId,
    required String source,
    required double amount,
    required DateTime incomeDate,
    String? description,
    String? paymentMethod,
    String? referenceNumber,
    String? notes,
  }) async {
    final companion = IncomesCompanion(
      eventId: Value(eventId),
      source: Value(source),
      amount: Value(amount),
      incomeDate: Value(incomeDate),
      description: Value(description),
      paymentMethod: Value(paymentMethod),
      referenceNumber: Value(referenceNumber),
      notes: Value(notes),
      isActive: const Value(true),
      createdAt: Value(DateTime.now()),
      updatedAt: Value(DateTime.now()),
    );

    return await _database.into(_database.incomes).insert(companion);
  }

  /// Update an existing income
  Future<bool> updateIncome({
    required int id,
    String? source,
    double? amount,
    DateTime? incomeDate,
    String? description,
    String? paymentMethod,
    String? referenceNumber,
    String? notes,
  }) async {
    final existing = await getIncomeById(id);
    if (existing == null) return false;

    final companion = IncomesCompanion(
      id: Value(id),
      source: source != null ? Value(source) : const Value.absent(),
      amount: amount != null ? Value(amount) : const Value.absent(),
      incomeDate: incomeDate != null ? Value(incomeDate) : const Value.absent(),
      description: description != null ? Value(description) : const Value.absent(),
      paymentMethod: paymentMethod != null ? Value(paymentMethod) : const Value.absent(),
      referenceNumber: referenceNumber != null ? Value(referenceNumber) : const Value.absent(),
      notes: notes != null ? Value(notes) : const Value.absent(),
      updatedAt: Value(DateTime.now()),
    );

    return await _database.update(_database.incomes).replace(companion);
  }

  /// Soft delete an income
  Future<bool> deleteIncome(int id) async {
    final existing = await getIncomeById(id);
    if (existing == null) return false;

    return await (_database.update(_database.incomes)
          ..where((t) => t.id.equals(id)))
        .write(
      IncomesCompanion(
        isActive: const Value(false),
        updatedAt: Value(DateTime.now()),
      ),
    ) >
        0;
  }

  /// Permanently delete an income (hard delete)
  Future<bool> permanentlyDeleteIncome(int id) async {
    return await (_database.delete(_database.incomes)
          ..where((t) => t.id.equals(id)))
        .go() >
        0;
  }

  /// Get income statistics for an event
  Future<Map<String, dynamic>> getIncomeStatistics(int eventId) async {
    final incomes = await getIncomesByEvent(eventId);
    final total = await getTotalIncomes(eventId);
    final bySource = await getIncomesBySource(eventId);

    // Find largest income source
    String? largestSource;
    double maxSourceAmount = 0;
    bySource.forEach((source, amount) {
      if (amount > maxSourceAmount) {
        maxSourceAmount = amount;
        largestSource = source;
      }
    });

    return {
      'total': total,
      'count': incomes.length,
      'bySource': bySource,
      'largestSource': largestSource,
      'largestSourceAmount': maxSourceAmount,
      'averageIncome': incomes.isEmpty ? 0.0 : total / incomes.length,
    };
  }

  /// Search incomes by description or notes
  Future<List<Income>> searchIncomes(int eventId, String query) async {
    final lowerQuery = query.toLowerCase();

    return await (_database.select(_database.incomes)
          ..where((t) =>
              t.eventId.equals(eventId) &
              t.isActive.equals(true) &
              (t.description.lower().like('%$lowerQuery%') |
               t.notes.lower().like('%$lowerQuery%') |
               t.source.lower().like('%$lowerQuery%'))))
        .get();
  }
}
