import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/repositories/payment_repository.dart';
import '../data/database/app_database.dart';
import 'database_provider.dart';
import 'current_event_provider.dart';

/// Provider für Payment Repository
final paymentRepositoryProvider = Provider<PaymentRepository>((ref) {
  final database = ref.watch(databaseProvider);
  return PaymentRepository(database);
});

/// Provider für Zahlungen-Liste des aktuellen Events
final paymentsProvider = StreamProvider<List<Payment>>((ref) {
  final repository = ref.watch(paymentRepositoryProvider);
  final eventId = ref.watch(currentEventIdProvider);

  if (eventId == null) {
    return Stream.value([]);
  }

  return repository.watchPaymentsByEvent(eventId);
});

/// Provider für Gesamtsumme der Zahlungen
final totalPaymentsProvider = FutureProvider<double>((ref) async {
  final repository = ref.watch(paymentRepositoryProvider);
  final eventId = ref.watch(currentEventIdProvider);

  if (eventId == null) {
    return 0.0;
  }

  return repository.getTotalPayments(eventId);
});
