import 'dart:io';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:path_provider/path_provider.dart';
import 'package:intl/intl.dart';
import '../data/database/app_database.dart';
import '../utils/date_utils.dart';

class PdfExportService {
  /// Export participants list to PDF
  Future<String> exportParticipantsList({
    required List<Participant> participants,
    required String eventName,
  }) async {
    final pdf = pw.Document();

    pdf.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.all(32),
        build: (context) => [
          // Title
          pw.Header(
            level: 0,
            child: pw.Text(
              'Teilnehmerliste - $eventName',
              style: pw.TextStyle(fontSize: 24, fontWeight: pw.FontWeight.bold),
            ),
          ),
          pw.SizedBox(height: 20),

          // Summary
          pw.Text(
            'Erstellt am: ${DateFormat('dd.MM.yyyy HH:mm', 'de_DE').format(DateTime.now())}',
            style: const pw.TextStyle(color: PdfColors.grey600),
          ),
          pw.Text(
            'Anzahl Teilnehmer: ${participants.length}',
            style: pw.TextStyle(fontSize: 14, fontWeight: pw.FontWeight.bold),
          ),
          pw.SizedBox(height: 20),

          // Participants Table
          pw.Table.fromTextArray(
            context: context,
            headers: ['Nr', 'Name', 'Geburtsdatum', 'Alter', 'Preis (€)'],
            data: participants.asMap().entries.map((entry) {
              final index = entry.key;
              final p = entry.value;
              final age = AppDateUtils.calculateAge(p.birthDate);
              final price = p.manualPriceOverride ?? p.calculatedPrice;
              return [
                '${index + 1}',
                '${p.firstName} ${p.lastName}',
                AppDateUtils.formatGerman(p.birthDate),
                '$age',
                price.toStringAsFixed(2),
              ];
            }).toList(),
            headerStyle: pw.TextStyle(
              fontWeight: pw.FontWeight.bold,
              color: PdfColors.white,
            ),
            headerDecoration: const pw.BoxDecoration(color: PdfColors.blue),
            cellAlignment: pw.Alignment.centerLeft,
            cellHeight: 30,
          ),

          pw.SizedBox(height: 20),

          // Total Price
          pw.Container(
            alignment: pw.Alignment.centerRight,
            child: pw.Text(
              'Gesamtpreis: ${participants.fold<double>(0, (sum, p) => sum + (p.manualPriceOverride ?? p.calculatedPrice)).toStringAsFixed(2)} €',
              style: pw.TextStyle(fontSize: 16, fontWeight: pw.FontWeight.bold),
            ),
          ),
        ],
      ),
    );

    // Save file
    final directory = await getApplicationDocumentsDirectory();
    final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
    final fileName = 'teilnehmerliste_$timestamp.pdf';
    final file = File('${directory.path}/$fileName');
    await file.writeAsBytes(await pdf.save());

    return file.path;
  }

  /// Export participant details to PDF
  Future<String> exportParticipantDetails({
    required Participant participant,
    String? eventName,
  }) async {
    final pdf = pw.Document();

    pdf.addPage(
      pw.Page(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.all(32),
        build: (context) => pw.Column(
          crossAxisAlignment: pw.CrossAxisAlignment.start,
          children: [
            pw.Header(
              level: 0,
              child: pw.Text(
                'Teilnehmer-Details',
                style: pw.TextStyle(fontSize: 24, fontWeight: pw.FontWeight.bold),
              ),
            ),
            pw.SizedBox(height: 20),

            _buildSection('Persönliche Daten', [
              _buildField('Vorname', participant.firstName),
              _buildField('Nachname', participant.lastName),
              _buildField('Geburtsdatum', AppDateUtils.formatGerman(participant.birthDate)),
              _buildField('Alter', '${AppDateUtils.calculateAge(participant.birthDate)} Jahre'),
              if (participant.gender != null) _buildField('Geschlecht', participant.gender!),
            ]),

            pw.SizedBox(height: 15),

            _buildSection('Adresse', [
              if (participant.street != null && participant.houseNumber != null)
                _buildField('Straße', '${participant.street} ${participant.houseNumber}'),
              if (participant.postalCode != null && participant.city != null)
                _buildField('Ort', '${participant.postalCode} ${participant.city}'),
              if (participant.country != null) _buildField('Land', participant.country!),
            ]),

            pw.SizedBox(height: 15),

            _buildSection('Kontakt', [
              if (participant.email != null) _buildField('E-Mail', participant.email!),
              if (participant.phone != null) _buildField('Telefon', participant.phone!),
              if (participant.mobile != null) _buildField('Mobil', participant.mobile!),
            ]),

            pw.SizedBox(height: 15),

            _buildSection('Notfallkontakt', [
              if (participant.emergencyContactName != null)
                _buildField('Name', participant.emergencyContactName!),
              if (participant.emergencyContactPhone != null)
                _buildField('Telefon', participant.emergencyContactPhone!),
            ]),

            pw.SizedBox(height: 15),

            _buildSection('Preis', [
              _buildField(
                'Berechneter Preis',
                '${participant.calculatedPrice.toStringAsFixed(2)} €',
              ),
              if (participant.manualPriceOverride != null)
                _buildField(
                  'Manueller Preis',
                  '${participant.manualPriceOverride!.toStringAsFixed(2)} €',
                ),
            ]),
          ],
        ),
      ),
    );

    final directory = await getApplicationDocumentsDirectory();
    final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
    final fileName = 'teilnehmer_${participant.firstName}_${participant.lastName}_$timestamp.pdf';
    final file = File('${directory.path}/$fileName');
    await file.writeAsBytes(await pdf.save());

    return file.path;
  }

  /// Export financial report to PDF
  Future<String> exportFinancialReport({
    required String eventName,
    required double totalIncomes,
    required double totalExpenses,
    required double totalPayments,
    required Map<String, double> expensesByCategory,
    required Map<String, double> incomesBySource,
  }) async {
    final pdf = pw.Document();
    final balance = totalIncomes - totalExpenses;

    pdf.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.all(32),
        build: (context) => [
          // Title
          pw.Header(
            level: 0,
            child: pw.Text(
              'Finanzbericht - $eventName',
              style: pw.TextStyle(fontSize: 24, fontWeight: pw.FontWeight.bold),
            ),
          ),
          pw.SizedBox(height: 20),

          pw.Text(
            'Erstellt am: ${DateFormat('dd.MM.yyyy HH:mm', 'de_DE').format(DateTime.now())}',
            style: const pw.TextStyle(color: PdfColors.grey600),
          ),
          pw.SizedBox(height: 20),

          // Summary
          _buildFinancialSummary(totalIncomes, totalExpenses, totalPayments, balance),
          pw.SizedBox(height: 20),

          // Expenses by Category
          if (expensesByCategory.isNotEmpty) ...[
            pw.Text(
              'Ausgaben nach Kategorie',
              style: pw.TextStyle(fontSize: 16, fontWeight: pw.FontWeight.bold),
            ),
            pw.SizedBox(height: 10),
            _buildCategoryTable(expensesByCategory),
            pw.SizedBox(height: 20),
          ],

          // Incomes by Source
          if (incomesBySource.isNotEmpty) ...[
            pw.Text(
              'Einnahmen nach Quelle',
              style: pw.TextStyle(fontSize: 16, fontWeight: pw.FontWeight.bold),
            ),
            pw.SizedBox(height: 10),
            _buildCategoryTable(incomesBySource),
          ],
        ],
      ),
    );

    final directory = await getApplicationDocumentsDirectory();
    final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
    final fileName = 'finanzbericht_$timestamp.pdf';
    final file = File('${directory.path}/$fileName');
    await file.writeAsBytes(await pdf.save());

    return file.path;
  }

  pw.Widget _buildSection(String title, List<pw.Widget> fields) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(
          title,
          style: pw.TextStyle(fontSize: 14, fontWeight: pw.FontWeight.bold),
        ),
        pw.SizedBox(height: 5),
        ...fields,
      ],
    );
  }

  pw.Widget _buildField(String label, String value) {
    return pw.Padding(
      padding: const pw.EdgeInsets.only(bottom: 3),
      child: pw.Row(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
          pw.SizedBox(
            width: 150,
            child: pw.Text(
              '$label:',
              style: const pw.TextStyle(color: PdfColors.grey700),
            ),
          ),
          pw.Expanded(child: pw.Text(value)),
        ],
      ),
    );
  }

  pw.Widget _buildFinancialSummary(
    double totalIncomes,
    double totalExpenses,
    double totalPayments,
    double balance,
  ) {
    return pw.Container(
      decoration: pw.BoxDecoration(
        border: pw.Border.all(color: PdfColors.grey),
        borderRadius: const pw.BorderRadius.all(pw.Radius.circular(8)),
      ),
      padding: const pw.EdgeInsets.all(16),
      child: pw.Column(
        children: [
          _buildSummaryRow('Einnahmen', totalIncomes, PdfColors.green),
          pw.Divider(),
          _buildSummaryRow('Ausgaben', totalExpenses, PdfColors.red),
          pw.Divider(),
          _buildSummaryRow('Zahlungen', totalPayments, PdfColors.blue),
          pw.Divider(thickness: 2),
          _buildSummaryRow(
            'Kassenstand',
            balance,
            balance >= 0 ? PdfColors.teal : PdfColors.orange,
          ),
        ],
      ),
    );
  }

  pw.Widget _buildSummaryRow(String label, double amount, PdfColor color) {
    final formatter = NumberFormat.currency(locale: 'de_DE', symbol: '€');
    return pw.Row(
      mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
      children: [
        pw.Text(label, style: pw.TextStyle(fontSize: 12, color: color)),
        pw.Text(
          formatter.format(amount),
          style: pw.TextStyle(
            fontSize: 12,
            fontWeight: pw.FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  pw.Widget _buildCategoryTable(Map<String, double> data) {
    final formatter = NumberFormat.currency(locale: 'de_DE', symbol: '€');
    return pw.Table.fromTextArray(
      headers: ['Kategorie', 'Betrag'],
      data: data.entries.map((e) => [e.key, formatter.format(e.value)]).toList(),
      headerStyle: pw.TextStyle(fontWeight: pw.FontWeight.bold),
      cellAlignment: pw.Alignment.centerLeft,
    );
  }
}
