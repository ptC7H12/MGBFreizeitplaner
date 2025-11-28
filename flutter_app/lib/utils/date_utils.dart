import 'package:intl/intl.dart';

/// Datum-Utilities für deutsche Formatierung
class AppDateUtils {
  static final DateFormat _germanDateFormat = DateFormat('dd.MM.yyyy', 'de_DE');
  static final DateFormat _germanDateTimeFormat =
      DateFormat('dd.MM.yyyy HH:mm', 'de_DE');
  static final DateFormat _isoDateFormat = DateFormat('yyyy-MM-dd');

  /// Formatiert Datum zu deutschem Format: 01.01.2025
  static String formatGerman(DateTime date) {
    return _germanDateFormat.format(date);
  }

  /// Formatiert Datum+Zeit zu deutschem Format: 01.01.2025 14:30
  static String formatGermanDateTime(DateTime dateTime) {
    return _germanDateTimeFormat.format(dateTime);
  }

  /// Formatiert Datum zu ISO-Format: 2025-01-01
  static String formatISO(DateTime date) {
    return _isoDateFormat.format(date);
  }

  /// Berechnet Alter basierend auf Geburtsdatum
  static int calculateAge(DateTime birthDate, {DateTime? referenceDate}) {
    final reference = referenceDate ?? DateTime.now();
    int age = reference.year - birthDate.year;

    if (reference.month < birthDate.month ||
        (reference.month == birthDate.month && reference.day < birthDate.day)) {
      age--;
    }

    return age;
  }

  /// Berechnet Alter zum Event-Start (für Preisberechnung)
  static int calculateAgeAtEventStart(DateTime birthDate, DateTime eventStart) {
    return calculateAge(birthDate, referenceDate: eventStart);
  }

  /// Prüft ob Datum in Vergangenheit liegt
  static bool isInPast(DateTime date) {
    return date.isBefore(DateTime.now());
  }

  /// Prüft ob Datum in Zukunft liegt
  static bool isInFuture(DateTime date) {
    return date.isAfter(DateTime.now());
  }

  /// Erstellt DateTime für "heute"
  static DateTime today() {
    final now = DateTime.now();
    return DateTime(now.year, now.month, now.day);
  }

  /// Prüft ob zwei Datums-Objekte den gleichen Tag repräsentieren
  static bool isSameDay(DateTime a, DateTime b) {
    return a.year == b.year && a.month == b.month && a.day == b.day;
  }

  /// Gibt den ersten Tag des Monats zurück
  static DateTime firstDayOfMonth(DateTime date) {
    return DateTime(date.year, date.month, 1);
  }

  /// Gibt den letzten Tag des Monats zurück
  static DateTime lastDayOfMonth(DateTime date) {
    return DateTime(date.year, date.month + 1, 0);
  }

  /// Parst deutsches Datum (dd.MM.yyyy) zu DateTime
  static DateTime? parseGerman(String dateString) {
    try {
      return _germanDateFormat.parse(dateString);
    } catch (e) {
      return null;
    }
  }

  /// Parst ISO-Datum (yyyy-MM-dd) zu DateTime
  static DateTime? parseISO(String dateString) {
    try {
      return _isoDateFormat.parse(dateString);
    } catch (e) {
      return null;
    }
  }
}
