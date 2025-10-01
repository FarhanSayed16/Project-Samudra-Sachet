// File: E:/civic-issue-reporter/apps/mobile/lib/features/profile/presentation/profile_screen.dart

import 'package:flutter/material.dart';
import 'package:percent_indicator/circular_percent_indicator.dart';
import '../../../core/theme/app_colors.dart';
import '../../settings/presentation/settings_screen.dart'; // We will create this next

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Mock data based on your design
    const user = {
      "name": "Ananya Singh",
      "handle": "@AnanyaRanchi",
      "avatarUrl": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=face",
      "issuesReported": 69,
      "followers": 1500,
      "following": 250,
      "trustScore": 1.0, // 1.0 means 100%
    };

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        leading: const BackButton(),
        title: const Text('Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (context) => const SettingsScreen()),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // User Info Section
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 24.0),
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 50,
                    backgroundImage: NetworkImage(user["avatarUrl"] as String),
                  ),
                  const SizedBox(height: 12),
                  Text(user["name"] as String, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                  Text(user["handle"] as String, style: const TextStyle(fontSize: 16, color: AppColors.textLight)),
                ],
              ),
            ),

            // Stats Row
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _StatItem(count: user["issuesReported"] as int, label: 'Issues Reported'),
                  _StatItem(count: user["followers"] as int, label: 'Followers'),
                  _StatItem(count: user["following"] as int, label: 'Following'),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // Trust Score Gauge
            CircularPercentIndicator(
              radius: 100.0,
              lineWidth: 15.0,
              percent: user["trustScore"] as double,
              center: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    "${((user["trustScore"] as double) * 100).toInt()}%",
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 40.0, color: AppColors.success),
                  ),
                  const Text(
                    "Trust score",
                    style: TextStyle(fontSize: 16.0, color: AppColors.textLight),
                  )
                ],
              ),
              circularStrokeCap: CircularStrokeCap.round,
              backgroundColor: Colors.green.shade100,
              progressColor: AppColors.success,
            ),
          ],
        ),
      ),
    );
  }
}

// Helper widget for the stat items
class _StatItem extends StatelessWidget {
  final int count;
  final String label;
  const _StatItem({required this.count, required this.label});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(count.toString(), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        Text(label, style: const TextStyle(fontSize: 12, color: AppColors.textLight)),
      ],
    );
  }
}