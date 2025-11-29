import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/database/app_database.dart';
import '../data/repositories/role_repository.dart';
import 'database_provider.dart';
import 'current_event_provider.dart';

/// Provider for RoleRepository
final roleRepositoryProvider = Provider<RoleRepository>((ref) {
  final database = ref.watch(databaseProvider);
  return RoleRepository(database);
});

/// Provider for watching roles for the current event
final rolesProvider = StreamProvider<List<Role>>((ref) {
  final repository = ref.watch(roleRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return Stream.value([]);
  }

  return repository.watchRolesByEvent(currentEvent.id);
});

/// Provider for getting a single role by ID
final roleByIdProvider = FutureProvider.family<Role?, int>((ref, id) async {
  final repository = ref.watch(roleRepositoryProvider);
  return repository.getRoleById(id);
});

/// Provider for roles with participant counts
final rolesWithCountsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final repository = ref.watch(roleRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return [];
  }

  return repository.getRolesWithCounts(currentEvent.id);
});
