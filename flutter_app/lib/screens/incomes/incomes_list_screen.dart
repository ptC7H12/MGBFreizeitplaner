import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../data/database/app_database.dart';
import '../../providers/income_provider.dart';
import '../../providers/current_event_provider.dart';
import 'income_form_screen.dart';

class IncomesListScreen extends ConsumerWidget {
  const IncomesListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentEvent = ref.watch(currentEventProvider);
    final incomesAsync = ref.watch(incomesProvider);

    if (currentEvent == null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Einnahmen'),
        ),
        body: const Center(
          child: Text('Bitte wählen Sie zuerst eine Veranstaltung aus.'),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Einnahmen'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const IncomeFormScreen(),
                ),
              );
            },
            tooltip: 'Neue Einnahme',
          ),
        ],
      ),
      body: incomesAsync.when(
        data: (incomes) {
          if (incomes.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.account_balance_wallet_outlined,
                    size: 80,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Noch keine Einnahmen',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: Colors.grey[600],
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Fügen Sie die erste Einnahme hinzu',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.grey[500],
                        ),
                  ),
                  const SizedBox(height: 24),
                  FilledButton.icon(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const IncomeFormScreen(),
                        ),
                      );
                    },
                    icon: const Icon(Icons.add),
                    label: const Text('Einnahme hinzufügen'),
                  ),
                ],
              ),
            );
          }

          // Group incomes by source
          final incomesBySource = <String, List<Income>>{};
          double total = 0.0;

          for (final income in incomes) {
            incomesBySource.putIfAbsent(income.source, () => []).add(income);
            total += income.amount;
          }

          return Column(
            children: [
              // Total summary card
              Card(
                margin: const EdgeInsets.all(16),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      const Icon(Icons.euro, size: 32, color: Colors.green),
                      const SizedBox(width: 16),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Gesamteinnahmen',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                          Text(
                            '${NumberFormat.currency(locale: 'de_DE', symbol: '€').format(total)}',
                            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.green[700],
                                ),
                          ),
                        ],
                      ),
                      const Spacer(),
                      Text(
                        '${incomes.length} Einnahmen',
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    ],
                  ),
                ),
              ),

              // Source filter chips
              SizedBox(
                height: 50,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  children: [
                    Chip(
                      label: Text('Alle (${incomes.length})'),
                      backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                    ),
                    const SizedBox(width: 8),
                    ...incomesBySource.entries.map((entry) => Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: Chip(
                            label: Text('${entry.key} (${entry.value.length})'),
                          ),
                        )),
                  ],
                ),
              ),

              // Incomes list
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: incomes.length,
                  itemBuilder: (context, index) {
                    final income = incomes[index];
                    return _IncomeListItem(income: income);
                  },
                ),
              ),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Text('Fehler beim Laden der Einnahmen: $error'),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const IncomeFormScreen(),
            ),
          );
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}

class _IncomeListItem extends StatelessWidget {
  final Income income;

  const _IncomeListItem({required this.income});

  IconData _getSourceIcon(String source) {
    switch (source.toLowerCase()) {
      case 'teilnehmerbeitrag':
        return Icons.person;
      case 'spende':
        return Icons.favorite;
      case 'zuschuss':
        return Icons.account_balance;
      case 'sponsoring':
        return Icons.business;
      case 'merchandise':
        return Icons.shopping_bag;
      case 'sonstiges':
        return Icons.more_horiz;
      default:
        return Icons.account_balance_wallet;
    }
  }

  Color _getSourceColor(String source) {
    switch (source.toLowerCase()) {
      case 'teilnehmerbeitrag':
        return Colors.blue;
      case 'spende':
        return Colors.pink;
      case 'zuschuss':
        return Colors.green;
      case 'sponsoring':
        return Colors.purple;
      case 'merchandise':
        return Colors.orange;
      case 'sonstiges':
        return Colors.grey;
      default:
        return Colors.teal;
    }
  }

  @override
  Widget build(BuildContext context) {
    final sourceColor = _getSourceColor(income.source);
    final sourceIcon = _getSourceIcon(income.source);
    final dateFormat = DateFormat('dd.MM.yyyy', 'de_DE');

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => IncomeFormScreen(incomeId: income.id),
            ),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Source icon
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: sourceColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  sourceIcon,
                  color: sourceColor,
                ),
              ),
              const SizedBox(width: 16),

              // Income details
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      income.source,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 4),
                    if (income.description != null)
                      Text(
                        income.description!,
                        style: Theme.of(context).textTheme.bodyMedium,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(
                          Icons.calendar_today,
                          size: 14,
                          color: Colors.grey[600],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          dateFormat.format(income.incomeDate),
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: Colors.grey[600],
                              ),
                        ),
                        if (income.paymentMethod != null) ...[
                          const SizedBox(width: 12),
                          Icon(
                            Icons.payment,
                            size: 14,
                            color: Colors.grey[600],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            income.paymentMethod!,
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: Colors.grey[600],
                                ),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),

              // Amount
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    NumberFormat.currency(locale: 'de_DE', symbol: '€').format(income.amount),
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.green[700],
                        ),
                  ),
                  if (income.referenceNumber != null)
                    Text(
                      'Ref: ${income.referenceNumber}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.grey[600],
                          ),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
