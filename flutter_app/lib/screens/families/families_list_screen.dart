import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/family_provider.dart';
import '../../data/database/app_database.dart';

/// Families List Screen
class FamiliesListScreen extends ConsumerWidget {
  const FamiliesListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final familiesAsync = ref.watch(familiesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Familien'),
      ),
      body: familiesAsync.when(
        data: (families) {
          if (families.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.family_restroom, size: 100, color: Colors.grey),
                  const SizedBox(height: 24),
                  const Text(
                    'Noch keine Familien',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Füge deine erste Familie hinzu.',
                    style: TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: families.length,
            itemBuilder: (context, index) {
              final family = families[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  leading: const CircleAvatar(
                    child: Icon(Icons.family_restroom),
                  ),
                  title: Text(
                    family.familyName,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: family.contactPerson != null
                      ? Text('Kontakt: ${family.contactPerson}')
                      : null,
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    // TODO: Detail/Edit Screen (Sprint 2)
                  },
                ),
              );
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(child: Text('Fehler: $error')),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          // TODO: Create Family Screen (Sprint 2)
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Familien-Formular kommt in Sprint 2')),
          );
        },
        icon: const Icon(Icons.add),
        label: const Text('Familie'),
      ),
    );
  }
}
