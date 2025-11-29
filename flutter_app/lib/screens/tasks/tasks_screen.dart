import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../data/database/app_database.dart';
import '../../providers/task_provider.dart';
import '../../providers/current_event_provider.dart';
import '../../providers/participant_provider.dart';
import '../../data/repositories/task_repository.dart';

class TasksScreen extends ConsumerStatefulWidget {
  const TasksScreen({super.key});

  @override
  ConsumerState<TasksScreen> createState() => _TasksScreenState();
}

class _TasksScreenState extends ConsumerState<TasksScreen> {
  String _selectedTab = 'all'; // 'all', 'pending', 'completed', 'overdue'

  @override
  Widget build(BuildContext context) {
    final currentEvent = ref.watch(currentEventProvider);
    final tasksAsync = ref.watch(tasksProvider);
    final statsAsync = ref.watch(taskStatisticsProvider);

    if (currentEvent == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Aufgaben')),
        body: const Center(child: Text('Bitte wählen Sie zuerst eine Veranstaltung aus.')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Aufgaben'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _showTaskDialog(context),
            tooltip: 'Neue Aufgabe',
          ),
        ],
      ),
      body: Column(
        children: [
          // Statistics Card
          statsAsync.when(
            data: (stats) => Card(
              margin: const EdgeInsets.all(16),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildStatItem(Icons.list_alt, 'Gesamt', '${stats['total']}', Colors.blue),
                    _buildStatItem(Icons.pending, 'Offen', '${stats['pending']}', Colors.orange),
                    _buildStatItem(Icons.check_circle, 'Erledigt', '${stats['completed']}', Colors.green),
                    if (stats['overdue'] > 0)
                      _buildStatItem(Icons.warning, 'Überfällig', '${stats['overdue']}', Colors.red),
                  ],
                ),
              ),
            ),
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
          ),

          // Filter Tabs
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                _buildFilterChip('Alle', 'all'),
                _buildFilterChip('Offen', 'pending'),
                _buildFilterChip('Erledigt', 'completed'),
                _buildFilterChip('Überfällig', 'overdue'),
              ],
            ),
          ),
          const SizedBox(height: 8),

          // Tasks List
          Expanded(
            child: tasksAsync.when(
              data: (tasks) {
                final filteredTasks = _filterTasks(tasks);
                if (filteredTasks.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.task_alt, size: 80, color: Colors.grey[400]),
                        const SizedBox(height: 16),
                        Text('Keine Aufgaben', style: TextStyle(color: Colors.grey[600])),
                      ],
                    ),
                  );
                }

                return ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: filteredTasks.length,
                  itemBuilder: (context, index) =>
                      _TaskListItem(task: filteredTasks[index], onTap: () => _showTaskDialog(context, filteredTasks[index])),
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: Text('Fehler: $e')),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showTaskDialog(context),
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildStatItem(IconData icon, String label, String value, Color color) {
    return Column(
      children: [
        Icon(icon, color: color),
        const SizedBox(height: 4),
        Text(value, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: color)),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
      ],
    );
  }

  Widget _buildFilterChip(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: FilterChip(
        label: Text(label),
        selected: _selectedTab == value,
        onSelected: (selected) => setState(() => _selectedTab = value),
      ),
    );
  }

  List<Task> _filterTasks(List<Task> tasks) {
    final now = DateTime.now();
    switch (_selectedTab) {
      case 'pending':
        return tasks.where((t) => t.status == 'pending').toList();
      case 'completed':
        return tasks.where((t) => t.status == 'completed').toList();
      case 'overdue':
        return tasks.where((t) => t.status == 'pending' && t.dueDate.isBefore(now)).toList();
      default:
        return tasks;
    }
  }

  void _showTaskDialog(BuildContext context, [Task? task]) {
    showDialog(
      context: context,
      builder: (context) => _TaskFormDialog(task: task),
    );
  }
}

class _TaskListItem extends StatelessWidget {
  final Task task;
  final VoidCallback onTap;

  const _TaskListItem({required this.task, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final isOverdue = task.status == 'pending' && task.dueDate.isBefore(DateTime.now());
    return Card(
      child: ListTile(
        leading: Icon(
          task.status == 'completed' ? Icons.check_circle : Icons.radio_button_unchecked,
          color: task.status == 'completed' ? Colors.green : (isOverdue ? Colors.red : Colors.grey),
        ),
        title: Text(task.title, style: TextStyle(decoration: task.status == 'completed' ? TextDecoration.lineThrough : null)),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (task.description != null) Text(task.description!, maxLines: 1, overflow: TextOverflow.ellipsis),
            Text('Fällig: ${DateFormat('dd.MM.yyyy', 'de_DE').format(task.dueDate)}', style: TextStyle(color: isOverdue ? Colors.red : null)),
          ],
        ),
        trailing: _PriorityBadge(priority: task.priority),
        onTap: onTap,
      ),
    );
  }
}

