import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:drift/drift.dart' as drift;
import '../../data/database/app_database.dart';
import '../../providers/participant_provider.dart';
import '../../providers/current_event_provider.dart';
import '../../providers/database_provider.dart';
import '../../utils/validators.dart';
import '../../utils/date_utils.dart';
import '../../widgets/forms/price_preview_widget.dart';

/// Teilnehmer-Formular (Create/Edit)
///
/// Entspricht participants/form.html aus der Web-App
class ParticipantFormScreen extends ConsumerStatefulWidget {
  final int? participantId; // null = Create, sonst Edit

  const ParticipantFormScreen({
    super.key,
    this.participantId,
  });

  @override
  ConsumerState<ParticipantFormScreen> createState() =>
      _ParticipantFormScreenState();
}

class _ParticipantFormScreenState
    extends ConsumerState<ParticipantFormScreen> {
  final _formKey = GlobalKey<FormState>();

  // Form Controllers
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _streetController = TextEditingController();
  final _postalCodeController = TextEditingController();
  final _cityController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _emergencyContactController = TextEditingController();
  final _emergencyPhoneController = TextEditingController();
  final _medicalNotesController = TextEditingController();
  final _allergiesController = TextEditingController();
  final _dietaryRestrictionsController = TextEditingController();
  final _manualPriceController = TextEditingController();
  final _discountPercentController = TextEditingController();
  final _discountReasonController = TextEditingController();

  // Form State
  DateTime? _birthDate;
  String? _gender;
  bool _bildungUndTeilhabe = false;
  int? _selectedRoleId;
  int? _selectedFamilyId;
  bool _hasManualPrice = false;

  // Loading State
  bool _isLoading = false;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _initializeForm();
  }

  Future<void> _initializeForm() async {
    if (widget.participantId != null) {
      // Edit-Modus: Lade Teilnehmer-Daten
      final repository = ref.read(participantRepositoryProvider);
      final participant =
          await repository.getParticipantById(widget.participantId!);

      if (participant != null && mounted) {
        setState(() {
          _firstNameController.text = participant.firstName;
          _lastNameController.text = participant.lastName;
          _birthDate = participant.birthDate;
          _gender = participant.gender;
          _streetController.text = participant.street ?? '';
          _postalCodeController.text = participant.postalCode ?? '';
          _cityController.text = participant.city ?? '';
          _phoneController.text = participant.phone ?? '';
          _emailController.text = participant.email ?? '';
          _emergencyContactController.text = participant.emergencyContact ?? '';
          _emergencyPhoneController.text = participant.emergencyPhone ?? '';
          _medicalNotesController.text = participant.medicalNotes ?? '';
          _allergiesController.text = participant.allergies ?? '';
          _dietaryRestrictionsController.text =
              participant.dietaryRestrictions ?? '';
          _bildungUndTeilhabe = participant.bildungUndTeilhabe;
          _selectedRoleId = participant.roleId;
          _selectedFamilyId = participant.familyId;

          if (participant.manualPriceOverride != null) {
            _hasManualPrice = true;
            _manualPriceController.text =
                participant.manualPriceOverride.toString();
          }

          _discountPercentController.text =
              participant.discountPercent.toString();
          _discountReasonController.text = participant.discountReason ?? '';

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
    _firstNameController.dispose();
    _lastNameController.dispose();
    _streetController.dispose();
    _postalCodeController.dispose();
    _cityController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _emergencyContactController.dispose();
    _emergencyPhoneController.dispose();
    _medicalNotesController.dispose();
    _allergiesController.dispose();
    _dietaryRestrictionsController.dispose();
    _manualPriceController.dispose();
    _discountPercentController.dispose();
    _discountReasonController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_isInitialized) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Lädt...'),
        ),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    final isEdit = widget.participantId != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEdit ? 'Teilnehmer bearbeiten' : 'Neuer Teilnehmer'),
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
            // Persönliche Daten
            _buildSectionHeader('Persönliche Daten'),
            _buildTextField(
              controller: _firstNameController,
              label: 'Vorname *',
              validator: (value) => Validators.required(value, fieldName: 'Vorname'),
            ),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _lastNameController,
              label: 'Nachname *',
              validator: (value) => Validators.required(value, fieldName: 'Nachname'),
            ),
            const SizedBox(height: 16),
            _buildDateField(),
            const SizedBox(height: 16),
            _buildGenderDropdown(),

            const SizedBox(height: 24),

            // Adresse
            _buildSectionHeader('Adresse'),
            _buildTextField(
              controller: _streetController,
              label: 'Straße',
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  flex: 1,
                  child: _buildTextField(
                    controller: _postalCodeController,
                    label: 'PLZ',
                    keyboardType: TextInputType.number,
                    validator: Validators.postalCode,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  flex: 2,
                  child: _buildTextField(
                    controller: _cityController,
                    label: 'Ort',
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Kontakt
            _buildSectionHeader('Kontaktdaten'),
            _buildTextField(
              controller: _phoneController,
              label: 'Telefon',
              keyboardType: TextInputType.phone,
              validator: Validators.phone,
            ),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _emailController,
              label: 'E-Mail',
              keyboardType: TextInputType.emailAddress,
              validator: Validators.email,
            ),

            const SizedBox(height: 24),

            // Notfallkontakt
            _buildSectionHeader('Notfallkontakt'),
            _buildTextField(
              controller: _emergencyContactController,
              label: 'Notfallkontakt Name',
            ),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _emergencyPhoneController,
              label: 'Notfallkontakt Telefon',
              keyboardType: TextInputType.phone,
              validator: Validators.phone,
            ),

            const SizedBox(height: 24),

            // Medizinische Informationen
            _buildSectionHeader('Medizinische Informationen'),
            _buildTextField(
              controller: _medicalNotesController,
              label: 'Medizinische Hinweise',
              maxLines: 3,
            ),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _allergiesController,
              label: 'Allergien',
              maxLines: 2,
            ),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _dietaryRestrictionsController,
              label: 'Ernährungseinschränkungen',
              maxLines: 2,
            ),

            const SizedBox(height: 24),

            // Rolle & Familie
            _buildSectionHeader('Rolle & Familie'),
            _buildRoleDropdown(),
            const SizedBox(height: 16),
            _buildFamilyDropdown(),

            const SizedBox(height: 24),

            // Sonstige Optionen
            _buildSectionHeader('Sonstige Optionen'),
            SwitchListTile(
              title: const Text('Bildung & Teilhabe'),
              subtitle: const Text('Teilnehmer erhält Zuschuss'),
              value: _bildungUndTeilhabe,
              onChanged: (value) {
                setState(() {
                  _bildungUndTeilhabe = value;
                });
              },
            ),

            const SizedBox(height: 24),

            // Preis (TODO: Live-Berechnung)
            _buildSectionHeader('Preis'),
            _buildPriceSection(),

            const SizedBox(height: 32),

            // Speichern-Button
            SizedBox(
              height: 48,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _saveParticipant,
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

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16, top: 8),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    String? Function(String?)? validator,
    TextInputType? keyboardType,
    int maxLines = 1,
  }) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
      ),
      validator: validator,
      keyboardType: keyboardType,
      maxLines: maxLines,
    );
  }

  Widget _buildDateField() {
    return InkWell(
      onTap: () => _selectBirthDate(context),
      child: InputDecorator(
        decoration: InputDecoration(
          labelText: 'Geburtsdatum *',
          errorText: _birthDate == null && _formKey.currentState?.validate() == false
              ? 'Bitte Geburtsdatum auswählen'
              : null,
        ),
        child: Text(
          _birthDate != null
              ? AppDateUtils.formatGerman(_birthDate!)
              : 'Datum auswählen',
          style: TextStyle(
            color: _birthDate != null ? null : Colors.grey,
          ),
        ),
      ),
    );
  }

  Future<void> _selectBirthDate(BuildContext context) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _birthDate ?? DateTime(2010, 1, 1),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
      locale: const Locale('de', 'DE'),
    );

    if (picked != null) {
      setState(() {
        _birthDate = picked;
      });
    }
  }

  Widget _buildGenderDropdown() {
    return DropdownButtonFormField<String>(
      value: _gender,
      decoration: const InputDecoration(
        labelText: 'Geschlecht',
      ),
      items: const [
        DropdownMenuItem(value: 'Männlich', child: Text('Männlich')),
        DropdownMenuItem(value: 'Weiblich', child: Text('Weiblich')),
        DropdownMenuItem(value: 'Divers', child: Text('Divers')),
      ],
      onChanged: (value) {
        setState(() {
          _gender = value;
        });
      },
    );
  }

  Widget _buildRoleDropdown() {
    final database = ref.watch(databaseProvider);
    final eventId = ref.watch(currentEventIdProvider);

    if (eventId == null) {
      return const SizedBox.shrink();
    }

    return StreamBuilder<List<Role>>(
      stream: (database.select(database.roles)
            ..where((tbl) => tbl.eventId.equals(eventId)))
          .watch(),
      builder: (context, snapshot) {
        final roles = snapshot.data ?? [];

        return DropdownButtonFormField<int>(
          value: _selectedRoleId,
          decoration: const InputDecoration(
            labelText: 'Rolle',
            hintText: 'Keine Rolle',
          ),
          items: [
            const DropdownMenuItem(
              value: null,
              child: Text('Keine Rolle'),
            ),
            ...roles.map(
              (role) => DropdownMenuItem(
                value: role.id,
                child: Text(role.displayName),
              ),
            ),
          ],
          onChanged: (value) {
            setState(() {
              _selectedRoleId = value;
            });
          },
        );
      },
    );
  }

  Widget _buildFamilyDropdown() {
    final database = ref.watch(databaseProvider);
    final eventId = ref.watch(currentEventIdProvider);

    if (eventId == null) {
      return const SizedBox.shrink();
    }

    return StreamBuilder<List<Family>>(
      stream: (database.select(database.families)
            ..where((tbl) => tbl.eventId.equals(eventId)))
          .watch(),
      builder: (context, snapshot) {
        final families = snapshot.data ?? [];

        return DropdownButtonFormField<int>(
          value: _selectedFamilyId,
          decoration: const InputDecoration(
            labelText: 'Familie',
            hintText: 'Keine Familie',
          ),
          items: [
            const DropdownMenuItem(
              value: null,
              child: Text('Keine Familie'),
            ),
            ...families.map(
              (family) => DropdownMenuItem(
                value: family.id,
                child: Text(family.familyName),
              ),
            ),
          ],
          onChanged: (value) {
            setState(() {
              _selectedFamilyId = value;
            });
          },
        );
      },
    );
  }

  Widget _buildPriceSection() {
    final manualPrice = _hasManualPrice && _manualPriceController.text.isNotEmpty
        ? double.tryParse(_manualPriceController.text.replaceAll(',', '.'))
        : null;

    final discountPercent = _discountPercentController.text.isNotEmpty
        ? double.tryParse(_discountPercentController.text.replaceAll(',', '.')) ?? 0.0
        : 0.0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SwitchListTile(
          title: const Text('Manueller Preis'),
          subtitle: const Text('Eigenen Preis festlegen'),
          value: _hasManualPrice,
          onChanged: (value) {
            setState(() {
              _hasManualPrice = value;
              if (!value) {
                _manualPriceController.clear();
              }
            });
          },
        ),
        if (_hasManualPrice) ...[
          const SizedBox(height: 16),
          _buildTextField(
            controller: _manualPriceController,
            label: 'Preis (€) *',
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            validator: Validators.positiveAmount,
          ),
        ],
        const SizedBox(height: 16),
        _buildTextField(
          controller: _discountPercentController,
          label: 'Zusätzlicher Rabatt (%)',
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          validator: Validators.percentage,
        ),
        const SizedBox(height: 16),
        _buildTextField(
          controller: _discountReasonController,
          label: 'Rabattgrund',
          maxLines: 2,
        ),
        const SizedBox(height: 16),
        // Live-Preisberechnung (wie HTMX in Web-App!)
        PricePreviewWidget(
          birthDate: _birthDate,
          roleId: _selectedRoleId,
          familyId: _selectedFamilyId,
          manualPriceOverride: manualPrice,
          discountPercent: discountPercent,
          discountReason: _discountReasonController.text.isNotEmpty
              ? _discountReasonController.text
              : null,
        ),
      ],
    );
  }

  Future<void> _saveParticipant() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (_birthDate == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Bitte Geburtsdatum auswählen')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final repository = ref.read(participantRepositoryProvider);
      final eventId = ref.read(currentEventIdProvider);

      if (eventId == null) {
        throw Exception('Kein Event ausgewählt');
      }

      final manualPrice = _hasManualPrice && _manualPriceController.text.isNotEmpty
          ? double.tryParse(_manualPriceController.text.replaceAll(',', '.'))
          : null;

      final discountPercent = _discountPercentController.text.isNotEmpty
          ? double.tryParse(_discountPercentController.text.replaceAll(',', '.')) ?? 0.0
          : 0.0;

      if (widget.participantId == null) {
        // Create
        await repository.createParticipant(
          eventId: eventId,
          firstName: _firstNameController.text,
          lastName: _lastNameController.text,
          birthDate: _birthDate!,
          gender: _gender,
          street: _streetController.text.isNotEmpty ? _streetController.text : null,
          postalCode:
              _postalCodeController.text.isNotEmpty ? _postalCodeController.text : null,
          city: _cityController.text.isNotEmpty ? _cityController.text : null,
          phone: _phoneController.text.isNotEmpty ? _phoneController.text : null,
          email: _emailController.text.isNotEmpty ? _emailController.text : null,
          emergencyContact: _emergencyContactController.text.isNotEmpty
              ? _emergencyContactController.text
              : null,
          emergencyPhone: _emergencyPhoneController.text.isNotEmpty
              ? _emergencyPhoneController.text
              : null,
          medicalNotes: _medicalNotesController.text.isNotEmpty
              ? _medicalNotesController.text
              : null,
          allergies:
              _allergiesController.text.isNotEmpty ? _allergiesController.text : null,
          dietaryRestrictions: _dietaryRestrictionsController.text.isNotEmpty
              ? _dietaryRestrictionsController.text
              : null,
          bildungUndTeilhabe: _bildungUndTeilhabe,
          roleId: _selectedRoleId,
          familyId: _selectedFamilyId,
          manualPriceOverride: manualPrice,
          discountPercent: discountPercent,
          discountReason: _discountReasonController.text.isNotEmpty
              ? _discountReasonController.text
              : null,
        );

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Teilnehmer erstellt')),
          );
          Navigator.of(context).pop();
        }
      } else {
        // Update
        await repository.updateParticipant(
          id: widget.participantId!,
          firstName: _firstNameController.text,
          lastName: _lastNameController.text,
          birthDate: _birthDate!,
          gender: _gender,
          street: _streetController.text.isNotEmpty ? _streetController.text : null,
          postalCode:
              _postalCodeController.text.isNotEmpty ? _postalCodeController.text : null,
          city: _cityController.text.isNotEmpty ? _cityController.text : null,
          phone: _phoneController.text.isNotEmpty ? _phoneController.text : null,
          email: _emailController.text.isNotEmpty ? _emailController.text : null,
          emergencyContact: _emergencyContactController.text.isNotEmpty
              ? _emergencyContactController.text
              : null,
          emergencyPhone: _emergencyPhoneController.text.isNotEmpty
              ? _emergencyPhoneController.text
              : null,
          medicalNotes: _medicalNotesController.text.isNotEmpty
              ? _medicalNotesController.text
              : null,
          allergies:
              _allergiesController.text.isNotEmpty ? _allergiesController.text : null,
          dietaryRestrictions: _dietaryRestrictionsController.text.isNotEmpty
              ? _dietaryRestrictionsController.text
              : null,
          bildungUndTeilhabe: _bildungUndTeilhabe,
          roleId: _selectedRoleId,
          familyId: _selectedFamilyId,
          manualPriceOverride: manualPrice,
          discountPercent: discountPercent,
          discountReason: _discountReasonController.text.isNotEmpty
              ? _discountReasonController.text
              : null,
        );

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Teilnehmer aktualisiert')),
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
        title: const Text('Teilnehmer löschen?'),
        content: const Text('Möchten Sie diesen Teilnehmer wirklich löschen?'),
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
      final repository = ref.read(participantRepositoryProvider);
      await repository.deleteParticipant(widget.participantId!);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Teilnehmer gelöscht')),
        );
        Navigator.of(context).pop();
      }
    }
  }
}
