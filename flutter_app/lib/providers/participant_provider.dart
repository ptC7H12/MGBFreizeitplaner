import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/repositories/participant_repository.dart';
import '../data/database/app_database.dart';
import 'database_provider.dart';
import 'current_event_provider.dart';

/// Provider für Participant Repository
final participantRepositoryProvider = Provider<ParticipantRepository>((ref) {
  final database = ref.watch(databaseProvider);
  return ParticipantRepository(database);
});

/// Provider für Teilnehmer-Liste des aktuellen Events
final participantsProvider = StreamProvider<List<Participant>>((ref) {
  final repository = ref.watch(participantRepositoryProvider);
  final eventId = ref.watch(currentEventIdProvider);

  if (eventId == null) {
    return Stream.value([]);
  }

  return repository.watchParticipantsByEvent(eventId);
});

/// Provider für einzelnen Teilnehmer
final participantProvider =
    StreamProvider.family<Participant?, int>((ref, participantId) {
  final repository = ref.watch(participantRepositoryProvider);
  return repository.watchParticipantById(participantId);
});

/// Provider für Teilnehmer-Anzahl
final participantCountProvider = FutureProvider<int>((ref) async {
  final repository = ref.watch(participantRepositoryProvider);
  final eventId = ref.watch(currentEventIdProvider);

  if (eventId == null) {
    return 0;
  }

  return repository.getParticipantCount(eventId);
});