class _PriorityBadge extends StatelessWidget {
  final int priority;
  const _PriorityBadge({required this.priority});

  @override
  Widget build(BuildContext context) {
    final color = priority == 3 ? Colors.red : (priority == 2 ? Colors.orange : Colors.grey);
    final label = priority == 3 ? 'Hoch' : (priority == 2 ? 'Mittel' : 'Niedrig');
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(12)),
      child: Text(label, style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }
}

class _TaskFormDialog extends ConsumerStatefulWidget {
  final Task? task;
  const _TaskFormDialog({this.task});

  @override
  ConsumerState<_TaskFormDialog> createState() => _TaskFormDialogState();
}

class _TaskFormDialogState extends ConsumerState<_TaskFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _titleController;
  late TextEditingController _descriptionController;
  late DateTime _dueDate;
  late int _priority;
  late String _status;
  int? _assignedTo;

  @override
  void initState() {
    super.initState();
    _titleController = TextEditingController(text: widget.task?.title);
    _descriptionController = TextEditingController(text: widget.task?.description);
    _dueDate = widget.task?.dueDate ?? DateTime.now().add(const Duration(days: 7));
    _priority = widget.task?.priority ?? 1;
    _status = widget.task?.status ?? 'pending';
    _assignedTo = widget.task?.assignedTo;
  }

  @override
  Widget build(BuildContext context) {
    final participantsAsync = ref.watch(participantsProvider);

    return AlertDialog(
      title: Text(widget.task == null ? 'Neue Aufgabe' : 'Aufgabe bearbeiten'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _titleController,
                decoration: const InputDecoration(labelText: 'Titel *', border: OutlineInputBorder()),
                validator: (v) => v?.isEmpty == true ? 'Titel erforderlich' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(labelText: 'Beschreibung', border: OutlineInputBorder()),
                maxLines: 3,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<int>(
                value: _priority,
                decoration: const InputDecoration(labelText: 'Priorität', border: OutlineInputBorder()),
                items: const [
                  DropdownMenuItem(value: 1, child: Text('Niedrig')),
                  DropdownMenuItem(value: 2, child: Text('Mittel')),
                  DropdownMenuItem(value: 3, child: Text('Hoch')),
                ],
                onChanged: (v) => setState(() => _priority = v!),
              ),
              const SizedBox(height: 12),
              InkWell(
                onTap: () async {
                  final picked = await showDatePicker(
                    context: context,
                    initialDate: _dueDate,
                    firstDate: DateTime(2000),
                    lastDate: DateTime(2100),
                  );
                  if (picked != null) setState(() => _dueDate = picked);
                },
                child: InputDecorator(
                  decoration: const InputDecoration(labelText: 'Fälligkeitsdatum', border: OutlineInputBorder()),
                  child: Text(DateFormat('dd.MM.yyyy').format(_dueDate)),
                ),
              ),
              const SizedBox(height: 12),
              participantsAsync.when(
                data: (participants) => DropdownButtonFormField<int?>(
                  value: _assignedTo,
                  decoration: const InputDecoration(labelText: 'Zugewiesen an', border: OutlineInputBorder()),
                  items: [
                    const DropdownMenuItem(value: null, child: Text('Nicht zugewiesen')),
                    ...participants.map((p) => DropdownMenuItem(value: p.id, child: Text('${p.firstName} ${p.lastName}'))),
                  ],
                  onChanged: (v) => setState(() => _assignedTo = v),
                ),
                loading: () => const CircularProgressIndicator(),
                error: (_, __) => const Text('Fehler beim Laden'),
              ),
            ],
          ),
        ),
      ),
      actions: [
        if (widget.task != null)
          TextButton(
            onPressed: () async {
              final repo = ref.read(taskRepositoryProvider);
              await repo.deleteTask(widget.task!.id);
              if (mounted) Navigator.pop(context);
            },
            child: const Text('Löschen', style: TextStyle(color: Colors.red)),
          ),
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Abbrechen')),
        FilledButton(
          onPressed: () async {
            if (!_formKey.currentState!.validate()) return;
            final repo = ref.read(taskRepositoryProvider);
            final event = ref.read(currentEventProvider)!;

            if (widget.task == null) {
              await repo.createTask(
                eventId: event.id,
                title: _titleController.text,
                description: _descriptionController.text.isEmpty ? null : _descriptionController.text,
                dueDate: _dueDate,
                priority: _priority,
                status: _status,
                assignedTo: _assignedTo,
              );
            } else {
              await repo.updateTask(
                id: widget.task!.id,
                title: _titleController.text,
                description: _descriptionController.text.isEmpty ? null : _descriptionController.text,
                dueDate: _dueDate,
                priority: _priority,
                status: _status,
                assignedTo: _assignedTo,
              );
            }
            if (mounted) Navigator.pop(context);
          },
          child: const Text('Speichern'),
        ),
      ],
    );
  }
}
