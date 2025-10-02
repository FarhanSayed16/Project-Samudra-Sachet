import 'package:flutter/material.dart';

class AppColors {
  // Primary Ocean Theme Colors
  static const Color primary = Color(0xFF0066CC); // Ocean Blue
  static const Color primaryLight = Color(0xFF4A90E2); // Light Ocean Blue
  static const Color primaryDark = Color(0xFF003D82); // Dark Ocean Blue

  // Secondary Colors
  static const Color secondary = Color(0xFF00B4DB); // Cyan
  static const Color accent = Color(0xFF7ED321); // Safety Green

  // Hazard Colors
  static const Color warning = Color(0xFFFF9500); // Orange
  static const Color danger = Color(0xFFFF3B30); // Red
  static const Color success = Color(0xFF34C759); // Green
  static const Color info = Color(0xFF007AFF); // Blue

  // Neutral Colors
  static const Color background = Color(0xFFF8FAFC); // Light Gray
  static const Color surface = Color(0xFFFFFFFF); // White
  static const Color surfaceVariant = Color(0xFFF1F5F9); // Light Gray

  // Text Colors
  static const Color textPrimary = Color(0xFF1E293B); // Dark Gray
  static const Color textSecondary = Color(0xFF64748B); // Medium Gray
  static const Color textLight = Color(0xFF94A3B8); // Light Gray

  // Border Colors
  static const Color border = Color(0xFFE2E8F0); // Light Border
  static const Color borderDark = Color(0xFFCBD5E1); // Dark Border

  // Status Colors
  static const Color error = Color(0xFFEF4444); // Red
  static const Color warningLight = Color(0xFFFEF3C7); // Light Yellow
  static const Color successLight = Color(0xFFD1FAE5); // Light Green
  static const Color infoLight = Color(0xFFDBEAFE); // Light Blue

  // Gradient Colors
  static const LinearGradient oceanGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primary, secondary],
  );

  static const LinearGradient safetyGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [success, accent],
  );
}

