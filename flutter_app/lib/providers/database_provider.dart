import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/database/app_database.dart';

/// Provider für die Datenbank-Instanz
///
/// Singleton-Instanz der Datenbank, die in der gesamten App verwendet wird
final databaseProvider = Provider<AppDatabase>((ref) {
  final database = AppDatabase();

  // Cleanup when provider is disposed
  ref.onDispose(() {
    database.close();
  });

  return database;
});
