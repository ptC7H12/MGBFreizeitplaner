import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/database/app_database.dart';
import '../data/repositories/task_repository.dart';
import 'database_provider.dart';
import 'current_event_provider.dart';

/// Provider for TaskRepository
final taskRepositoryProvider = Provider<TaskRepository>((ref) {
  final database = ref.watch(databaseProvider);
  return TaskRepository(database);
});

/// Provider for watching tasks for the current event
final tasksProvider = StreamProvider<List<Task>>((ref) {
  final repository = ref.watch(taskRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return Stream.value([]);
  }

  return repository.watchTasksByEvent(currentEvent.id);
});

/// Provider for getting a single task by ID
final taskByIdProvider = FutureProvider.family<Task?, int>((ref, id) async {
  final repository = ref.watch(taskRepositoryProvider);
  return repository.getTaskById(id);
});

/// Provider for task statistics
final taskStatisticsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final repository = ref.watch(taskRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return {
      'total': 0,
      'pending': 0,
      'inProgress': 0,
      'completed': 0,
      'overdue': 0,
      'completionRate': 0.0,
    };
  }

  return repository.getTaskStatistics(currentEvent.id);
});

/// Provider for overdue tasks
final overdueTasksProvider = FutureProvider<List<Task>>((ref) async {
  final repository = ref.watch(taskRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return [];
  }

  return repository.getOverdueTasks(currentEvent.id);
});

/// Provider for upcoming tasks
final upcomingTasksProvider = FutureProvider<List<Task>>((ref) async {
  final repository = ref.watch(taskRepositoryProvider);
  final currentEvent = ref.watch(currentEventProvider);

  if (currentEvent == null) {
    return [];
  }

  return repository.getUpcomingTasks(currentEvent.id);
});
