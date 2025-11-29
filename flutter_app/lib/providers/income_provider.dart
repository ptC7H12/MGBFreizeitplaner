import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/database/app_database.dart';
import '../data/repositories/income_repository.dart';
import 'database_provider.dart';
import 'current_event_provider.dart';

/// Provider for IncomeRepository
final incomeRepositoryProvider = Provider<IncomeRepository>((ref) {
  final database = ref.watch(databaseProvider);
  return IncomeRepository(database);
});

/// Provider for watching incomes for the current event
final incomesProvider = StreamProvider<List<Income>>((ref) {
  final repository = ref.watch(incomeRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return Stream.value([]);
  }

  return repository.watchIncomesByEvent(currentEvent.id);
});

/// Provider for getting a single income by ID
final incomeByIdProvider = FutureProvider.family<Income?, int>((ref, id) async {
  final repository = ref.watch(incomeRepositoryProvider);
  return repository.getIncomeById(id);
});

/// Provider for total incomes
final totalIncomesProvider = FutureProvider<double>((ref) async {
  final repository = ref.watch(incomeRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return 0.0;
  }

  return repository.getTotalIncomes(currentEvent.id);
});

/// Provider for incomes by source
final incomesBySourceProvider = FutureProvider<Map<String, double>>((ref) async {
  final repository = ref.watch(incomeRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return {};
  }

  return repository.getIncomesBySource(currentEvent.id);
});

/// Provider for income statistics
final incomeStatisticsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final repository = ref.watch(incomeRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return {
      'total': 0.0,
      'count': 0,
      'bySource': {},
      'largestSource': null,
      'largestSourceAmount': 0.0,
      'averageIncome': 0.0,
    };
  }

  return repository.getIncomeStatistics(currentEvent.id);
});
