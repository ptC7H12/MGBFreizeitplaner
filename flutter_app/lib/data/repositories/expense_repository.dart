import 'package:drift/drift.dart';
import '../database/app_database.dart';

class ExpenseRepository {
  final AppDatabase _database;

  ExpenseRepository(this._database);

  /// Get all expenses for a specific event
  Stream<List<Expense>> watchExpensesByEvent(int eventId) {
    return (_database.select(_database.expenses)
          ..where((t) => t.eventId.equals(eventId) & t.isActive.equals(true))
          ..orderBy([
            (t) => OrderingTerm(expression: t.expenseDate, mode: OrderingMode.desc),
          ]))
        .watch();
  }

  /// Get a single expense by ID
  Future<Expense?> getExpenseById(int id) async {
    return await (_database.select(_database.expenses)
          ..where((t) => t.id.equals(id) & t.isActive.equals(true)))
        .getSingleOrNull();
  }

  /// Get all expenses for an event (one-time fetch)
  Future<List<Expense>> getExpensesByEvent(int eventId) async {
    return await (_database.select(_database.expenses)
          ..where((t) => t.eventId.equals(eventId) & t.isActive.equals(true))
          ..orderBy([
            (t) => OrderingTerm(expression: t.expenseDate, mode: OrderingMode.desc),
          ]))
        .get();
  }

  /// Get total expenses for an event
  Future<double> getTotalExpenses(int eventId) async {
    final result = await _database.customSelect(
      'SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE event_id = ? AND is_active = 1',
      variables: [Variable.withInt(eventId)],
      readsFrom: {_database.expenses},
    ).getSingle();

    return result.read<double>('total');
  }

  /// Get expenses by category
  Future<Map<String, double>> getExpensesByCategory(int eventId) async {
    final results = await _database.customSelect(
      'SELECT category, SUM(amount) as total FROM expenses WHERE event_id = ? AND is_active = 1 GROUP BY category',
      variables: [Variable.withInt(eventId)],
      readsFrom: {_database.expenses},
    ).get();

    return {
      for (final row in results)
        row.read<String>('category'): row.read<double>('total')
    };
  }

  /// Get expenses within a date range
  Future<List<Expense>> getExpensesByDateRange(
    int eventId,
    DateTime startDate,
    DateTime endDate,
  ) async {
    return await (_database.select(_database.expenses)
          ..where((t) =>
              t.eventId.equals(eventId) &
              t.isActive.equals(true) &
              t.expenseDate.isBiggerOrEqualValue(startDate) &
              t.expenseDate.isSmallerOrEqualValue(endDate))
          ..orderBy([
            (t) => OrderingTerm(expression: t.expenseDate, mode: OrderingMode.desc),
          ]))
        .get();
  }

  /// Create a new expense
  Future<int> createExpense({
    required int eventId,
    required String category,
    required double amount,
    required DateTime expenseDate,
    String? description,
    String? paymentMethod,
    String? receiptNumber,
    String? vendor,
    String? notes,
  }) async {
    final companion = ExpensesCompanion(
      eventId: Value(eventId),
      category: Value(category),
      amount: Value(amount),
      expenseDate: Value(expenseDate),
      description: Value(description),
      paymentMethod: Value(paymentMethod),
      receiptNumber: Value(receiptNumber),
      vendor: Value(vendor),
      notes: Value(notes),
      isActive: const Value(true),
      createdAt: Value(DateTime.now()),
      updatedAt: Value(DateTime.now()),
    );

    return await _database.into(_database.expenses).insert(companion);
  }

  /// Update an existing expense
  Future<bool> updateExpense({
    required int id,
    String? category,
    double? amount,
    DateTime? expenseDate,
    String? description,
    String? paymentMethod,
    String? receiptNumber,
    String? vendor,
    String? notes,
  }) async {
    final existing = await getExpenseById(id);
    if (existing == null) return false;

    final companion = ExpensesCompanion(
      id: Value(id),
      category: category != null ? Value(category) : const Value.absent(),
      amount: amount != null ? Value(amount) : const Value.absent(),
      expenseDate: expenseDate != null ? Value(expenseDate) : const Value.absent(),
      description: description != null ? Value(description) : const Value.absent(),
      paymentMethod: paymentMethod != null ? Value(paymentMethod) : const Value.absent(),
      receiptNumber: receiptNumber != null ? Value(receiptNumber) : const Value.absent(),
      vendor: vendor != null ? Value(vendor) : const Value.absent(),
      notes: notes != null ? Value(notes) : const Value.absent(),
      updatedAt: Value(DateTime.now()),
    );

    return await _database.update(_database.expenses).replace(companion);
  }

  /// Soft delete an expense
  Future<bool> deleteExpense(int id) async {
    final existing = await getExpenseById(id);
    if (existing == null) return false;

    return await (_database.update(_database.expenses)
          ..where((t) => t.id.equals(id)))
        .write(
      ExpensesCompanion(
        isActive: const Value(false),
        updatedAt: Value(DateTime.now()),
      ),
    ) >
        0;
  }

  /// Permanently delete an expense (hard delete)
  Future<bool> permanentlyDeleteExpense(int id) async {
    return await (_database.delete(_database.expenses)
          ..where((t) => t.id.equals(id)))
        .go() >
        0;
  }

  /// Get expense statistics for an event
  Future<Map<String, dynamic>> getExpenseStatistics(int eventId) async {
    final expenses = await getExpensesByEvent(eventId);
    final total = await getTotalExpenses(eventId);
    final byCategory = await getExpensesByCategory(eventId);

    // Find most expensive category
    String? mostExpensiveCategory;
    double maxCategoryAmount = 0;
    byCategory.forEach((category, amount) {
      if (amount > maxCategoryAmount) {
        maxCategoryAmount = amount;
        mostExpensiveCategory = category;
      }
    });

    return {
      'total': total,
      'count': expenses.length,
      'byCategory': byCategory,
      'mostExpensiveCategory': mostExpensiveCategory,
      'mostExpensiveCategoryAmount': maxCategoryAmount,
      'averageExpense': expenses.isEmpty ? 0.0 : total / expenses.length,
    };
  }

  /// Search expenses by description, vendor, or notes
  Future<List<Expense>> searchExpenses(int eventId, String query) async {
    final lowerQuery = query.toLowerCase();

    return await (_database.select(_database.expenses)
          ..where((t) =>
              t.eventId.equals(eventId) &
              t.isActive.equals(true) &
              (t.description.lower().like('%$lowerQuery%') |
               t.vendor.lower().like('%$lowerQuery%') |
               t.notes.lower().like('%$lowerQuery%'))))
        .get();
  }
}
