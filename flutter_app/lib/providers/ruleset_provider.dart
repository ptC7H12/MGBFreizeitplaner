import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/database/app_database.dart';
import '../data/repositories/ruleset_repository.dart';
import 'database_provider.dart';
import 'current_event_provider.dart';

/// Provider for RulesetRepository
final rulesetRepositoryProvider = Provider<RulesetRepository>((ref) {
  final database = ref.watch(databaseProvider);
  return RulesetRepository(database);
});

/// Provider for watching rulesets for the current event
final rulesetsProvider = StreamProvider<List<Ruleset>>((ref) {
  final repository = ref.watch(rulesetRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return Stream.value([]);
  }

  return repository.watchRulesetsByEvent(currentEvent.id);
});

/// Provider for getting a single ruleset by ID
final rulesetByIdProvider = FutureProvider.family<Ruleset?, int>((ref, id) async {
  final repository = ref.watch(rulesetRepositoryProvider);
  return repository.getRulesetById(id);
});

/// Provider for getting the current active ruleset
final currentRulesetProvider = FutureProvider<Ruleset?>((ref) async {
  final repository = ref.watch(rulesetRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return null;
  }

  return repository.getCurrentRuleset(currentEvent.id);
});

/// Provider for getting a ruleset with parsed data
final rulesetWithParsedDataProvider =
    FutureProvider.family<Map<String, dynamic>?, int>((ref, id) async {
  final repository = ref.watch(rulesetRepositoryProvider);
  return repository.getRulesetWithParsedData(id);
});

/// Provider for getting ruleset statistics
final rulesetStatisticsProvider =
    FutureProvider.family<Map<String, dynamic>, int>((ref, id) async {
  final repository = ref.watch(rulesetRepositoryProvider);
  return repository.getRulesetStatistics(id);
});
