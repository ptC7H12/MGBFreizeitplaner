import 'package:drift/drift.dart';
import '../database/app_database.dart';

class RoleRepository {
  final AppDatabase _database;

  RoleRepository(this._database);

  /// Get all roles for a specific event
  Stream<List<Role>> watchRolesByEvent(int eventId) {
    return (_database.select(_database.roles)
          ..where((t) => t.eventId.equals(eventId))
          ..orderBy([(t) => OrderingTerm(expression: t.name)]))
        .watch();
  }

  /// Get a single role by ID
  Future<Role?> getRoleById(int id) async {
    return await (_database.select(_database.roles)
          ..where((t) => t.id.equals(id)))
        .getSingleOrNull();
  }

  /// Get all roles for an event (one-time fetch)
  Future<List<Role>> getRolesByEvent(int eventId) async {
    return await (_database.select(_database.roles)
          ..where((t) => t.eventId.equals(eventId))
          ..orderBy([(t) => OrderingTerm(expression: t.name)]))
        .get();
  }

  /// Get role by name
  Future<Role?> getRoleByName(int eventId, String name) async {
    return await (_database.select(_database.roles)
          ..where((t) => t.eventId.equals(eventId) & t.name.equals(name)))
        .getSingleOrNull();
  }

  /// Create a new role
  Future<int> createRole({
    required int eventId,
    required String name,
    String? description,
  }) async {
    // Check if role with same name already exists
    final existing = await getRoleByName(eventId, name);
    if (existing != null) {
      throw Exception('Eine Rolle mit diesem Namen existiert bereits');
    }

    final companion = RolesCompanion(
      eventId: Value(eventId),
      name: Value(name),
      description: Value(description),
      createdAt: Value(DateTime.now()),
      updatedAt: Value(DateTime.now()),
    );

    return await _database.into(_database.roles).insert(companion);
  }

  /// Update an existing role
  Future<bool> updateRole({
    required int id,
    String? name,
    String? description,
  }) async {
    final existing = await getRoleById(id);
    if (existing == null) return false;

    // Check if new name conflicts with another role
    if (name != null && name != existing.name) {
      final conflict = await getRoleByName(existing.eventId, name);
      if (conflict != null && conflict.id != id) {
        throw Exception('Eine Rolle mit diesem Namen existiert bereits');
      }
    }

    final companion = RolesCompanion(
      id: Value(id),
      name: name != null ? Value(name) : const Value.absent(),
      description: description != null ? Value(description) : const Value.absent(),
      updatedAt: Value(DateTime.now()),
    );

    return await _database.update(_database.roles).replace(companion);
  }

  /// Delete a role
  Future<bool> deleteRole(int id) async {
    // Check if role is in use by any participants
    final participantsWithRole = await (_database.select(_database.participants)
          ..where((t) => t.roleId.equals(id)))
        .get();

    if (participantsWithRole.isNotEmpty) {
      throw Exception(
        'Diese Rolle kann nicht gelöscht werden, da sie von ${participantsWithRole.length} Teilnehmer(n) verwendet wird',
      );
    }

    return await (_database.delete(_database.roles)
          ..where((t) => t.id.equals(id)))
        .go() >
        0;
  }

  /// Get role statistics
  Future<Map<String, dynamic>> getRoleStatistics(int roleId) async {
    final role = await getRoleById(roleId);
    if (role == null) {
      return {'error': 'Rolle nicht gefunden'};
    }

    // Count participants with this role
    final participants = await (_database.select(_database.participants)
          ..where((t) => t.roleId.equals(roleId) & t.isActive.equals(true)))
        .get();

    return {
      'role': role,
      'participantCount': participants.length,
    };
  }

  /// Get all roles with participant counts
  Future<List<Map<String, dynamic>>> getRolesWithCounts(int eventId) async {
    final roles = await getRolesByEvent(eventId);
    final result = <Map<String, dynamic>>[];

    for (final role in roles) {
      final count = await (_database.select(_database.participants)
            ..where((t) => t.roleId.equals(role.id) & t.isActive.equals(true)))
          .get()
          .then((list) => list.length);

      result.add({
        'role': role,
        'participantCount': count,
      });
    }

    return result;
  }
}
