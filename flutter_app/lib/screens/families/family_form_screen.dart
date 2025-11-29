import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/database/app_database.dart';
import '../../providers/family_provider.dart';
import '../../providers/current_event_provider.dart';
import '../../utils/validators.dart';

/// Familien-Formular (Create/Edit)
class FamilyFormScreen extends ConsumerStatefulWidget {
  final int? familyId; // null = Create, sonst Edit

  const FamilyFormScreen({
    super.key,
    this.familyId,
  });

  @override
  ConsumerState<FamilyFormScreen> createState() => _FamilyFormScreenState();
}

class _FamilyFormScreenState extends ConsumerState<FamilyFormScreen> {
  final _formKey = GlobalKey<FormState>();

  // Form Controllers
  final _familyNameController = TextEditingController();
  final _contactPersonController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _streetController = TextEditingController();
  final _postalCodeController = TextEditingController();
  final _cityController = TextEditingController();

  bool _isLoading = false;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _initializeForm();
  }

  Future<void> _initializeForm() async {
    if (widget.familyId != null) {
      // Edit-Modus: Lade Familien-Daten
      final repository = ref.read(familyRepositoryProvider);
      final family = await repository.getFamilyById(widget.familyId!);

      if (family != null && mounted) {
        setState(() {
          _familyNameController.text = family.familyName;
          _contactPersonController.text = family.contactPerson ?? '';
          _phoneController.text = family.phone ?? '';
          _emailController.text = family.email ?? '';
          _streetController.text = family.street ?? '';
          _postalCodeController.text = family.postalCode ?? '';
          _cityController.text = family.city ?? '';
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
    _familyNameController.dispose();
    _contactPersonController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _streetController.dispose();
    _postalCodeController.dispose();
    _cityController.dispose();
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

    final isEdit = widget.familyId != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEdit ? 'Familie bearbeiten' : 'Neue Familie'),
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
            // Familienname
            TextFormField(
              controller: _familyNameController,
              decoration: const InputDecoration(
                labelText: 'Familienname *',
                hintText: 'z.B. Familie Müller',
              ),
              validator: (value) =>
                  Validators.required(value, fieldName: 'Familienname'),
            ),

            const SizedBox(height: 24),

            // Kontaktdaten
            Text(
              'Kontaktdaten',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),

            TextFormField(
              controller: _contactPersonController,
              decoration: const InputDecoration(
                labelText: 'Kontaktperson',
                hintText: 'z.B. Max Müller',
              ),
            ),

            const SizedBox(height: 16),

            TextFormField(
              controller: _phoneController,
              decoration: const InputDecoration(
                labelText: 'Telefon',
              ),
              keyboardType: TextInputType.phone,
              validator: Validators.phone,
            ),

            const SizedBox(height: 16),

            TextFormField(
              controller: _emailController,
              decoration: const InputDecoration(
                labelText: 'E-Mail',
              ),
              keyboardType: TextInputType.emailAddress,
              validator: Validators.email,
            ),

            const SizedBox(height: 24),

            // Adresse
            Text(
              'Adresse',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),

            TextFormField(
              controller: _streetController,
              decoration: const InputDecoration(
                labelText: 'Straße',
              ),
            ),

            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  flex: 1,
                  child: TextFormField(
                    controller: _postalCodeController,
                    decoration: const InputDecoration(
                      labelText: 'PLZ',
                    ),
                    keyboardType: TextInputType.number,
                    validator: Validators.postalCode,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  flex: 2,
                  child: TextFormField(
                    controller: _cityController,
                    decoration: const InputDecoration(
                      labelText: 'Ort',
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 32),

            // Speichern-Button
            SizedBox(
              height: 48,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _saveFamily,
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

  Future<void> _saveFamily() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final repository = ref.read(familyRepositoryProvider);
      final eventId = ref.read(currentEventIdProvider);

      if (eventId == null) {
        throw Exception('Kein Event ausgewählt');
      }

      if (widget.familyId == null) {
        // Create
        await repository.createFamily(
          eventId: eventId,
          familyName: _familyNameController.text,
          contactPerson: _contactPersonController.text.isNotEmpty
              ? _contactPersonController.text
              : null,
          phone: _phoneController.text.isNotEmpty ? _phoneController.text : null,
          email: _emailController.text.isNotEmpty ? _emailController.text : null,
          street:
              _streetController.text.isNotEmpty ? _streetController.text : null,
          postalCode: _postalCodeController.text.isNotEmpty
              ? _postalCodeController.text
              : null,
          city: _cityController.text.isNotEmpty ? _cityController.text : null,
        );

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Familie erstellt')),
          );
          Navigator.of(context).pop();
        }
      } else {
        // Update
        await repository.updateFamily(
          id: widget.familyId!,
          familyName: _familyNameController.text,
          contactPerson: _contactPersonController.text.isNotEmpty
              ? _contactPersonController.text
              : null,
          phone: _phoneController.text.isNotEmpty ? _phoneController.text : null,
          email: _emailController.text.isNotEmpty ? _emailController.text : null,
          street:
              _streetController.text.isNotEmpty ? _streetController.text : null,
          postalCode: _postalCodeController.text.isNotEmpty
              ? _postalCodeController.text
              : null,
          city: _cityController.text.isNotEmpty ? _cityController.text : null,
        );

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Familie aktualisiert')),
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
        title: const Text('Familie löschen?'),
        content: const Text(
          'Möchten Sie diese Familie wirklich löschen?\n\n'
          'Hinweis: Teilnehmer dieser Familie werden NICHT gelöscht, '
          'sie werden nur von der Familie getrennt.',
        ),
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
      final repository = ref.read(familyRepositoryProvider);
      await repository.deleteFamily(widget.familyId!);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Familie gelöscht')),
        );
        Navigator.of(context).pop();
      }
    }
  }
}
