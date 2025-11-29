import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/current_event_provider.dart';
import '../../providers/participant_provider.dart';
import '../../data/database/app_database.dart';
import '../../utils/date_utils.dart';
import 'participant_form_screen.dart';
import 'participant_import_screen.dart';

/// Participants List Screen
///
/// Zeigt alle Teilnehmer des aktuellen Events mit Suche und Filtern
class ParticipantsListScreen extends ConsumerStatefulWidget {
  const ParticipantsListScreen({super.key});

  @override
  ConsumerState<ParticipantsListScreen> createState() => _ParticipantsListScreenState();
}

class _ParticipantsListScreenState extends ConsumerState<ParticipantsListScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';
  String? _ageFilter; // 'children', 'youth', 'adults'
  String? _genderFilter;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  List<Participant> _filterParticipants(List<Participant> participants) {
    var filtered = participants;

    // Search filter
    if (_searchQuery.isNotEmpty) {
      final query = _searchQuery.toLowerCase();
      filtered = filtered.where((p) {
        final fullName = '${p.firstName} ${p.lastName}'.toLowerCase();
        final email = p.email?.toLowerCase() ?? '';
        final city = p.city?.toLowerCase() ?? '';
        return fullName.contains(query) || email.contains(query) || city.contains(query);
      }).toList();
    }

    // Age filter
    if (_ageFilter != null) {
      filtered = filtered.where((p) {
        final age = AppDateUtils.calculateAge(p.birthDate);
        switch (_ageFilter) {
          case 'children':
            return age <= 12;
          case 'youth':
            return age >= 13 && age <= 17;
          case 'adults':
            return age >= 18;
          default:
            return true;
        }
      }).toList();
    }

    // Gender filter
    if (_genderFilter != null && _genderFilter!.isNotEmpty) {
      filtered = filtered.where((p) => p.gender == _genderFilter).toList();
    }

    return filtered;
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Filter'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Altersgruppe:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: [
                FilterChip(
                  label: const Text('Alle'),
                  selected: _ageFilter == null,
                  onSelected: (selected) {
                    setState(() {
                      _ageFilter = null;
                    });
                    Navigator.pop(context);
                  },
                ),
                FilterChip(
                  label: const Text('Kinder (≤12)'),
                  selected: _ageFilter == 'children',
                  onSelected: (selected) {
                    setState(() {
                      _ageFilter = selected ? 'children' : null;
                    });
                    Navigator.pop(context);
                  },
                ),
                FilterChip(
                  label: const Text('Jugendliche (13-17)'),
                  selected: _ageFilter == 'youth',
                  onSelected: (selected) {
                    setState(() {
                      _ageFilter = selected ? 'youth' : null;
                    });
                    Navigator.pop(context);
                  },
                ),
                FilterChip(
                  label: const Text('Erwachsene (≥18)'),
                  selected: _ageFilter == 'adults',
                  onSelected: (selected) {
                    setState(() {
                      _ageFilter = selected ? 'adults' : null;
                    });
                    Navigator.pop(context);
                  },
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text('Geschlecht:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: [
                FilterChip(
                  label: const Text('Alle'),
                  selected: _genderFilter == null,
                  onSelected: (selected) {
                    setState(() {
                      _genderFilter = null;
                    });
                    Navigator.pop(context);
                  },
                ),
                FilterChip(
                  label: const Text('Männlich'),
                  selected: _genderFilter == 'Männlich',
                  onSelected: (selected) {
                    setState(() {
                      _genderFilter = selected ? 'Männlich' : null;
                    });
                    Navigator.pop(context);
                  },
                ),
                FilterChip(
                  label: const Text('Weiblich'),
                  selected: _genderFilter == 'Weiblich',
                  onSelected: (selected) {
                    setState(() {
                      _genderFilter = selected ? 'Weiblich' : null;
                    });
                    Navigator.pop(context);
                  },
                ),
                FilterChip(
                  label: const Text('Divers'),
                  selected: _genderFilter == 'Divers',
                  onSelected: (selected) {
                    setState(() {
                      _genderFilter = selected ? 'Divers' : null;
                    });
                    Navigator.pop(context);
                  },
                ),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              setState(() {
                _ageFilter = null;
                _genderFilter = null;
              });
              Navigator.pop(context);
            },
            child: const Text('Zurücksetzen'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Schließen'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final participantsAsync = ref.watch(participantsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Teilnehmer'),
        actions: [
          IconButton(
            icon: Icon(
              Icons.filter_list,
              color: (_ageFilter != null || _genderFilter != null) ? Colors.orange : null,
            ),
            onPressed: _showFilterDialog,
            tooltip: 'Filter',
          ),
          IconButton(
            icon: const Icon(Icons.upload_file),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const ParticipantImportScreen(),
                ),
              );
            },
            tooltip: 'Excel importieren',
          ),
        ],
      ),
      body: Column(
        children: [
          // Search Bar
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Suche nach Name, E-Mail oder Stadt...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          setState(() {
                            _searchController.clear();
                            _searchQuery = '';
                          });
                        },
                      )
                    : null,
                border: const OutlineInputBorder(),
              ),
              onChanged: (value) {
                setState(() {
                  _searchQuery = value;
                });
              },
            ),
          ),

          // Filter chips
          if (_ageFilter != null || _genderFilter != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Wrap(
                spacing: 8,
                children: [
                  if (_ageFilter != null)
                    Chip(
                      label: Text(_getAgeFilterLabel(_ageFilter!)),
                      onDeleted: () {
                        setState(() {
                          _ageFilter = null;
                        });
                      },
                    ),
                  if (_genderFilter != null)
                    Chip(
                      label: Text(_genderFilter!),
                      onDeleted: () {
                        setState(() {
                          _genderFilter = null;
                        });
                      },
                    ),
                ],
              ),
            ),

          // Participants List
          Expanded(
            child: participantsAsync.when(
              data: (participants) {
                if (participants.isEmpty) {
                  return _buildEmptyState(context);
                }

                final filteredParticipants = _filterParticipants(participants);

                if (filteredParticipants.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.search_off, size: 80, color: Colors.grey),
                        const SizedBox(height: 16),
                        const Text(
                          'Keine Ergebnisse gefunden',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        const Text('Versuchen Sie eine andere Suche oder Filter'),
                        const SizedBox(height: 16),
                        TextButton(
                          onPressed: () {
                            setState(() {
                              _searchController.clear();
                              _searchQuery = '';
                              _ageFilter = null;
                              _genderFilter = null;
                            });
                          },
                          child: const Text('Filter zurücksetzen'),
                        ),
                      ],
                    ),
                  );
                }

                return Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      child: Text(
                        '${filteredParticipants.length} von ${participants.length} Teilnehmern',
                        style: TextStyle(color: Colors.grey[600]),
                      ),
                    ),
                    Expanded(
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: filteredParticipants.length,
                        itemBuilder: (context, index) {
                          final participant = filteredParticipants[index];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: ListTile(
                              leading: CircleAvatar(
                                child: Text(
                                  participant.firstName[0].toUpperCase(),
                                  style: const TextStyle(fontWeight: FontWeight.bold),
                                ),
                              ),
                              title: Text(
                                '${participant.firstName} ${participant.lastName}',
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const SizedBox(height: 4),
                                  Text(
                                    'Geb.: ${AppDateUtils.formatGerman(participant.birthDate)} (${AppDateUtils.calculateAge(participant.birthDate)} Jahre)',
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    'Preis: ${_getDisplayPrice(participant).toStringAsFixed(2)} €',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      color: Colors.green,
                                    ),
                                  ),
                                ],
                              ),
                              trailing: const Icon(Icons.chevron_right),
                              onTap: () {
                                Navigator.of(context).push(
                                  MaterialPageRoute(
                                    builder: (context) => ParticipantFormScreen(
                                      participantId: participant.id,
                                    ),
                                  ),
                                );
                              },
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stack) => Center(
                child: Text('Fehler: $error'),
              ),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => const ParticipantFormScreen(),
            ),
          );
        },
        icon: const Icon(Icons.add),
        label: const Text('Teilnehmer'),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.people_outline,
            size: 100,
            color: Colors.grey,
          ),
          const SizedBox(height: 24),
          const Text(
            'Noch keine Teilnehmer',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Füge deinen ersten Teilnehmer hinzu.',
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }

  String _getAgeFilterLabel(String filter) {
    switch (filter) {
      case 'children':
        return 'Kinder (≤12)';
      case 'youth':
        return 'Jugendliche (13-17)';
      case 'adults':
        return 'Erwachsene (≥18)';
      default:
        return filter;
    }
  }

  double _getDisplayPrice(Participant participant) {
    return participant.manualPriceOverride ?? participant.calculatedPrice;
  }
}
