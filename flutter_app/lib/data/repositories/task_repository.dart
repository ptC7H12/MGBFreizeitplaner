import 'package:drift/drift.dart';
import '../database/app_database.dart';

class TaskRepository {
  final AppDatabase _database;

  TaskRepository(this._database);

  /// Get all tasks for a specific event
  Stream<List<Task>> watchTasksByEvent(int eventId) {
    return (_database.select(_database.tasks)
          ..where((t) => t.eventId.equals(eventId))
          ..orderBy([
            (t) => OrderingTerm(expression: t.dueDate),
            (t) => OrderingTerm(expression: t.priority, mode: OrderingMode.desc),
          ]))
        .watch();
  }

  /// Get a single task by ID
  Future<Task?> getTaskById(int id) async {
    return await (_database.select(_database.tasks)
          ..where((t) => t.id.equals(id)))
        .getSingleOrNull();
  }

  /// Get all tasks for an event (one-time fetch)
  Future<List<Task>> getTasksByEvent(int eventId) async {
    return await (_database.select(_database.tasks)
          ..where((t) => t.eventId.equals(eventId))
          ..orderBy([
            (t) => OrderingTerm(expression: t.dueDate),
            (t) => OrderingTerm(expression: t.priority, mode: OrderingMode.desc),
          ]))
        .get();
  }

  /// Get tasks by status
  Future<List<Task>> getTasksByStatus(int eventId, String status) async {
    return await (_database.select(_database.tasks)
          ..where((t) => t.eventId.equals(eventId) & t.status.equals(status))
          ..orderBy([
            (t) => OrderingTerm(expression: t.dueDate),
          ]))
        .get();
  }

  /// Get tasks assigned to a participant
  Future<List<Task>> getTasksByParticipant(int participantId) async {
    return await (_database.select(_database.tasks)
          ..where((t) => t.assignedTo.equals(participantId))
          ..orderBy([
            (t) => OrderingTerm(expression: t.dueDate),
          ]))
        .get();
  }

  /// Get overdue tasks
  Future<List<Task>> getOverdueTasks(int eventId) async {
    final now = DateTime.now();
    return await (_database.select(_database.tasks)
          ..where((t) =>
              t.eventId.equals(eventId) &
              t.status.equals('pending') &
              t.dueDate.isSmallerThanValue(now))
          ..orderBy([
            (t) => OrderingTerm(expression: t.priority, mode: OrderingMode.desc),
          ]))
        .get();
  }

  /// Get upcoming tasks (next 7 days)
  Future<List<Task>> getUpcomingTasks(int eventId) async {
    final now = DateTime.now();
    final sevenDaysFromNow = now.add(const Duration(days: 7));
    return await (_database.select(_database.tasks)
          ..where((t) =>
              t.eventId.equals(eventId) &
              t.status.equals('pending') &
              t.dueDate.isBiggerOrEqualValue(now) &
              t.dueDate.isSmallerOrEqualValue(sevenDaysFromNow))
          ..orderBy([
            (t) => OrderingTerm(expression: t.dueDate),
          ]))
        .get();
  }

  /// Create a new task
  Future<int> createTask({
    required int eventId,
    required String title,
    required DateTime dueDate,
    String? description,
    String status = 'pending',
    int priority = 1,
    int? assignedTo,
  }) async {
    final companion = TasksCompanion(
      eventId: Value(eventId),
      title: Value(title),
      description: Value(description),
      status: Value(status),
      priority: Value(priority),
      dueDate: Value(dueDate),
      assignedTo: Value(assignedTo),
      createdAt: Value(DateTime.now()),
      updatedAt: Value(DateTime.now()),
    );

    return await _database.into(_database.tasks).insert(companion);
  }

  /// Update an existing task
  Future<bool> updateTask({
    required int id,
    String? title,
    String? description,
    String? status,
    int? priority,
    DateTime? dueDate,
    int? assignedTo,
    bool? clearAssignment,
  }) async {
    final existing = await getTaskById(id);
    if (existing == null) return false;

    final companion = TasksCompanion(
      id: Value(id),
      title: title != null ? Value(title) : const Value.absent(),
      description: description != null ? Value(description) : const Value.absent(),
      status: status != null ? Value(status) : const Value.absent(),
      priority: priority != null ? Value(priority) : const Value.absent(),
      dueDate: dueDate != null ? Value(dueDate) : const Value.absent(),
      assignedTo: clearAssignment == true
          ? const Value(null)
          : (assignedTo != null ? Value(assignedTo) : const Value.absent()),
      updatedAt: Value(DateTime.now()),
    );

    return await _database.update(_database.tasks).replace(companion);
  }

  /// Mark task as completed
  Future<bool> completeTask(int id) async {
    return updateTask(id: id, status: 'completed');
  }

  /// Mark task as in progress
  Future<bool> startTask(int id) async {
    return updateTask(id: id, status: 'in_progress');
  }

  /// Delete a task
  Future<bool> deleteTask(int id) async {
    return await (_database.delete(_database.tasks)
          ..where((t) => t.id.equals(id)))
        .go() >
        0;
  }

  /// Get task statistics
  Future<Map<String, dynamic>> getTaskStatistics(int eventId) async {
    final tasks = await getTasksByEvent(eventId);
    final pending = tasks.where((t) => t.status == 'pending').length;
    final inProgress = tasks.where((t) => t.status == 'in_progress').length;
    final completed = tasks.where((t) => t.status == 'completed').length;
    final overdue = await getOverdueTasks(eventId);

    return {
      'total': tasks.length,
      'pending': pending,
      'inProgress': inProgress,
      'completed': completed,
      'overdue': overdue.length,
      'completionRate': tasks.isEmpty ? 0.0 : (completed / tasks.length) * 100,
    };
  }
}
