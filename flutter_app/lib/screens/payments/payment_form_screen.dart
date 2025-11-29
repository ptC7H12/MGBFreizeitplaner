import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/database/app_database.dart';
import '../../providers/payment_provider.dart';
import '../../providers/current_event_provider.dart';
import '../../providers/database_provider.dart';
import '../../providers/participant_provider.dart';
import '../../providers/family_provider.dart';
import '../../utils/validators.dart';
import '../../utils/date_utils.dart';

/// Zahlungs-Formular (Create/Edit)
class PaymentFormScreen extends ConsumerStatefulWidget {
  final int? paymentId; // null = Create, sonst Edit
  final int? preselectedParticipantId; // Vorauswahl Teilnehmer
  final int? preselectedFamilyId; // Vorauswahl Familie

  const PaymentFormScreen({
    super.key,
    this.paymentId,
    this.preselectedParticipantId,
    this.preselectedFamilyId,
  });

  @override
  ConsumerState<PaymentFormScreen> createState() => _PaymentFormScreenState();
}

class _PaymentFormScreenState extends ConsumerState<PaymentFormScreen> {
  final _formKey = GlobalKey<FormState>();

  // Form Controllers
  final _amountController = TextEditingController();
  final _notesController = TextEditingController();

  // Form State
  DateTime _paymentDate = DateTime.now();
  String? _paymentMethod;
  int? _selectedParticipantId;
  int? _selectedFamilyId;
  String _paymentType = 'participant'; // 'participant' oder 'family'

  bool _isLoading = false;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();

    // Vorauswahl setzen
    if (widget.preselectedParticipantId != null) {
      _selectedParticipantId = widget.preselectedParticipantId;
      _paymentType = 'participant';
    } else if (widget.preselectedFamilyId != null) {
      _selectedFamilyId = widget.preselectedFamilyId;
      _paymentType = 'family';
    }

