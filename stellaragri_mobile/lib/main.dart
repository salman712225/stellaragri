import 'package:flutter/material.dart';
import 'core/theme.dart';
import 'screens/home_advisory_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const StellarAgriApp());
}

class StellarAgriApp extends StatelessWidget {
  const StellarAgriApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Stellar Agri AI',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const HomeAdvisoryScreen(),
    );
  }
}
