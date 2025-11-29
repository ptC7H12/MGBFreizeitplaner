import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/database/app_database.dart';
import '../data/repositories/expense_repository.dart';
import 'database_provider.dart';
import 'current_event_provider.dart';

/// Provider for ExpenseRepository
final expenseRepositoryProvider = Provider<ExpenseRepository>((ref) {
  final database = ref.watch(databaseProvider);
  return ExpenseRepository(database);
});

/// Provider for watching expenses for the current event
final expensesProvider = StreamProvider<List<Expense>>((ref) {
  final repository = ref.watch(expenseRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return Stream.value([]);
  }

  return repository.watchExpensesByEvent(currentEvent.id);
});

/// Provider for getting a single expense by ID
final expenseByIdProvider = FutureProvider.family<Expense?, int>((ref, id) async {
  final repository = ref.watch(expenseRepositoryProvider);
  return repository.getExpenseById(id);
});

/// Provider for total expenses
final totalExpensesProvider = FutureProvider<double>((ref) async {
  final repository = ref.watch(expenseRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return 0.0;
  }

  return repository.getTotalExpenses(currentEvent.id);
});

/// Provider for expenses by category
final expensesByCategoryProvider = FutureProvider<Map<String, double>>((ref) async {
  final repository = ref.watch(expenseRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return {};
  }

  return repository.getExpensesByCategory(currentEvent.id);
});

/// Provider for expense statistics
final expenseStatisticsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final repository = ref.watch(expenseRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return {
      'total': 0.0,
      'count': 0,
      'byCategory': {},
      'mostExpensiveCategory': null,
      'mostExpensiveCategoryAmount': 0.0,
      'averageExpense': 0.0,
    };
  }

  return repository.getExpenseStatistics(currentEvent.id);
});