    _initializeForm();
  }

  Future<void> _initializeForm() async {
    if (widget.paymentId != null) {
      // Edit-Modus: Lade Zahlungs-Daten
      final repository = ref.read(paymentRepositoryProvider);
      final payment = await repository.getPaymentById(widget.paymentId!);

      if (payment != null && mounted) {
        setState(() {
          _amountController.text = payment.amount.toStringAsFixed(2);
          _paymentDate = payment.paymentDate;
          _paymentMethod = payment.paymentMethod;
          _notesController.text = payment.notes ?? '';
          _selectedParticipantId = payment.participantId;
          _selectedFamilyId = payment.familyId;
          _paymentType =
              payment.participantId != null ? 'participant' : 'family';
          _isInitialized = true;
        });
      }
    } else {
      setState(() {
        _isInitialized = true;
      });
    }
  }

  @override
  void dispose() {
    _amountController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_isInitialized) {
      return Scaffold(
        appBar: AppBar(title: const Text('Lädt...')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    final isEdit = widget.paymentId != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEdit ? 'Zahlung bearbeiten' : 'Neue Zahlung'),
        actions: [
          if (isEdit)
            IconButton(
              icon: const Icon(Icons.delete),
              onPressed: _confirmDelete,
            ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Betrag
            TextFormField(
              controller: _amountController,
              decoration: const InputDecoration(
                labelText: 'Betrag (€) *',
                prefixIcon: Icon(Icons.euro),
              ),
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              validator: Validators.positiveAmount,
              autofocus: true,
            ),

            const SizedBox(height: 24),

            // Zahlungsdatum
            Text(
              'Zahlungsdatum',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            InkWell(
              onTap: () => _selectPaymentDate(context),
              child: InputDecorator(
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.calendar_today),
                ),
                child: Text(AppDateUtils.formatGerman(_paymentDate)),
              ),
            ),

            const SizedBox(height: 24),

            // Zahlungsmethode
            DropdownButtonFormField<String>(
              value: _paymentMethod,
              decoration: const InputDecoration(
                labelText: 'Zahlungsmethode',
                prefixIcon: Icon(Icons.payment),
              ),
              items: const [
                DropdownMenuItem(value: null, child: Text('Keine Angabe')),
                DropdownMenuItem(value: 'Bar', child: Text('Bar')),
                DropdownMenuItem(value: 'Überweisung', child: Text('Überweisung')),
                DropdownMenuItem(value: 'EC-Karte', child: Text('EC-Karte')),
                DropdownMenuItem(value: 'PayPal', child: Text('PayPal')),
                DropdownMenuItem(value: 'Sonstige', child: Text('Sonstige')),
              ],
              onChanged: (value) {
                setState(() {
                  _paymentMethod = value;
                });
              },
            ),

            const SizedBox(height: 24),

            // Zahlungstyp
            Text(
              'Zahlung für',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(
                  value: 'participant',
                  label: Text('Teilnehmer'),
                  icon: Icon(Icons.person),
                ),
                ButtonSegment(
                  value: 'family',
                  label: Text('Familie'),
                  icon: Icon(Icons.family_restroom),
                ),
              ],
              selected: {_paymentType},
              onSelectionChanged: (Set<String> selected) {
                setState(() {
                  _paymentType = selected.first;
                  // Reset andere Auswahl
                  if (_paymentType == 'participant') {
                    _selectedFamilyId = null;
                  } else {
                    _selectedParticipantId = null;
                  }
                });
              },
            ),

            const SizedBox(height: 16),

            // Teilnehmer/Familie Auswahl
            if (_paymentType == 'participant')
              _buildParticipantDropdown()
            else
              _buildFamilyDropdown(),

            const SizedBox(height: 24),

            // Notizen
            TextFormField(
              controller: _notesController,
              decoration: const InputDecoration(
                labelText: 'Notizen',
                prefixIcon: Icon(Icons.note),
              ),
              maxLines: 3,
            ),

            const SizedBox(height: 32),

            // Speichern-Button
            SizedBox(
              height: 48,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _savePayment,
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : Text(isEdit ? 'Speichern' : 'Erstellen'),
              ),
            ),

            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildParticipantDropdown() {
    final participantsAsync = ref.watch(participantsProvider);

    return participantsAsync.when(
      data: (participants) {
        return DropdownButtonFormField<int>(
          value: _selectedParticipantId,
          decoration: const InputDecoration(
            labelText: 'Teilnehmer *',
            prefixIcon: Icon(Icons.person),
          ),
          items: participants.map((p) {
            return DropdownMenuItem(
              value: p.id,
              child: Text('${p.firstName} ${p.lastName}'),
            );
          }).toList(),
          onChanged: (value) {
            setState(() {
              _selectedParticipantId = value;
            });
          },
          validator: (value) {
            if (value == null && _paymentType == 'participant') {
              return 'Bitte Teilnehmer auswählen';
            }
            return null;
          },
        );
      },
      loading: () => const LinearProgressIndicator(),
      error: (_, __) => const Text('Fehler beim Laden der Teilnehmer'),
    );
  }

  Widget _buildFamilyDropdown() {
    final familiesAsync = ref.watch(familiesProvider);

    return familiesAsync.when(
      data: (families) {
        return DropdownButtonFormField<int>(
          value: _selectedFamilyId,
          decoration: const InputDecoration(
            labelText: 'Familie *',
            prefixIcon: Icon(Icons.family_restroom),
          ),
          items: families.map((f) {
            return DropdownMenuItem(
              value: f.id,
              child: Text(f.familyName),
            );
          }).toList(),
          onChanged: (value) {
            setState(() {
              _selectedFamilyId = value;
            });
          },
          validator: (value) {
            if (value == null && _paymentType == 'family') {
              return 'Bitte Familie auswählen';
            }
            return null;
          },
        );
      },
      loading: () => const LinearProgressIndicator(),
      error: (_, __) => const Text('Fehler beim Laden der Familien'),
    );
  }

  Future<void> _selectPaymentDate(BuildContext context) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _paymentDate,
      firstDate: DateTime(2000),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      locale: const Locale('de', 'DE'),
    );

    if (picked != null) {
      setState(() {
        _paymentDate = picked;
      });
    }
  }

  Future<void> _savePayment() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final repository = ref.read(paymentRepositoryProvider);
      final eventId = ref.read(currentEventIdProvider);

      if (eventId == null) {
        throw Exception('Kein Event ausgewählt');
      }

      final amount =
          double.parse(_amountController.text.replaceAll(',', '.'));

      if (widget.paymentId == null) {
        // Create
        await repository.createPayment(
          eventId: eventId,
          participantId: _selectedParticipantId,
          familyId: _selectedFamilyId,
          amount: amount,
          paymentDate: _paymentDate,
          paymentMethod: _paymentMethod,
          notes: _notesController.text.isNotEmpty ? _notesController.text : null,
        );

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Zahlung erstellt')),
          );
          Navigator.of(context).pop();
        }
      } else {
        // Update
        await repository.updatePayment(
          id: widget.paymentId!,
          amount: amount,
          paymentDate: _paymentDate,
          paymentMethod: _paymentMethod,
          notes: _notesController.text.isNotEmpty ? _notesController.text : null,
        );

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Zahlung aktualisiert')),
          );
          Navigator.of(context).pop();
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Fehler: $e')),
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

  Future<void> _confirmDelete() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Zahlung löschen?'),
        content: const Text('Möchten Sie diese Zahlung wirklich löschen?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Abbrechen'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Löschen'),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      final repository = ref.read(paymentRepositoryProvider);
      await repository.deletePayment(widget.paymentId!);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Zahlung gelöscht')),
        );
        Navigator.of(context).pop();
      }
    }
  }
}
