import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../data/repositories/ruleset_repository.dart';
import '../../providers/ruleset_provider.dart';
import '../../providers/current_event_provider.dart';

class RulesetFormScreen extends ConsumerStatefulWidget {
  final int? rulesetId;

  const RulesetFormScreen({super.key, this.rulesetId});

  @override
  ConsumerState<RulesetFormScreen> createState() => _RulesetFormScreenState();
}

class _RulesetFormScreenState extends ConsumerState<RulesetFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _yamlController = TextEditingController();

  DateTime _selectedDate = DateTime.now();
  bool _isLoading = false;
  bool _isDeleting = false;
  String? _yamlError;
  Map<String, dynamic>? _parsedData;

  @override
  void initState() {
    super.initState();
    if (widget.rulesetId != null) {
      _loadRuleset();
    } else {
      // Load default template for new rulesets
      final repository = ref.read(rulesetRepositoryProvider);
      _yamlController.text = repository.getDefaultRulesetTemplate();
      _validateYaml();
    }
  }

  Future<void> _loadRuleset() async {
    final ruleset = await ref.read(rulesetByIdProvider(widget.rulesetId!).future);
    if (ruleset != null && mounted) {
      setState(() {
        _nameController.text = ruleset.name;
        _descriptionController.text = ruleset.description ?? '';
        _yamlController.text = ruleset.yamlContent;
        _selectedDate = ruleset.validFrom;
      });
      _validateYaml();
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _yamlController.dispose();
    super.dispose();
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime(2000),
      lastDate: DateTime(2100),
      locale: const Locale('de', 'DE'),
    );

    if (picked != null && picked != _selectedDate) {
      setState(() {
        _selectedDate = picked;
      });
    }
  }

  void _validateYaml() {
    setState(() {
      _yamlError = null;
      _parsedData = null;
    });

    try {
      final repository = ref.read(rulesetRepositoryProvider);
      _parsedData = repository.parseRulesetYaml(_yamlController.text);
    } catch (e) {
      setState(() {
        _yamlError = e.toString();
      });
    }
  }

  Future<void> _saveRuleset() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    // Validate YAML before saving
    _validateYaml();
    if (_yamlError != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('YAML-Fehler: $_yamlError'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    final currentEvent = ref.read(currentEventProvider);
    if (currentEvent == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Keine Veranstaltung ausgewählt')),
        );
      }
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final repository = ref.read(rulesetRepositoryProvider);

      if (widget.rulesetId == null) {
        // Create new ruleset
        await repository.createRuleset(
          eventId: currentEvent.id,
          name: _nameController.text,
          yamlContent: _yamlController.text,
          validFrom: _selectedDate,
          description: _descriptionController.text.isEmpty ? null : _descriptionController.text,
        );
      } else {
        // Update existing ruleset
        await repository.updateRuleset(
          id: widget.rulesetId!,
          name: _nameController.text,
          yamlContent: _yamlController.text,
          validFrom: _selectedDate,
          description: _descriptionController.text.isEmpty ? null : _descriptionController.text,
        );
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(widget.rulesetId == null
                ? 'Regelwerk erfolgreich erstellt'
                : 'Regelwerk erfolgreich aktualisiert'),
          ),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Fehler beim Speichern: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _deleteRuleset() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Regelwerk löschen'),
        content: const Text(
          'Möchten Sie dieses Regelwerk wirklich löschen?\n\n'
          'Achtung: Dies kann Auswirkungen auf bestehende Teilnehmer haben!',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Abbrechen'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            style: FilledButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('Löschen'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    setState(() {
      _isDeleting = true;
    });

    try {
      final repository = ref.read(rulesetRepositoryProvider);
      await repository.deleteRuleset(widget.rulesetId!);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Regelwerk erfolgreich gelöscht')),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Fehler beim Löschen: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isDeleting = false;
        });
      }
    }
  }

  Future<void> _loadTemplate() async {
    final repository = ref.read(rulesetRepositoryProvider);
    final template = repository.getDefaultRulesetTemplate();

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Vorlage laden'),
        content: const Text(
          'Möchten Sie die Standardvorlage laden?\n\n'
          'Dies überschreibt den aktuellen YAML-Inhalt.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Abbrechen'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Vorlage laden'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      setState(() {
        _yamlController.text = template;
      });
      _validateYaml();
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEditing = widget.rulesetId != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEditing ? 'Regelwerk bearbeiten' : 'Neues Regelwerk'),
        actions: [
          if (isEditing)
            IconButton(
              icon: _isDeleting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.delete),
              onPressed: _isDeleting ? null : _deleteRuleset,
              tooltip: 'Löschen',
            ),
          IconButton(
            icon: const Icon(Icons.help_outline),
            onPressed: () => _showHelp(),
            tooltip: 'Hilfe',
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Basic Information
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Grundinformationen',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _nameController,
                      decoration: const InputDecoration(
                        labelText: 'Name *',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.label),
                        helperText: 'z.B. "Sommerfreizeit 2024"',
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Bitte geben Sie einen Namen ein';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    InkWell(
                      onTap: _selectDate,
                      borderRadius: BorderRadius.circular(8),
                      child: InputDecorator(
                        decoration: const InputDecoration(
                          labelText: 'Gültig ab *',
                          border: OutlineInputBorder(),
                          prefixIcon: Icon(Icons.calendar_today),
                          helperText: 'Ab diesem Datum wird das Regelwerk aktiv',
                        ),
                        child: Text(
                          DateFormat('dd.MM.yyyy', 'de_DE').format(_selectedDate),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _descriptionController,
                      decoration: const InputDecoration(
                        labelText: 'Beschreibung',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.description),
                        helperText: 'Optional: Zusätzliche Informationen',
                      ),
                      maxLines: 3,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // YAML Editor
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          'YAML-Konfiguration',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const Spacer(),
                        TextButton.icon(
                          onPressed: _loadTemplate,
                          icon: const Icon(Icons.file_copy, size: 16),
                          label: const Text('Vorlage'),
                        ),
                        const SizedBox(width: 8),
                        FilledButton.icon(
                          onPressed: _validateYaml,
                          icon: const Icon(Icons.check_circle, size: 16),
                          label: const Text('Prüfen'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _yamlController,
                      decoration: InputDecoration(
                        border: const OutlineInputBorder(),
                        hintText: 'YAML-Inhalt hier eingeben...',
                        errorText: _yamlError,
                        errorMaxLines: 3,
                      ),
                      maxLines: 20,
                      style: const TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 12,
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Bitte geben Sie YAML-Inhalt ein';
                        }
                        return null;
                      },
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Validation Status
            if (_yamlError == null && _parsedData != null)
              Card(
                color: Colors.green[50],
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.check_circle, color: Colors.green),
                          const SizedBox(width: 8),
                          Text(
                            'YAML ist gültig',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                  color: Colors.green[900],
                                  fontWeight: FontWeight.bold,
                                ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      _buildParsedDataSummary(_parsedData!),
                    ],
                  ),
                ),
              ),
            if (_yamlError != null)
              Card(
                color: Colors.red[50],
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.error, color: Colors.red),
                          const SizedBox(width: 8),
                          Text(
                            'YAML-Fehler',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                  color: Colors.red[900],
                                  fontWeight: FontWeight.bold,
                                ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _yamlError!,
                        style: TextStyle(
                          color: Colors.red[900],
                          fontFamily: 'monospace',
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 24),

            // Save button
            FilledButton.icon(
              onPressed: _isLoading ? null : _saveRuleset,
              icon: _isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.save),
              label: Text(isEditing ? 'Aktualisieren' : 'Speichern'),
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.all(16),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildParsedDataSummary(Map<String, dynamic> data) {
    final ageGroups = data['age_groups'] as List;
    final roleDiscounts = data['role_discounts'] as List;
    final hasFamilyDiscount = data['family_discount'] != null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('📊 ${ageGroups.length} Altersgruppen definiert'),
        Text('💼 ${roleDiscounts.length} Rollenrabatte definiert'),
        if (hasFamilyDiscount) const Text('👨‍👩‍👧‍👦 Familienrabatt aktiviert'),
      ],
    );
  }

  void _showHelp() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('YAML-Hilfe'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Ein Regelwerk definiert Preise und Rabatte für Ihre Veranstaltung.\n\n'
                'YAML-Struktur:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Text(
                  'age_groups:\n'
                  '  - name: "Kinder"\n'
                  '    min_age: 0\n'
                  '    max_age: 12\n'
                  '    base_price: 150.00\n\n'
                  'role_discounts:\n'
                  '  - role_name: "Mitarbeiter"\n'
                  '    discount_percent: 50.0\n\n'
                  'family_discount:\n'
                  '  min_children: 2\n'
                  '  discount_percent_per_child:\n'
                  '    - children_count: 2\n'
                  '      discount_percent: 10.0',
                  style: TextStyle(
                    fontFamily: 'monospace',
                    fontSize: 11,
                  ),
                ),
              ),
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
}
