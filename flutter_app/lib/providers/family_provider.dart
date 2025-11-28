import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/repositories/family_repository.dart';
import '../data/database/app_database.dart';
import 'database_provider.dart';
import 'current_event_provider.dart';

/// Provider für Family Repository
final familyRepositoryProvider = Provider<FamilyRepository>((ref) {
  final database = ref.watch(databaseProvider);
  return FamilyRepository(database);
});

/// Provider für Familien-Liste des aktuellen Events
final familiesProvider = StreamProvider<List<Family>>((ref) {
  final repository = ref.watch(familyRepositoryProvider);
  final eventId = ref.watch(currentEventIdProvider);

  if (eventId == null) {
    return Stream.value([]);
  }

  return repository.watchFamiliesByEvent(eventId);
});

/// Provider für einzelne Familie
final familyProvider = StreamProvider.family<Family?, int>((ref, familyId) {
  final database = ref.watch(databaseProvider);
  return (database.select(database.families)
        ..where((tbl) => tbl.id.equals(familyId)))
      .watchSingleOrNull();
});
