import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/pdf_export_service.dart';

/// Provider for PdfExportService
final pdfExportServiceProvider = Provider<PdfExportService>((ref) {
  return PdfExportService();
});
