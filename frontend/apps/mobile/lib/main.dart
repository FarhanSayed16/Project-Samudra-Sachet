// File: E:/civic-issue-reporter/apps/mobile/lib/main.dart

import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart'; // 👈 Import your new theme file
import 'features/auth/presentation/login_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Civic Reporter',
      // 👇 Apply the custom light theme for the whole app
      theme: AppTheme.lightTheme,
      home: const LoginScreen(),
    );
  }
}
