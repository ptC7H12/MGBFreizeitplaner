import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'screens/auth/event_selection_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize German locale for date formatting
  await initializeDateFormatting('de_DE', null);

  runApp(
    const ProviderScope(
      child: MGBFreizeitplanerApp(),
    ),
  );
}

class MGBFreizeitplanerApp extends StatelessWidget {
  const MGBFreizeitplanerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MGB Freizeitplaner',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.light,
        ),
        useMaterial3: true,

        // German-style date formatting
        // Additional theme customizations
        appBarTheme: const AppBarTheme(
          centerTitle: false,
          elevation: 0,
        ),

        cardTheme: CardTheme(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),

        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 12,
          ),
        ),

        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(
              horizontal: 24,
              vertical: 12,
            ),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
      ),

      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),

      // Start with event selection screen
      home: const EventSelectionScreen(),
    );
  }
}
