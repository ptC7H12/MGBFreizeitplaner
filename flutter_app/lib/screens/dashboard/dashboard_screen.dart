import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../providers/current_event_provider.dart';
import '../../providers/database_provider.dart';
import '../../data/database/app_database.dart';
import '../participants/participants_list_screen.dart';
import '../families/families_list_screen.dart';
import '../payments/payments_list_screen.dart';
import '../expenses/expenses_list_screen.dart';
import '../incomes/incomes_list_screen.dart';
import '../rulesets/rulesets_list_screen.dart';
import '../cash_status/cash_status_screen.dart';
import '../roles/roles_list_screen.dart';
import '../tasks/tasks_screen.dart';

/// Dashboard Screen
///
/// Hauptübersicht mit Statistiken und Schnellzugriff auf alle Funktionen
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentEvent = ref.watch(currentEventProvider);

    if (currentEvent == null) {
      // Sollte nicht passieren, aber als Fallback
      return const Scaffold(
        body: Center(
          child: Text('Kein Event ausgewählt'),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Dashboard'),
            Text(
              currentEvent.name,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.normal),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // TODO: Settings Screen
            },
          ),
        ],
      ),
      drawer: _buildDrawer(context, ref),
      body: _buildDashboardContent(context, ref, currentEvent),
    );
  }

  Widget _buildDrawer(BuildContext context, WidgetRef ref) {
    final currentEvent = ref.watch(currentEventProvider);

    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: BoxDecoration(
              color: Theme.of(context).primaryColor,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                const Icon(
                  Icons.event,
                  size: 48,
                  color: Colors.white,
                ),
                const SizedBox(height: 8),
                const Text(
                  'MGB Freizeitplaner',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (currentEvent != null)
                  Text(
                    currentEvent.name,
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                  ),
              ],
            ),
          ),
          ListTile(
            leading: const Icon(Icons.dashboard),
            title: const Text('Dashboard'),
            onTap: () => Navigator.of(context).pop(),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.people),
            title: const Text('Teilnehmer'),
            onTap: () {
              Navigator.of(context).pop();
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const ParticipantsListScreen(),
                ),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.family_restroom),
            title: const Text('Familien'),
            onTap: () {
              Navigator.of(context).pop();
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const FamiliesListScreen(),
                ),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.payment),
            title: const Text('Zahlungen'),
            onTap: () {
              Navigator.of(context).pop();
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const PaymentsListScreen(),
                ),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.shopping_cart),
            title: const Text('Ausgaben'),
            onTap: () {
              Navigator.of(context).pop();
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const ExpensesListScreen(),
                ),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.attach_money),
            title: const Text('Einnahmen'),
            onTap: () {
              Navigator.of(context).pop();
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const IncomesListScreen(),
                ),
              );
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.receipt_long),
            title: const Text('Kassenstand'),
            onTap: () {
              Navigator.of(context).pop();
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const CashStatusScreen(),
                ),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.rule),
            title: const Text('Regelwerke'),
            onTap: () {
              Navigator.of(context).pop();
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const RulesetsListScreen(),
                ),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.badge),
            title: const Text('Rollen'),
            onTap: () {
              Navigator.of(context).pop();
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const RolesListScreen(),
                ),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.task_alt),
            title: const Text('Aufgaben'),
            onTap: () {
              Navigator.of(context).pop();
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const TasksScreen(),
                ),
              );
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.event_note),
            title: const Text('Event wechseln'),
            onTap: () {
              ref.read(currentEventProvider.notifier).clearEvent();
              Navigator.of(context).pushReplacementNamed('/');
            },
          ),
        ],
      ),
    );
  }

  Widget _buildDashboardContent(
    BuildContext context,
    WidgetRef ref,
    Event currentEvent,
  ) {
    final database = ref.watch(databaseProvider);
    final eventId = currentEvent.id;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Event Info Card
          _buildEventInfoCard(context, currentEvent),
          const SizedBox(height: 24),

          // Statistics Cards
          const Text(
            'Übersicht',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),

          StreamBuilder<int>(
            stream: (database.select(database.participants)
                  ..where((tbl) => tbl.eventId.equals(eventId))
                  ..where((tbl) => tbl.isActive.equals(true)))
                .watch()
                .map((list) => list.length),
            builder: (context, snapshot) {
              final participantCount = snapshot.data ?? 0;

              return Row(
                children: [
                  Expanded(
                    child: _buildStatCard(
                      context,
                      'Teilnehmer',
                      participantCount.toString(),
                      Icons.people,
                      Colors.blue,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: StreamBuilder<int>(
                      stream: (database.select(database.families)
                            ..where((tbl) => tbl.eventId.equals(eventId)))
                          .watch()
                          .map((list) => list.length),
                      builder: (context, snapshot) {
                        final familyCount = snapshot.data ?? 0;
                        return _buildStatCard(
                          context,
                          'Familien',
                          familyCount.toString(),
                          Icons.family_restroom,
                          Colors.green,
                        );
                      },
                    ),
                  ),
                ],
              );
            },
          ),

          const SizedBox(height: 16),

          // Financial Overview - Payments and Expenses
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

              return Row(
                children: [
                  Expanded(
                    child: _buildStatCard(
                      context,
                      'Zahlungen',
                      NumberFormat.currency(locale: 'de_DE', symbol: '€').format(totalPayments),
                      Icons.payment,
                      Colors.blue,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: StreamBuilder<List<Expense>>(
                      stream: (database.select(database.expenses)
                            ..where((tbl) => tbl.eventId.equals(eventId))
                            ..where((tbl) => tbl.isActive.equals(true)))
                          .watch(),
                      builder: (context, snapshot) {
                        final expenses = snapshot.data ?? [];
                        final totalExpenses = expenses.fold<double>(
                          0.0,
                          (sum, expense) => sum + expense.amount,
                        );

                        return _buildStatCard(
                          context,
                          'Ausgaben',
                          NumberFormat.currency(locale: 'de_DE', symbol: '€').format(totalExpenses),
                          Icons.shopping_cart,
                          Colors.red,
                        );
                      },
                    ),
                  ),
                ],
              );
            },
          ),

          const SizedBox(height: 16),

          // Financial Overview - Incomes and Cash Balance
          StreamBuilder<List<Income>>(
            stream: (database.select(database.incomes)
                  ..where((tbl) => tbl.eventId.equals(eventId))
                  ..where((tbl) => tbl.isActive.equals(true)))
                .watch(),
            builder: (context, incomeSnapshot) {
              final incomes = incomeSnapshot.data ?? [];
              final totalIncomes = incomes.fold<double>(
                0.0,
                (sum, income) => sum + income.amount,
              );

              return StreamBuilder<List<Expense>>(
                stream: (database.select(database.expenses)
                      ..where((tbl) => tbl.eventId.equals(eventId))
                      ..where((tbl) => tbl.isActive.equals(true)))
                    .watch(),
                builder: (context, expenseSnapshot) {
                  final expenses = expenseSnapshot.data ?? [];
                  final totalExpenses = expenses.fold<double>(
                    0.0,
                    (sum, expense) => sum + expense.amount,
                  );
                  final cashBalance = totalIncomes - totalExpenses;

                  return Row(
                    children: [
                      Expanded(
                        child: _buildStatCard(
                          context,
                          'Einnahmen',
                          NumberFormat.currency(locale: 'de_DE', symbol: '€').format(totalIncomes),
                          Icons.attach_money,
                          Colors.green,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildStatCard(
                          context,
                          'Kassenstand',
                          NumberFormat.currency(locale: 'de_DE', symbol: '€').format(cashBalance),
                          Icons.account_balance_wallet,
                          cashBalance >= 0 ? Colors.teal : Colors.deepOrange,
                        ),
                      ),
                    ],
                  );
                },
              );
            },
          ),

          const SizedBox(height: 24),

          // Quick Actions
          const Text(
            'Schnellzugriff',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),

          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
            children: [
              _buildQuickActionCard(
                context,
                'Teilnehmer',
                Icons.people,
                Colors.blue,
                () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => const ParticipantsListScreen(),
                  ),
                ),
              ),
              _buildQuickActionCard(
                context,
                'Familien',
                Icons.family_restroom,
                Colors.green,
                () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => const FamiliesListScreen(),
                  ),
                ),
              ),
              _buildQuickActionCard(
                context,
                'Zahlungen',
                Icons.payment,
                Colors.orange,
                () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => const PaymentsListScreen(),
                  ),
                ),
              ),
              _buildQuickActionCard(
                context,
                'Ausgaben',
                Icons.shopping_cart,
                Colors.red,
                () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => const ExpensesListScreen(),
                  ),
                ),
              ),
              _buildQuickActionCard(
                context,
                'Einnahmen',
                Icons.attach_money,
                Colors.green[700]!,
                () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => const IncomesListScreen(),
                  ),
                ),
              ),
              _buildQuickActionCard(
                context,
                'Regelwerke',
                Icons.rule,
                Colors.purple,
                () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => const RulesetsListScreen(),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildEventInfoCard(BuildContext context, Event event) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              event.name,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                const Icon(Icons.calendar_today, size: 16, color: Colors.grey),
                const SizedBox(width: 4),
                Text(
                  '${_formatDate(event.startDate)} - ${_formatDate(event.endDate)}',
                  style: const TextStyle(color: Colors.grey),
                ),
              ],
            ),
            if (event.location != null) ...[
              const SizedBox(height: 4),
              Row(
                children: [
                  const Icon(Icons.location_on, size: 16, color: Colors.grey),
                  const SizedBox(width: 4),
                  Text(
                    event.location!,
                    style: const TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(
    BuildContext context,
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 20),
                const Spacer(),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              title,
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActionCard(
    BuildContext context,
    String title,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 48, color: color),
              const SizedBox(height: 8),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}.${date.month.toString().padLeft(2, '0')}.${date.year}';
  }
}
