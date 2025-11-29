import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../data/database/app_database.dart';
import '../../providers/expense_provider.dart';
import '../../providers/current_event_provider.dart';
import 'expense_form_screen.dart';

class ExpensesListScreen extends ConsumerWidget {
  const ExpensesListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentEvent = ref.watch(currentEventProvider);
    final expensesAsync = ref.watch(expensesProvider);

    if (currentEvent == null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Ausgaben'),
        ),
        body: const Center(
          child: Text('Bitte wählen Sie zuerst eine Veranstaltung aus.'),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Ausgaben'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const ExpenseFormScreen(),
                ),
              );
            },
            tooltip: 'Neue Ausgabe',
          ),
        ],
      ),
      body: expensesAsync.when(
        data: (expenses) {
          if (expenses.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.receipt_long_outlined,
                    size: 80,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Noch keine Ausgaben',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: Colors.grey[600],
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Fügen Sie die erste Ausgabe hinzu',
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
                          builder: (context) => const ExpenseFormScreen(),
                        ),
                      );
                    },
                    icon: const Icon(Icons.add),
                    label: const Text('Ausgabe hinzufügen'),
                  ),
                ],
              ),
            );
          }

          // Group expenses by category
          final expensesByCategory = <String, List<Expense>>{};
          double total = 0.0;

          for (final expense in expenses) {
            expensesByCategory.putIfAbsent(expense.category, () => []).add(expense);
            total += expense.amount;
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
                      const Icon(Icons.euro, size: 32, color: Colors.red),
                      const SizedBox(width: 16),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Gesamtausgaben',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                          Text(
                            '${NumberFormat.currency(locale: 'de_DE', symbol: '€').format(total)}',
                            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.red[700],
                                ),
                          ),
                        ],
                      ),
                      const Spacer(),
                      Text(
                        '${expenses.length} Ausgaben',
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    ],
                  ),
                ),
              ),

              // Category filter chips
              SizedBox(
                height: 50,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  children: [
                    Chip(
                      label: Text('Alle (${expenses.length})'),
                      backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                    ),
                    const SizedBox(width: 8),
                    ...expensesByCategory.entries.map((entry) => Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: Chip(
                            label: Text('${entry.key} (${entry.value.length})'),
                          ),
                        )),
                  ],
                ),
              ),

              // Expenses list
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: expenses.length,
                  itemBuilder: (context, index) {
                    final expense = expenses[index];
                    return _ExpenseListItem(expense: expense);
                  },
                ),
              ),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Text('Fehler beim Laden der Ausgaben: $error'),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const ExpenseFormScreen(),
            ),
          );
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}

class _ExpenseListItem extends StatelessWidget {
  final Expense expense;

  const _ExpenseListItem({required this.expense});

  IconData _getCategoryIcon(String category) {
    switch (category.toLowerCase()) {
      case 'verpflegung':
        return Icons.restaurant;
      case 'unterkunft':
        return Icons.hotel;
      case 'transport':
        return Icons.directions_bus;
      case 'material':
        return Icons.construction;
      case 'personal':
        return Icons.people;
      case 'versicherung':
        return Icons.shield;
      case 'sonstiges':
        return Icons.more_horiz;
      default:
        return Icons.receipt_long;
    }
  }

  Color _getCategoryColor(String category) {
    switch (category.toLowerCase()) {
      case 'verpflegung':
        return Colors.orange;
      case 'unterkunft':
        return Colors.blue;
      case 'transport':
        return Colors.green;
      case 'material':
        return Colors.purple;
      case 'personal':
        return Colors.teal;
      case 'versicherung':
        return Colors.indigo;
      case 'sonstiges':
        return Colors.grey;
      default:
        return Colors.brown;
    }
  }

  @override
  Widget build(BuildContext context) {
    final categoryColor = _getCategoryColor(expense.category);
    final categoryIcon = _getCategoryIcon(expense.category);
    final dateFormat = DateFormat('dd.MM.yyyy', 'de_DE');

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => ExpenseFormScreen(expenseId: expense.id),
            ),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Category icon
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: categoryColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  categoryIcon,
                  color: categoryColor,
                ),
              ),
              const SizedBox(width: 16),

              // Expense details
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          expense.category,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                        if (expense.vendor != null) ...[
                          const SizedBox(width: 8),
                          Flexible(
                            child: Text(
                              '• ${expense.vendor}',
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                    color: Colors.grey[600],
                                  ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 4),
                    if (expense.description != null)
                      Text(
                        expense.description!,
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
                          dateFormat.format(expense.expenseDate),
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: Colors.grey[600],
                              ),
                        ),
                        if (expense.paymentMethod != null) ...[
                          const SizedBox(width: 12),
                          Icon(
                            Icons.payment,
                            size: 14,
                            color: Colors.grey[600],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            expense.paymentMethod!,
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
                    NumberFormat.currency(locale: 'de_DE', symbol: '€').format(expense.amount),
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.red[700],
                        ),
                  ),
                  if (expense.receiptNumber != null)
                    Text(
                      'Beleg: ${expense.receiptNumber}',
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
