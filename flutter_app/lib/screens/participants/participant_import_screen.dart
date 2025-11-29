import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:path_provider/path_provider.dart';
import '../../providers/excel_import_provider.dart';
import '../../providers/current_event_provider.dart';
import '../../services/excel_import_service.dart';

class ParticipantImportScreen extends ConsumerStatefulWidget {
  const ParticipantImportScreen({super.key});

  @override
  ConsumerState<ParticipantImportScreen> createState() => _ParticipantImportScreenState();
}

class _ParticipantImportScreenState extends ConsumerState<ParticipantImportScreen> {
  String? _selectedFilePath;
  bool _isImporting = false;
  ExcelImportResult? _importResult;

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['xlsx', 'xls'],
    );

    if (result != null && result.files.single.path != null) {
      setState(() {
        _selectedFilePath = result.files.single.path;
        _importResult = null; // Reset previous result
      });
    }
  }

  Future<void> _downloadTemplate() async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final outputPath = '${directory.path}/teilnehmer_vorlage.xlsx';

      final service = ref.read(excelImportServiceProvider);
      final path = await service.generateImportTemplate(outputPath);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Vorlage gespeichert: $path'),
            action: SnackBarAction(
              label: 'Öffnen',
              onPressed: () {
                // TODO: Open file with default app
              },
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Fehler beim Erstellen der Vorlage: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _importFile() async {
    if (_selectedFilePath == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Bitte wählen Sie zuerst eine Datei aus')),
      );
      return;
    }

    final currentEvent = ref.read(currentEventProvider);
    if (currentEvent == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Keine Veranstaltung ausgewählt')),
      );
      return;
    }

    setState(() {
      _isImporting = true;
      _importResult = null;
    });

    try {
      final service = ref.read(excelImportServiceProvider);
      final result = await service.importParticipantsFromExcel(
        filePath: _selectedFilePath!,
        eventId: currentEvent.id,
      );

      setState(() {
        _importResult = result;
      });

      if (result.successCount > 0) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${result.successCount} Teilnehmer erfolgreich importiert'),
            backgroundColor: Colors.green,
          ),
        );
      }

      if (result.hasErrors) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Import abgeschlossen mit ${result.errorCount} Fehlern'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Fehler beim Import: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isImporting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Teilnehmer importieren'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Instructions Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.info_outline, color: Colors.blue),
                      const SizedBox(width: 8),
                      Text(
                        'Anleitung',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    '1. Laden Sie die Excel-Vorlage herunter\n'
                    '2. Füllen Sie die Teilnehmerdaten aus\n'
                    '3. Speichern Sie die Datei\n'
                    '4. Wählen Sie die Datei aus und starten Sie den Import\n\n'
                    'Pflichtfelder: Vorname, Nachname, Geburtsdatum',
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Download Template Button
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Schritt 1: Vorlage herunterladen',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 12),
                  FilledButton.icon(
                    onPressed: _downloadTemplate,
                    icon: const Icon(Icons.download),
                    label: const Text('Excel-Vorlage herunterladen'),
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.all(16),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // File Selection
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Schritt 2: Datei auswählen',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 12),
                  if (_selectedFilePath != null) ...[
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.green[50],
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.green[200]!),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.check_circle, color: Colors.green[700]),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Datei ausgewählt',
                                  style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                                Text(
                                  _selectedFilePath!.split(Platform.pathSeparator).last,
                                  style: const TextStyle(fontSize: 12),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ],
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.close),
                            onPressed: () {
                              setState(() {
                                _selectedFilePath = null;
                                _importResult = null;
                              });
                            },
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                  ],
                  FilledButton.icon(
                    onPressed: _pickFile,
                    icon: const Icon(Icons.folder_open),
                    label: Text(_selectedFilePath == null
                        ? 'Excel-Datei auswählen'
                        : 'Andere Datei auswählen'),
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.all(16),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Import Button
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Schritt 3: Import starten',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 12),
                  FilledButton.icon(
                    onPressed: _isImporting || _selectedFilePath == null ? null : _importFile,
                    icon: _isImporting
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.upload),
                    label: Text(_isImporting ? 'Importiere...' : 'Import starten'),
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.all(16),
                      backgroundColor: Colors.green,
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Import Results
          if (_importResult != null) ...[
            const SizedBox(height: 16),
            Card(
              color: _importResult!.hasErrors ? Colors.orange[50] : Colors.green[50],
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          _importResult!.hasErrors ? Icons.warning_amber : Icons.check_circle,
                          color: _importResult!.hasErrors ? Colors.orange[700] : Colors.green[700],
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Import-Ergebnis',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: _importResult!.hasErrors
                                    ? Colors.orange[900]
                                    : Colors.green[900],
                              ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text('Gesamtzeilen: ${_importResult!.totalRows}'),
                    Text('Erfolgreich: ${_importResult!.successCount}'),
                    if (_importResult!.hasErrors)
                      Text('Fehler: ${_importResult!.errorCount}'),
                    if (_importResult!.hasErrors) ...[
                      const SizedBox(height: 12),
                      const Divider(),
                      const SizedBox(height: 12),
                      Text(
                        'Fehlerdetails:',
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 8),
                      ..._importResult!.errors.take(10).map((error) => Padding(
                            padding: const EdgeInsets.only(bottom: 4),
                            child: Text(
                              '• $error',
                              style: const TextStyle(fontSize: 12),
                            ),
                          )),
                      if (_importResult!.errors.length > 10)
                        Text(
                          '... und ${_importResult!.errors.length - 10} weitere Fehler',
                          style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic),
                        ),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
