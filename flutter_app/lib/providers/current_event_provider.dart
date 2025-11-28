import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/database/app_database.dart';

/// Provider für das aktuell ausgewählte Event
///
/// Entspricht der Session-basierten Event-Auswahl in der Web-App
class CurrentEventNotifier extends StateNotifier<Event?> {
  CurrentEventNotifier() : super(null);

  void selectEvent(Event event) {
    state = event;
  }

  void clearEvent() {
    state = null;
  }

  int? get eventId => state?.id;
}

final currentEventProvider =
    StateNotifierProvider<CurrentEventNotifier, Event?>((ref) {
  return CurrentEventNotifier();
});

/// Helper Provider um nur die Event-ID zu bekommen
final currentEventIdProvider = Provider<int?>((ref) {
  final event = ref.watch(currentEventProvider);
  return event?.id;
});
