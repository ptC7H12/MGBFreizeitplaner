import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../data/repositories/expense_repository.dart';
import '../../providers/expense_provider.dart';
import '../../providers/current_event_provider.dart';

class ExpenseFormScreen extends ConsumerStatefulWidget {
  final int? expenseId;

  const ExpenseFormScreen({super.key, this.expenseId});

  @override
  ConsumerState<ExpenseFormScreen> createState() => _ExpenseFormScreenState();
}

class _ExpenseFormScreenState extends ConsumerState<ExpenseFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _vendorController = TextEditingController();
  final _receiptNumberController = TextEditingController();
  final _notesController = TextEditingController();

  String _selectedCategory = 'Verpflegung';
  DateTime _selectedDate = DateTime.now();
  String? _selectedPaymentMethod;

  bool _isLoading = false;
  bool _isDeleting = false;

  final List<String> _categories = [
    'Verpflegung',
    'Unterkunft',
    'Transport',
    'Material',
    'Personal',
    'Versicherung',
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
    if (widget.expenseId != null) {
      _loadExpense();
    }
  }

  Future<void> _loadExpense() async {
    final expense = await ref.read(expenseByIdProvider(widget.expenseId!).future);
    if (expense != null && mounted) {
      setState(() {
        _selectedCategory = expense.category;
        _amountController.text = expense.amount.toStringAsFixed(2);
        _selectedDate = expense.expenseDate;
        _descriptionController.text = expense.description ?? '';
        _vendorController.text = expense.vendor ?? '';
        _receiptNumberController.text = expense.receiptNumber ?? '';
        _selectedPaymentMethod = expense.paymentMethod;
        _notesController.text = expense.notes ?? '';
      });
    }
  }

  @override
  void dispose() {
    _amountController.dispose();
    _descriptionController.dispose();
    _vendorController.dispose();
    _receiptNumberController.dispose();
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

  Future<void> _saveExpense() async {
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
      final repository = ref.read(expenseRepositoryProvider);
      final amount = double.parse(_amountController.text.replaceAll(',', '.'));

      if (widget.expenseId == null) {
        // Create new expense
        await repository.createExpense(
          eventId: currentEvent.id,
          category: _selectedCategory,
          amount: amount,
          expenseDate: _selectedDate,
          description: _descriptionController.text.isEmpty ? null : _descriptionController.text,
          vendor: _vendorController.text.isEmpty ? null : _vendorController.text,
          receiptNumber: _receiptNumberController.text.isEmpty ? null : _receiptNumberController.text,
          paymentMethod: _selectedPaymentMethod,
          notes: _notesController.text.isEmpty ? null : _notesController.text,
        );
      } else {
        // Update existing expense
        await repository.updateExpense(
          id: widget.expenseId!,
          category: _selectedCategory,
          amount: amount,
          expenseDate: _selectedDate,
          description: _descriptionController.text.isEmpty ? null : _descriptionController.text,
          vendor: _vendorController.text.isEmpty ? null : _vendorController.text,
          receiptNumber: _receiptNumberController.text.isEmpty ? null : _receiptNumberController.text,
          paymentMethod: _selectedPaymentMethod,
          notes: _notesController.text.isEmpty ? null : _notesController.text,
        );
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(widget.expenseId == null
                ? 'Ausgabe erfolgreich erstellt'
                : 'Ausgabe erfolgreich aktualisiert'),
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

  Future<void> _deleteExpense() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Ausgabe löschen'),
        content: const Text('Möchten Sie diese Ausgabe wirklich löschen?'),
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
      final repository = ref.read(expenseRepositoryProvider);
      await repository.deleteExpense(widget.expenseId!);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Ausgabe erfolgreich gelöscht')),
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
    final isEditing = widget.expenseId != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEditing ? 'Ausgabe bearbeiten' : 'Neue Ausgabe'),
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
              onPressed: _isDeleting ? null : _deleteExpense,
              tooltip: 'Löschen',
            ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Category selection
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Kategorie',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      value: _selectedCategory,
                      decoration: const InputDecoration(
                        labelText: 'Kategorie *',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.category),
                      ),
                      items: _categories.map((category) {
                        return DropdownMenuItem(
                          value: category,
                          child: Text(category),
                        );
                      }).toList(),
                      onChanged: (value) {
                        if (value != null) {
                          setState(() {
                            _selectedCategory = value;
                          });
                        }
                      },
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Bitte wählen Sie eine Kategorie';
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

            // Description and Vendor
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
                        helperText: 'Kurze Beschreibung der Ausgabe',
                      ),
                      maxLines: 3,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _vendorController,
                      decoration: const InputDecoration(
                        labelText: 'Anbieter/Lieferant',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.store),
                        helperText: 'z.B. Supermarkt, Hotel, etc.',
                      ),
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
                      controller: _receiptNumberController,
                      decoration: const InputDecoration(
                        labelText: 'Belegnummer',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.receipt),
                        helperText: 'Rechnungs- oder Belegnummer',
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
              onPressed: _isLoading ? null : _saveExpense,
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
