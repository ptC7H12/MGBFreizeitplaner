import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/current_event_provider.dart';
import '../../providers/participant_provider.dart';
import '../../data/database/app_database.dart';
import '../../utils/date_utils.dart';
import 'participant_form_screen.dart';
import 'participant_import_screen.dart';

/// Participants List Screen
///
/// Zeigt alle Teilnehmer des aktuellen Events
class ParticipantsListScreen extends ConsumerWidget {
  const ParticipantsListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final participantsAsync = ref.watch(participantsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Teilnehmer'),
        actions: [
          IconButton(
            icon: const Icon(Icons.upload_file),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const ParticipantImportScreen(),
                ),
              );
            },
            tooltip: 'Excel importieren',
          ),
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              // TODO: Search
            },
          ),
        ],
      ),
      body: participantsAsync.when(
        data: (participants) {
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
                        'Geb.: ${AppDateUtils.formatGerman(participant.birthDate)} (${AppDateUtils.calculateAge(participant.birthDate)} Jahre)',
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
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (context) => ParticipantFormScreen(
                          participantId: participant.id,
                        ),
                      ),
                    );
                  },
                ),
              );
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Text('Fehler: $error'),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => const ParticipantFormScreen(),
            ),
          );
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

  double _getDisplayPrice(Participant participant) {
    return participant.manualPriceOverride ?? participant.calculatedPrice;
  }
}
