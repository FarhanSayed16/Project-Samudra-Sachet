// File: E:/civic-issue-reporter/apps/mobile/lib/features/home/presentation/widgets/issue_card.dart

import 'package:flutter/material.dart';
import 'package:lucide_flutter/lucide_flutter.dart';
import '../../../../data/models/issue.dart';
import '../../../../core/theme/app_colors.dart';

class IssueCard extends StatelessWidget {
  final Issue issue;
  const IssueCard({super.key, required this.issue});

  // Helper to get an icon based on category
  IconData _getCategoryIcon(String category) {
    // ... same as before
    switch (category.toLowerCase()) {
      case 'pothole': return LucideIcons.milestone;
      case 'streetlight': return LucideIcons.lightbulb;
      case 'garbage': return LucideIcons.trash2;
      case 'water': return LucideIcons.droplets;
      default: return LucideIcons.circleAlert;
    }
  }

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () {
        // TODO: Navigate to the full Issue Details page
        print("Tapped on Issue #${issue.id}");
      },
      child: Container(
        padding: const EdgeInsets.all(16.0),
        decoration: const BoxDecoration(
          color: Colors.white,
          border: Border(bottom: BorderSide(color: Color(0xFFF0F2F5), width: 1.0)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // --- Card Header ---
            Row( /* ... same as before ... */ ),
            const SizedBox(height: 8),

            // --- Issue Content ---
            Text(issue.description, style: const TextStyle(fontSize: 16, height: 1.4)),
            const SizedBox(height: 12),

            // --- NEW: Image Display ---
            if (issue.imageUrl != null && issue.imageUrl!.isNotEmpty)
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.network(
                  issue.imageUrl!,
                  fit: BoxFit.cover,
                  // Show a loader while the image is loading
                  loadingBuilder: (context, child, loadingProgress) {
                    if (loadingProgress == null) return child;
                    return const Center(child: CircularProgressIndicator());
                  },
                  // Show an error icon if the image fails to load
                  errorBuilder: (context, error, stackTrace) {
                    return const Icon(Icons.broken_image, color: Colors.grey, size: 48);
                  },
                ),
              ),
            const SizedBox(height: 12),

            // --- UPDATED: Interactive Action Bar ---
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _StatIcon(
                  icon: LucideIcons.trendingUp,
                  text: issue.upvoteCount.toString(),
                  onTap: () => ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Upvote feature coming soon!'))),
                ),
                _StatIcon(
                  icon: LucideIcons.repeat,
                  text: issue.shareCount.toString(),
                  onTap: () => ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Reshare feature coming soon!'))),
                ),
                _StatIcon(icon: _getCategoryIcon(issue.category), text: issue.category),
                IconButton(
                  icon: const Icon(LucideIcons.share2, color: AppColors.textLight, size: 20),
                  onPressed: () => ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Share to social media coming soon!'))),
                ),
              ],
            ),

            if (issue.status == 'resolved') ...[ /* ... same as before ... */ ]
          ],
        ),
      ),
    );
  }
}

// Updated helper widget for the stat icons to be tappable
class _StatIcon extends StatelessWidget {
  final IconData icon;
  final String text;
  final VoidCallback? onTap; // Make onTap optional

  const _StatIcon({required this.icon, required this.text, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container( // Wrap with container for a larger tap area
        color: Colors.transparent, // Makes the container itself invisible
        padding: const EdgeInsets.symmetric(vertical: 4.0, horizontal: 2.0),
        child: Row(
          children: [
            Icon(icon, size: 18, color: AppColors.textLight),
            const SizedBox(width: 6),
            Text(text, style: const TextStyle(color: AppColors.textLight, fontWeight: FontWeight.w500)),
          ],
        ),
      ),
    );
  }
}