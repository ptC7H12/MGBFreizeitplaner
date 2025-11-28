import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:drift/drift.dart' as drift;
import '../../data/database/app_database.dart';
import '../../providers/database_provider.dart';
import '../../providers/current_event_provider.dart';
import '../dashboard/dashboard_screen.dart';

/// Event Selection Screen
///
/// Entspricht der Landing Page / Event-Auswahl in der Web-App
/// Nutzer wählt hier das Event aus, an dem er arbeiten möchte
class EventSelectionScreen extends ConsumerWidget {
  const EventSelectionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final database = ref.watch(databaseProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('MGB Freizeitplaner'),
        centerTitle: true,
      ),
      body: StreamBuilder<List<Event>>(
        stream: database.select(database.events).watch(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text('Fehler: ${snapshot.error}'),
                ],
              ),
            );
          }

          final events = snapshot.data ?? [];

          if (events.isEmpty) {
            return _buildEmptyState(context, database);
          }

          return _buildEventList(context, ref, events);
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showCreateEventDialog(context, ref),
        icon: const Icon(Icons.add),
        label: const Text('Neues Event'),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context, AppDatabase database) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.event_outlined,
            size: 100,
            color: Colors.grey,
          ),
          const SizedBox(height: 24),
          const Text(
            'Noch keine Events vorhanden',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Erstelle dein erstes Event, um zu beginnen.',
            style: TextStyle(color: Colors.grey),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => _showCreateEventDialog(context, null),
            icon: const Icon(Icons.add),
            label: const Text('Erstes Event erstellen'),
          ),
        ],
      ),
    );
  }

  Widget _buildEventList(
    BuildContext context,
    WidgetRef ref,
    List<Event> events,
  ) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 600),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 24),
              const Text(
                'Wähle ein Event aus',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              const Text(
                'Mit welchem Event möchtest du arbeiten?',
                style: TextStyle(color: Colors.grey),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              Expanded(
                child: ListView.builder(
                  itemCount: events.length,
                  itemBuilder: (context, index) {
                    final event = events[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ListTile(
                        contentPadding: const EdgeInsets.all(16),
                        leading: CircleAvatar(
                          backgroundColor: Theme.of(context).primaryColor,
                          child: const Icon(Icons.event, color: Colors.white),
                        ),
                        title: Text(
                          event.name,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 18,
                          ),
                        ),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                const Icon(Icons.calendar_today, size: 16),
                                const SizedBox(width: 4),
                                Text(
                                  '${_formatDate(event.startDate)} - ${_formatDate(event.endDate)}',
                                ),
                              ],
                            ),
                            if (event.location != null) ...[
                              const SizedBox(height: 4),
                              Row(
                                children: [
                                  const Icon(Icons.location_on, size: 16),
                                  const SizedBox(width: 4),
                                  Text(event.location!),
                                ],
                              ),
                            ],
                          ],
                        ),
                        trailing: const Icon(Icons.arrow_forward_ios),
                        onTap: () => _selectEvent(context, ref, event),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _selectEvent(BuildContext context, WidgetRef ref, Event event) {
    // Event in State speichern
    ref.read(currentEventProvider.notifier).selectEvent(event);

    // Zum Dashboard navigieren
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (context) => const DashboardScreen(),
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}.${date.month.toString().padLeft(2, '0')}.${date.year}';
  }

  void _showCreateEventDialog(BuildContext context, WidgetRef? ref) {
    final nameController = TextEditingController();
    final locationController = TextEditingController();
    DateTime startDate = DateTime.now();
    DateTime endDate = DateTime.now().add(const Duration(days: 7));

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Neues Event erstellen'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(
                  labelText: 'Event-Name *',
                  hintText: 'z.B. Sommerfreizeit 2025',
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: locationController,
                decoration: const InputDecoration(
                  labelText: 'Ort',
                  hintText: 'z.B. Campingplatz Müggelsee',
                ),
              ),
              // TODO: Date pickers für Start/End-Datum
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Abbrechen'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (nameController.text.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Bitte Event-Name eingeben'),
                  ),
                );
                return;
              }

              // Event erstellen
              final database = ref?.read(databaseProvider);
              if (database != null) {
                await database.into(database.events).insert(
                      EventsCompanion.insert(
                        name: nameController.text,
                        startDate: startDate,
                        endDate: endDate,
                        location: drift.Value(locationController.text.isEmpty
                            ? null
                            : locationController.text),
                      ),
                    );
              }

              if (context.mounted) {
                Navigator.of(context).pop();
              }
            },
            child: const Text('Erstellen'),
          ),
        ],
      ),
    );
  }
}
