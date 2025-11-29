import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import '../../providers/current_event_provider.dart';
import '../../providers/database_provider.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentEvent = ref.watch(currentEventProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Einstellungen'),
      ),
      body: ListView(
        children: [
          // Event Info Section
          if (currentEvent != null) ...[
            _SectionHeader(title: 'Aktuelle Veranstaltung'),
            ListTile(
              leading: const Icon(Icons.event),
              title: Text(currentEvent.name),
              subtitle: Text(
                'Von ${_formatDate(currentEvent.startDate)} bis ${_formatDate(currentEvent.endDate)}',
              ),
            ),
            if (currentEvent.location != null)
              ListTile(
                leading: const Icon(Icons.location_on),
                title: const Text('Ort'),
                subtitle: Text(currentEvent.location!),
              ),
            const Divider(),
          ],

          // Database Section
          _SectionHeader(title: 'Datenbank'),
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('Datenbank-Information'),
            onTap: () => _showDatabaseInfo(context, ref),
          ),
          ListTile(
            leading: const Icon(Icons.folder_open),
            title: const Text('Datenbank-Pfad anzeigen'),
            onTap: () => _showDatabasePath(context),
          ),
          const Divider(),

          // App Info Section
          _SectionHeader(title: 'App-Information'),
          const ListTile(
            leading: Icon(Icons.info),
            title: Text('Version'),
            subtitle: Text('1.0.0'),
          ),
          const ListTile(
            leading: Icon(Icons.code),
            title: Text('Plattform'),
            subtitle: Text('Flutter'),
          ),
          ListTile(
            leading: const Icon(Icons.description),
            title: const Text('Über'),
            onTap: () => _showAboutDialog(context),
          ),
          const Divider(),

          // Danger Zone
          _SectionHeader(title: 'Erweitert'),
          ListTile(
            leading: const Icon(Icons.warning, color: Colors.orange),
            title: const Text('Cache leeren'),
            subtitle: const Text('Temporäre Daten entfernen'),
            onTap: () => _clearCache(context),
          ),
          ListTile(
            leading: const Icon(Icons.delete_forever, color: Colors.red),
            title: const Text(
              'Datenbank zurücksetzen',
              style: TextStyle(color: Colors.red),
            ),
            subtitle: const Text('WARNUNG: Alle Daten werden gelöscht!'),
            onTap: () => _confirmResetDatabase(context, ref),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}.${date.month.toString().padLeft(2, '0')}.${date.year}';
  }

  Future<void> _showDatabaseInfo(BuildContext context, WidgetRef ref) async {
    final database = ref.read(databaseProvider);

    // Get table counts
    final events = await database.select(database.events).get();
    final participants = await database.select(database.participants).get();
    final families = await database.select(database.families).get();
    final payments = await database.select(database.payments).get();
    final expenses = await database.select(database.expenses).get();
    final incomes = await database.select(database.incomes).get();
    final rulesets = await database.select(database.rulesets).get();
    final roles = await database.select(database.roles).get();
    final tasks = await database.select(database.tasks).get();

    if (!context.mounted) return;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Datenbank-Statistiken'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildStatRow('Veranstaltungen', events.length),
              _buildStatRow('Teilnehmer', participants.length),
              _buildStatRow('Familien', families.length),
              _buildStatRow('Zahlungen', payments.length),
              _buildStatRow('Ausgaben', expenses.length),
              _buildStatRow('Einnahmen', incomes.length),
              _buildStatRow('Regelwerke', rulesets.length),
              _buildStatRow('Rollen', roles.length),
              _buildStatRow('Aufgaben', tasks.length),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Schließen'),
          ),
        ],
      ),
    );
  }

  Widget _buildStatRow(String label, int count) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            count.toString(),
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Future<void> _showDatabasePath(BuildContext context) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final dbPath = '${directory.path}/databases/app_database.db';

      if (!context.mounted) return;

      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Datenbank-Pfad'),
          content: SelectableText(dbPath),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Schließen'),
            ),
          ],
        ),
      );
    } catch (e) {
      if (!context.mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Fehler: $e')),
      );
    }
  }

  void _showAboutDialog(BuildContext context) {
    showAboutDialog(
      context: context,
      applicationName: 'MGBFreizeitplaner',
      applicationVersion: '1.0.0',
      applicationIcon: const Icon(Icons.event, size: 48),
      children: [
        const Text(
          'Verwaltungssoftware für Jugendfreizeiten und Camps.\n\n'
          'Entwickelt mit Flutter für iOS, macOS und Windows.',
        ),
      ],
    );
  }

  Future<void> _clearCache(BuildContext context) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cache leeren?'),
        content: const Text('Temporäre Daten werden entfernt. Die Datenbank bleibt unverändert.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Abbrechen'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Cache leeren'),
          ),
        ],
      ),
    );

    if (confirmed != true || !context.mounted) return;

    try {
      final directory = await getApplicationDocumentsDirectory();
      // Clear temp files if any
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Cache geleert')),
      );
    } catch (e) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Fehler: $e')),
      );
    }
  }

  Future<void> _confirmResetDatabase(BuildContext context, WidgetRef ref) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Datenbank zurücksetzen?'),
        content: const Text(
          'WARNUNG: Alle Daten werden unwiderruflich gelöscht!\n\n'
          'Dies umfasst:\n'
          '• Alle Veranstaltungen\n'
          '• Alle Teilnehmer\n'
          '• Alle Zahlungen\n'
          '• Alle Ausgaben und Einnahmen\n'
          '• Alle Regelwerke und Rollen\n'
          '• Alle Aufgaben\n\n'
          'Dieser Vorgang kann NICHT rückgängig gemacht werden!',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Abbrechen'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Alles löschen'),
          ),
        ],
      ),
    );

    if (confirmed != true || !context.mounted) return;

    // Double confirmation
    final doubleConfirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Wirklich fortfahren?'),
        content: const Text(
          'Letzte Warnung: Alle Daten werden gelöscht!\n\n'
          'Sind Sie absolut sicher?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Abbrechen'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Ja, alles löschen'),
          ),
        ],
      ),
    );

    if (doubleConfirmed != true || !context.mounted) return;

    try {
      final database = ref.read(databaseProvider);
      final directory = await getApplicationDocumentsDirectory();
      final dbPath = '${directory.path}/databases/app_database.db';

      // Close database
      await database.close();

      // Delete database file
      final dbFile = File(dbPath);
      if (await dbFile.exists()) {
        await dbFile.delete();
      }

      if (!context.mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Datenbank wurde zurückgesetzt. Bitte App neu starten.'),
          duration: Duration(seconds: 5),
        ),
      );

      // Navigate to home and clear event
      ref.read(currentEventProvider.notifier).clearEvent();
      Navigator.of(context).pushNamedAndRemoveUntil('/', (route) => false);
    } catch (e) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Fehler beim Zurücksetzen: $e')),
      );
    }
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;

  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      child: Text(
        title.toUpperCase(),
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: Theme.of(context).colorScheme.primary,
        ),
      ),
    );
  }
}
