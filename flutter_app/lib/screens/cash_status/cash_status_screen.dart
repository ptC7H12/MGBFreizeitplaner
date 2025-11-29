import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../providers/current_event_provider.dart';
import '../../providers/database_provider.dart';
import '../../providers/expense_provider.dart';
import '../../providers/income_provider.dart';
import '../../providers/pdf_export_provider.dart';
import '../../data/database/app_database.dart';

class CashStatusScreen extends ConsumerWidget {
  const CashStatusScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentEvent = ref.watch(currentEventProvider);
    final database = ref.watch(databaseProvider);

    if (currentEvent == null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Kassenstand'),
        ),
        body: const Center(
          child: Text('Bitte wählen Sie zuerst eine Veranstaltung aus.'),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Kassenstand'),
        actions: [
          IconButton(
            icon: const Icon(Icons.download),
            onPressed: () async {
              final pdfService = ref.read(pdfExportServiceProvider);
              final totalIncomesAsync = ref.read(totalIncomesProvider);
              final totalExpensesAsync = ref.read(totalExpensesProvider);
              final expensesByCategoryAsync = ref.read(expensesByCategoryProvider);
              final incomesBySourceAsync = ref.read(incomesBySourceProvider);

              final payments = await (database.select(database.payments)
                    ..where((t) => t.eventId.equals(currentEvent.id) & t.isActive.equals(true)))
                  .get();
              final totalPayments = payments.fold<double>(0, (sum, p) => sum + p.amount);

              final totalIncomes = await totalIncomesAsync.future;
              final totalExpenses = await totalExpensesAsync.future;
              final expensesByCategory = await expensesByCategoryAsync.future;
              final incomesBySource = await incomesBySourceAsync.future;

              try {
                final filePath = await pdfService.exportFinancialReport(
                  eventName: currentEvent.name,
                  totalIncomes: totalIncomes,
                  totalExpenses: totalExpenses,
                  totalPayments: totalPayments,
                  expensesByCategory: expensesByCategory,
                  incomesBySource: incomesBySource,
                );

                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('PDF gespeichert: $filePath')),
                  );
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Fehler beim Export: $e')),
                  );
                }
              }
            },
            tooltip: 'PDF Export',
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Summary Card
          _buildSummaryCard(context, ref, currentEvent.id),
          const SizedBox(height: 24),

          // Income vs Expense Chart
          _buildIncomeExpenseChart(context, ref, currentEvent.id),
          const SizedBox(height: 24),

          // Expense by Category Chart
          _buildExpenseByCategoryChart(context, ref, currentEvent.id),
          const SizedBox(height: 24),

          // Income by Source Chart
          _buildIncomeBySourceChart(context, ref, currentEvent.id),
          const SizedBox(height: 24),

          // Detailed Breakdown
          _buildDetailedBreakdown(context, ref, database, currentEvent.id),
        ],
      ),
    );
  }

  Widget _buildSummaryCard(BuildContext context, WidgetRef ref, int eventId) {
    final totalIncomesAsync = ref.watch(totalIncomesProvider);
    final totalExpensesAsync = ref.watch(totalExpensesProvider);
    final database = ref.watch(databaseProvider);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Finanzübersicht',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: totalIncomesAsync.when(
                    data: (totalIncomes) => _buildSummaryItem(
                      context,
                      'Einnahmen',
                      totalIncomes,
                      Colors.green,
                      Icons.trending_up,
                    ),
                    loading: () => const CircularProgressIndicator(),
                    error: (_, __) => const Text('Fehler'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: totalExpensesAsync.when(
                    data: (totalExpenses) => _buildSummaryItem(
                      context,
                      'Ausgaben',
                      totalExpenses,
                      Colors.red,
                      Icons.trending_down,
                    ),
                    loading: () => const CircularProgressIndicator(),
                    error: (_, __) => const Text('Fehler'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 16),
            StreamBuilder<List<Payment>>(
              stream: (database.select(database.payments)
                    ..where((tbl) => tbl.eventId.equals(eventId))
                    ..where((tbl) => tbl.isActive.equals(true)))
                  .watch(),
              builder: (context, snapshot) {
                final payments = snapshot.data ?? [];
                final totalPayments = payments.fold<double>(
                  0.0,
                  (sum, payment) => sum + payment.amount,
                );

                return totalIncomesAsync.when(
                  data: (totalIncomes) => totalExpensesAsync.when(
                    data: (totalExpenses) {
                      final balance = totalIncomes - totalExpenses;
                      final expectedBalance = totalPayments - totalExpenses;
                      final outstanding = totalPayments - totalIncomes;

                      return Column(
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: _buildSummaryItem(
                                  context,
                                  'Kassenstand',
                                  balance,
                                  balance >= 0 ? Colors.teal : Colors.deepOrange,
                                  Icons.account_balance_wallet,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: _buildSummaryItem(
                                  context,
                                  'Zahlungen',
                                  totalPayments,
                                  Colors.blue,
                                  Icons.payment,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          if (outstanding > 0)
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.orange[50],
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.orange[200]!),
                              ),
                              child: Row(
                                children: [
                                  Icon(Icons.warning_amber, color: Colors.orange[700]),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          'Ausstehende Zahlungen',
                                          style: TextStyle(
                                            fontWeight: FontWeight.bold,
                                            color: Colors.orange[900],
                                          ),
                                        ),
                                        Text(
                                          NumberFormat.currency(locale: 'de_DE', symbol: '€')
                                              .format(outstanding),
                                          style: TextStyle(
                                            fontSize: 18,
                                            fontWeight: FontWeight.bold,
                                            color: Colors.orange[700],
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                        ],
                      );
                    },
                    loading: () => const CircularProgressIndicator(),
                    error: (_, __) => const Text('Fehler'),
                  ),
                  loading: () => const CircularProgressIndicator(),
                  error: (_, __) => const Text('Fehler'),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryItem(
    BuildContext context,
    String label,
    double value,
    Color color,
    IconData icon,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 20, color: color),
            const SizedBox(width: 8),
            Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          NumberFormat.currency(locale: 'de_DE', symbol: '€').format(value),
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: color,
              ),
        ),
      ],
    );
  }

  Widget _buildIncomeExpenseChart(BuildContext context, WidgetRef ref, int eventId) {
    final totalIncomesAsync = ref.watch(totalIncomesProvider);
    final totalExpensesAsync = ref.watch(totalExpensesProvider);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Einnahmen vs. Ausgaben',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              height: 200,
              child: totalIncomesAsync.when(
                data: (totalIncomes) => totalExpensesAsync.when(
                  data: (totalExpenses) {
                    if (totalIncomes == 0 && totalExpenses == 0) {
                      return Center(
                        child: Text(
                          'Noch keine Daten vorhanden',
                          style: TextStyle(color: Colors.grey[600]),
                        ),
                      );
                    }

                    return BarChart(
                      BarChartData(
                        alignment: BarChartAlignment.spaceAround,
                        maxY: (totalIncomes > totalExpenses ? totalIncomes : totalExpenses) * 1.2,
                        barTouchData: BarTouchData(enabled: false),
                        titlesData: FlTitlesData(
                          show: true,
                          bottomTitles: AxisTitles(
                            sideTitles: SideTitles(
                              showTitles: true,
                              getTitlesWidget: (value, meta) {
                                switch (value.toInt()) {
                                  case 0:
                                    return const Text('Einnahmen', style: TextStyle(fontSize: 12));
                                  case 1:
                                    return const Text('Ausgaben', style: TextStyle(fontSize: 12));
                                  default:
                                    return const Text('');
                                }
                              },
                            ),
                          ),
                          leftTitles: AxisTitles(
                            sideTitles: SideTitles(
                              showTitles: true,
                              reservedSize: 60,
                              getTitlesWidget: (value, meta) {
                                return Text(
                                  '${value.toInt()}€',
                                  style: const TextStyle(fontSize: 10),
                                );
                              },
                            ),
                          ),
                          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                        ),
                        gridData: const FlGridData(show: false),
                        borderData: FlBorderData(show: false),
                        barGroups: [
                          BarChartGroupData(
                            x: 0,
                            barRods: [
                              BarChartRodData(
                                toY: totalIncomes,
                                color: Colors.green,
                                width: 40,
                                borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
                              ),
                            ],
                          ),
                          BarChartGroupData(
                            x: 1,
                            barRods: [
                              BarChartRodData(
                                toY: totalExpenses,
                                color: Colors.red,
                                width: 40,
                                borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
                              ),
                            ],
                          ),
                        ],
                      ),
                    );
                  },
                  loading: () => const Center(child: CircularProgressIndicator()),
                  error: (_, __) => const Center(child: Text('Fehler')),
                ),
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (_, __) => const Center(child: Text('Fehler')),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildExpenseByCategoryChart(BuildContext context, WidgetRef ref, int eventId) {
    final expensesByCategoryAsync = ref.watch(expensesByCategoryProvider);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Ausgaben nach Kategorie',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              height: 200,
              child: expensesByCategoryAsync.when(
                data: (byCategory) {
                  if (byCategory.isEmpty) {
                    return Center(
                      child: Text(
                        'Noch keine Ausgaben vorhanden',
                        style: TextStyle(color: Colors.grey[600]),
                      ),
                    );
                  }

                  final total = byCategory.values.fold<double>(0, (sum, val) => sum + val);
                  final sections = byCategory.entries.map((entry) {
                    final percentage = (entry.value / total) * 100;
                    return PieChartSectionData(
                      value: entry.value,
                      title: '${percentage.toStringAsFixed(1)}%',
                      color: _getCategoryColor(entry.key),
                      radius: 80,
                      titleStyle: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    );
                  }).toList();

                  return Row(
                    children: [
                      Expanded(
                        flex: 2,
                        child: PieChart(
                          PieChartData(
                            sections: sections,
                            sectionsSpace: 2,
                            centerSpaceRadius: 40,
                          ),
                        ),
                      ),
                      Expanded(
                        flex: 1,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: byCategory.entries.map((entry) {
                            return Padding(
                              padding: const EdgeInsets.symmetric(vertical: 4),
                              child: Row(
                                children: [
                                  Container(
                                    width: 12,
                                    height: 12,
                                    decoration: BoxDecoration(
                                      color: _getCategoryColor(entry.key),
                                      shape: BoxShape.circle,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      entry.key,
                                      style: const TextStyle(fontSize: 11),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            );
                          }).toList(),
                        ),
                      ),
                    ],
                  );
                },
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (_, __) => const Center(child: Text('Fehler')),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIncomeBySourceChart(BuildContext context, WidgetRef ref, int eventId) {
    final incomesBySourceAsync = ref.watch(incomesBySourceProvider);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Einnahmen nach Quelle',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              height: 200,
              child: incomesBySourceAsync.when(
                data: (bySource) {
                  if (bySource.isEmpty) {
                    return Center(
                      child: Text(
                        'Noch keine Einnahmen vorhanden',
                        style: TextStyle(color: Colors.grey[600]),
                      ),
                    );
                  }

                  final total = bySource.values.fold<double>(0, (sum, val) => sum + val);
                  final sections = bySource.entries.map((entry) {
                    final percentage = (entry.value / total) * 100;
                    return PieChartSectionData(
                      value: entry.value,
                      title: '${percentage.toStringAsFixed(1)}%',
                      color: _getSourceColor(entry.key),
                      radius: 80,
                      titleStyle: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    );
                  }).toList();

                  return Row(
                    children: [
                      Expanded(
                        flex: 2,
                        child: PieChart(
                          PieChartData(
                            sections: sections,
                            sectionsSpace: 2,
                            centerSpaceRadius: 40,
                          ),
                        ),
                      ),
                      Expanded(
                        flex: 1,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: bySource.entries.map((entry) {
                            return Padding(
                              padding: const EdgeInsets.symmetric(vertical: 4),
                              child: Row(
                                children: [
                                  Container(
                                    width: 12,
                                    height: 12,
                                    decoration: BoxDecoration(
                                      color: _getSourceColor(entry.key),
                                      shape: BoxShape.circle,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      entry.key,
                                      style: const TextStyle(fontSize: 11),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            );
                          }).toList(),
                        ),
                      ),
                    ],
                  );
                },
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (_, __) => const Center(child: Text('Fehler')),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailedBreakdown(
    BuildContext context,
    WidgetRef ref,
    AppDatabase database,
    int eventId,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Detaillierte Aufschlüsselung',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            _buildDetailedSection(context, ref, 'Ausgaben nach Kategorie', expensesByCategoryProvider),
            const Divider(height: 32),
            _buildDetailedSection(context, ref, 'Einnahmen nach Quelle', incomesBySourceProvider),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailedSection(
    BuildContext context,
    WidgetRef ref,
    String title,
    ProviderListenable<AsyncValue<Map<String, double>>> provider,
  ) {
    final dataAsync = ref.watch(provider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 12),
        dataAsync.when(
          data: (data) {
            if (data.isEmpty) {
              return Text(
                'Keine Daten vorhanden',
                style: TextStyle(color: Colors.grey[600]),
              );
            }

            return Column(
              children: data.entries.map((entry) {
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  child: Row(
                    children: [
                      Expanded(
                        child: Text(entry.key),
                      ),
                      Text(
                        NumberFormat.currency(locale: 'de_DE', symbol: '€').format(entry.value),
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                );
              }).toList(),
            );
          },
          loading: () => const CircularProgressIndicator(),
          error: (_, __) => const Text('Fehler beim Laden'),
        ),
      ],
    );
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
      default:
        return Colors.grey;
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
      default:
        return Colors.teal;
    }
  }
}
