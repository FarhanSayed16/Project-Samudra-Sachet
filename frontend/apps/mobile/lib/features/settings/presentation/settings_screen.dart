// File: E:/civic-issue-reporter/apps/mobile/lib/features/settings/presentation/settings_screen.dart

import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Settings & Privacy'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        children: [
          const _SectionHeader(title: 'General'),
          _SettingsTile(
            title: '@AnanyaRanchi',
            onTap: () {},
          ),
          const Divider(height: 1),
          const _SectionHeader(title: 'Account'),
          _SettingsTile(
            title: 'Account Information',
            onTap: () {},
          ),
          _SettingsTile(
            title: 'Privacy and safety',
            onTap: () {},
          ),
          const Divider(height: 1),
          const _SectionHeader(title: 'Content & Display'),
          _SettingsTile(
            title: 'Notifications',
            onTap: () {},
          ),
          _SettingsTile(
            title: 'Content preferences',
            onTap: () {},
          ),
          _SettingsTile(
            title: 'Display and sound',
            onTap: () {},
            showArrow: true,
          ),
          _SettingsTile(
            title: 'Data usage',
            onTap: () {},
            showArrow: true,
          ),
          _SettingsTile(
            title: 'Accessibility',
            onTap: () {},
            showArrow: true,
          ),
          const Divider(height: 1),
          _SettingsTile(
            title: 'About Civic Reporter',
            onTap: () {},
            showArrow: true,
          ),
        ],
      ),
    );
  }
}

// Helper widget for section headers
class _SectionHeader extends StatelessWidget {
  final String title;
  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 20, 16, 8),
      child: Text(
        title,
        style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 16),
      ),
    );
  }
}

// Helper widget for each setting item
class _SettingsTile extends StatelessWidget {
  final String title;
  final VoidCallback onTap;
  final bool showArrow;

  const _SettingsTile({
    required this.title,
    required this.onTap,
    this.showArrow = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      child: ListTile(
        title: Text(title),
        trailing: showArrow ? const Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey) : null,
        onTap: onTap,
      ),
    );
  }
}