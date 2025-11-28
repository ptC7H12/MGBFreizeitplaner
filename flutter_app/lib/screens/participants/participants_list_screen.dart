import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/current_event_provider.dart';
import '../../providers/database_provider.dart';
import '../../data/database/app_database.dart';

/// Participants List Screen
///
/// Zeigt alle Teilnehmer des aktuellen Events
class ParticipantsListScreen extends ConsumerWidget {
  const ParticipantsListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final database = ref.watch(databaseProvider);
    final eventId = ref.watch(currentEventIdProvider);

    if (eventId == null) {
      return const Scaffold(
        body: Center(child: Text('Kein Event ausgewählt')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Teilnehmer'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              // TODO: Search
            },
          ),
        ],
      ),
      body: StreamBuilder<List<Participant>>(
        stream: (database.select(database.participants)
              ..where((tbl) => tbl.eventId.equals(eventId))
              ..where((tbl) => tbl.isActive.equals(true))
              ..orderBy([(tbl) => OrderingTerm.asc(tbl.lastName)]))
            .watch(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          final participants = snapshot.data ?? [];

          if (participants.isEmpty) {
            return _buildEmptyState(context);
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: participants.length,
            itemBuilder: (context, index) {
              final participant = participants[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  leading: CircleAvatar(
                    child: Text(
                      participant.firstName[0].toUpperCase(),
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                  title: Text(
                    '${participant.firstName} ${participant.lastName}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SizedBox(height: 4),
                      Text(
                        'Geb.: ${_formatDate(participant.birthDate)} (${_calculateAge(participant.birthDate)} Jahre)',
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Preis: ${_getDisplayPrice(participant).toStringAsFixed(2)} €',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.green,
                        ),
                      ),
                    ],
                  ),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    // TODO: Detail Screen
                  },
                ),
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          // TODO: Create Participant Screen
        },
        icon: const Icon(Icons.add),
        label: const Text('Teilnehmer'),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.people_outline,
            size: 100,
            color: Colors.grey,
          ),
          const SizedBox(height: 24),
          const Text(
            'Noch keine Teilnehmer',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Füge deinen ersten Teilnehmer hinzu.',
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}.${date.month.toString().padLeft(2, '0')}.${date.year}';
  }

  int _calculateAge(DateTime birthDate) {
    final now = DateTime.now();
    int age = now.year - birthDate.year;
    if (now.month < birthDate.month ||
        (now.month == birthDate.month && now.day < birthDate.day)) {
      age--;
    }
    return age;
  }

  double _getDisplayPrice(Participant participant) {
    if (participant.manualPriceOverride != null) {
      return participant.manualPriceOverride!;
    }
    return participant.calculatedPrice;
  }
}
