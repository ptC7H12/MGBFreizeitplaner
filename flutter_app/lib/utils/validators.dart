/// Form-Validatoren
///
/// Portiert von app/utils/validators.py
class Validators {
  /// Email-Validierung (basic)
  static String? email(String? value) {
    if (value == null || value.isEmpty) {
      return null; // Leer ist OK (wird mit required kombiniert)
    }

    final emailRegex = RegExp(
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    );

    if (!emailRegex.hasMatch(value)) {
      return 'Bitte gültige E-Mail-Adresse eingeben';
    }

    return null;
  }

  /// IBAN-Validierung (Deutschland)
  static String? iban(String? value) {
    if (value == null || value.isEmpty) {
      return null;
    }

    // Leerzeichen entfernen
    final cleanedIban = value.replaceAll(' ', '').toUpperCase();

    // Deutsche IBAN: DE + 2 Prüfziffern + 18 Ziffern = 22 Zeichen
    if (!cleanedIban.startsWith('DE')) {
      return 'IBAN muss mit DE beginnen';
    }

    if (cleanedIban.length != 22) {
      return 'Deutsche IBAN muss 22 Zeichen haben (DE + 20 Ziffern)';
    }

    final ibanRegex = RegExp(r'^DE\d{20}$');
    if (!ibanRegex.hasMatch(cleanedIban)) {
      return 'Ungültiges IBAN-Format';
    }

    // TODO: Mod-97-Prüfsumme validieren (optional)

    return null;
  }

  /// BIC-Validierung (8 oder 11 Zeichen)
  static String? bic(String? value) {
    if (value == null || value.isEmpty) {
      return null;
    }

    final cleanedBic = value.replaceAll(' ', '').toUpperCase();

    // BIC: 8 oder 11 alphanumerische Zeichen
    final bicRegex = RegExp(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$');

    if (!bicRegex.hasMatch(cleanedBic)) {
      return 'Ungültiges BIC-Format (8 oder 11 Zeichen)';
    }

    return null;
  }

  /// Postleitzahl-Validierung (Deutschland: 5 Ziffern)
  static String? postalCode(String? value) {
    if (value == null || value.isEmpty) {
      return null;
    }

    final postalCodeRegex = RegExp(r'^\d{5}$');

    if (!postalCodeRegex.hasMatch(value)) {
      return 'Bitte 5-stellige Postleitzahl eingeben';
    }

    return null;
  }

  /// Telefonnummer-Validierung (flexibel)
  static String? phone(String? value) {
    if (value == null || value.isEmpty) {
      return null;
    }

    // Entferne alle nicht-Ziffern außer + am Anfang
    final cleaned = value.replaceAll(RegExp(r'[^\d+]'), '');

    if (cleaned.isEmpty) {
      return 'Bitte gültige Telefonnummer eingeben';
    }

    // Mindestens 3 Ziffern (flexibel für internationale Nummern)
    if (cleaned.replaceAll('+', '').length < 3) {
      return 'Telefonnummer zu kurz';
    }

    return null;
  }

  /// Pflichtfeld-Validierung
  static String? required(String? value, {String? fieldName}) {
    if (value == null || value.trim().isEmpty) {
      return fieldName != null
          ? '$fieldName ist erforderlich'
          : 'Dieses Feld ist erforderlich';
    }
    return null;
  }

  /// Min-Länge Validierung
  static String? minLength(String? value, int min, {String? fieldName}) {
    if (value == null || value.isEmpty) {
      return null; // Wird mit required kombiniert
    }

    if (value.length < min) {
      return fieldName != null
          ? '$fieldName muss mindestens $min Zeichen haben'
          : 'Mindestens $min Zeichen erforderlich';
    }

    return null;
  }

  /// Max-Länge Validierung
  static String? maxLength(String? value, int max, {String? fieldName}) {
    if (value == null || value.isEmpty) {
      return null;
    }

    if (value.length > max) {
      return fieldName != null
          ? '$fieldName darf maximal $max Zeichen haben'
          : 'Maximal $max Zeichen erlaubt';
    }

    return null;
  }

  /// Betrag-Validierung (positiv)
  static String? positiveAmount(String? value, {String? fieldName}) {
    if (value == null || value.isEmpty) {
      return null;
    }

    final amount = double.tryParse(value.replaceAll(',', '.'));

    if (amount == null) {
      return 'Bitte gültigen Betrag eingeben';
    }

    if (amount <= 0) {
      return fieldName != null
          ? '$fieldName muss größer als 0 sein'
          : 'Betrag muss größer als 0 sein';
    }

    return null;
  }

  /// Prozent-Validierung (0-100)
  static String? percentage(String? value, {String? fieldName}) {
    if (value == null || value.isEmpty) {
      return null;
    }

    final percent = double.tryParse(value.replaceAll(',', '.'));

    if (percent == null) {
      return 'Bitte gültige Prozentzahl eingeben';
    }

    if (percent < 0 || percent > 100) {
      return 'Prozent muss zwischen 0 und 100 liegen';
    }

    return null;
  }

  /// Geburtsdatum-Validierung (nicht in der Zukunft, realistisch)
  static String? birthDate(DateTime? value) {
    if (value == null) {
      return 'Bitte Geburtsdatum auswählen';
    }

    final now = DateTime.now();

    if (value.isAfter(now)) {
      return 'Geburtsdatum darf nicht in der Zukunft liegen';
    }

    // Realistisches Alter: 0-120 Jahre
    final age = now.year - value.year;
    if (age > 120) {
      return 'Geburtsdatum unrealistisch (über 120 Jahre alt)';
    }

    return null;
  }

  /// Kombiniere mehrere Validatoren
  static String? combine(
    String? value,
    List<String? Function(String?)> validators,
  ) {
    for (var validator in validators) {
      final error = validator(value);
      if (error != null) {
        return error;
      }
    }
    return null;
  }
}
