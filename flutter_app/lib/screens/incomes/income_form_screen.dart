import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../data/repositories/income_repository.dart';
import '../../providers/income_provider.dart';
import '../../providers/current_event_provider.dart';

class IncomeFormScreen extends ConsumerStatefulWidget {
  final int? incomeId;

  const IncomeFormScreen({super.key, this.incomeId});

  @override
  ConsumerState<IncomeFormScreen> createState() => _IncomeFormScreenState();
}

class _IncomeFormScreenState extends ConsumerState<IncomeFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _referenceNumberController = TextEditingController();
  final _notesController = TextEditingController();

  String _selectedSource = 'Teilnehmerbeitrag';
  DateTime _selectedDate = DateTime.now();
  String? _selectedPaymentMethod;

  bool _isLoading = false;
  bool _isDeleting = false;

  final List<String> _sources = [
    'Teilnehmerbeitrag',
    'Spende',
    'Zuschuss',
    'Sponsoring',
    'Merchandise',
    'Sonstiges',
  ];

  final List<String> _paymentMethods = [
    'Barzahlung',
    'Überweisung',
    'Lastschrift',
    'Kreditkarte',
    'PayPal',
    'Sonstige',
  ];

  @override
  void initState() {
    super.initState();
    if (widget.incomeId != null) {
      _loadIncome();
    }
  }

  Future<void> _loadIncome() async {
    final income = await ref.read(incomeByIdProvider(widget.incomeId!).future);
    if (income != null && mounted) {
      setState(() {
        _selectedSource = income.source;
        _amountController.text = income.amount.toStringAsFixed(2);
        _selectedDate = income.incomeDate;
        _descriptionController.text = income.description ?? '';
        _referenceNumberController.text = income.referenceNumber ?? '';
        _selectedPaymentMethod = income.paymentMethod;
        _notesController.text = income.notes ?? '';
      });
    }
  }

  @override
  void dispose() {
    _amountController.dispose();
    _descriptionController.dispose();
    _referenceNumberController.dispose();
    _notesController.dispose();
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

  Future<void> _saveIncome() async {
    if (!_formKey.currentState!.validate()) {
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
      final repository = ref.read(incomeRepositoryProvider);
      final amount = double.parse(_amountController.text.replaceAll(',', '.'));

      if (widget.incomeId == null) {
        // Create new income
        await repository.createIncome(
          eventId: currentEvent.id,
          source: _selectedSource,
          amount: amount,
          incomeDate: _selectedDate,
          description: _descriptionController.text.isEmpty ? null : _descriptionController.text,
          referenceNumber: _referenceNumberController.text.isEmpty ? null : _referenceNumberController.text,
          paymentMethod: _selectedPaymentMethod,
          notes: _notesController.text.isEmpty ? null : _notesController.text,
        );
      } else {
        // Update existing income
        await repository.updateIncome(
          id: widget.incomeId!,
          source: _selectedSource,
          amount: amount,
          incomeDate: _selectedDate,
          description: _descriptionController.text.isEmpty ? null : _descriptionController.text,
          referenceNumber: _referenceNumberController.text.isEmpty ? null : _referenceNumberController.text,
          paymentMethod: _selectedPaymentMethod,
          notes: _notesController.text.isEmpty ? null : _notesController.text,
        );
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(widget.incomeId == null
                ? 'Einnahme erfolgreich erstellt'
                : 'Einnahme erfolgreich aktualisiert'),
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

  Future<void> _deleteIncome() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Einnahme löschen'),
        content: const Text('Möchten Sie diese Einnahme wirklich löschen?'),
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
      final repository = ref.read(incomeRepositoryProvider);
      await repository.deleteIncome(widget.incomeId!);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Einnahme erfolgreich gelöscht')),
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

  @override
  Widget build(BuildContext context) {
    final isEditing = widget.incomeId != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEditing ? 'Einnahme bearbeiten' : 'Neue Einnahme'),
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
              onPressed: _isDeleting ? null : _deleteIncome,
              tooltip: 'Löschen',
            ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Source selection
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Quelle',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      value: _selectedSource,
                      decoration: const InputDecoration(
                        labelText: 'Einnahmequelle *',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.source),
                      ),
                      items: _sources.map((source) {
                        return DropdownMenuItem(
                          value: source,
                          child: Text(source),
                        );
                      }).toList(),
                      onChanged: (value) {
                        if (value != null) {
                          setState(() {
                            _selectedSource = value;
                          });
                        }
                      },
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Bitte wählen Sie eine Quelle';
                        }
                        return null;
                      },
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Amount and Date
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Betrag und Datum',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _amountController,
                      decoration: const InputDecoration(
                        labelText: 'Betrag (€) *',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.euro),
                        helperText: 'z.B. 150.50 oder 150,50',
                      ),
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      inputFormatters: [
                        FilteringTextInputFormatter.allow(RegExp(r'[\d,.]')),
                      ],
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Bitte geben Sie einen Betrag ein';
                        }
                        final amount = double.tryParse(value.replaceAll(',', '.'));
                        if (amount == null || amount <= 0) {
                          return 'Bitte geben Sie einen gültigen Betrag ein';
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
                          labelText: 'Datum *',
                          border: OutlineInputBorder(),
                          prefixIcon: Icon(Icons.calendar_today),
                        ),
                        child: Text(
                          DateFormat('dd.MM.yyyy', 'de_DE').format(_selectedDate),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Description
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Details',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _descriptionController,
                      decoration: const InputDecoration(
                        labelText: 'Beschreibung',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.description),
                        helperText: 'Kurze Beschreibung der Einnahme',
                      ),
                      maxLines: 3,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Payment details
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Zahlungsdetails',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      value: _selectedPaymentMethod,
                      decoration: const InputDecoration(
                        labelText: 'Zahlungsmethode',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.payment),
                      ),
                      items: [
                        const DropdownMenuItem(
                          value: null,
                          child: Text('Keine Angabe'),
                        ),
                        ..._paymentMethods.map((method) {
                          return DropdownMenuItem(
                            value: method,
                            child: Text(method),
                          );
                        }),
                      ],
                      onChanged: (value) {
                        setState(() {
                          _selectedPaymentMethod = value;
                        });
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _referenceNumberController,
                      decoration: const InputDecoration(
                        labelText: 'Referenznummer',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.tag),
                        helperText: 'Transaktions- oder Referenznummer',
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Notes
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Notizen',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _notesController,
                      decoration: const InputDecoration(
                        labelText: 'Notizen',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.note),
                        helperText: 'Zusätzliche Anmerkungen',
                      ),
                      maxLines: 4,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Save button
            FilledButton.icon(
              onPressed: _isLoading ? null : _saveIncome,
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
}
