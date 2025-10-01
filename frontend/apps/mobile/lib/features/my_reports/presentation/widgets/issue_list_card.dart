// File: E:/civic-issue-reporter/apps/mobile/lib/features/my_reports/presentation/widgets/issue_list_card.dart

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:lucide_flutter/lucide_flutter.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../data/models/issue.dart';

class IssueListCard extends StatelessWidget {
  final Issue issue;

  const IssueListCard({super.key, required this.issue});

  // Helper function to get an icon based on category
  IconData _getCategoryIcon(String category) {
    switch (category.toLowerCase()) {
      case 'pothole':
        return Icons.alt_route; // or Icons.traffic
      case 'streetlight':
        return LucideIcons.lightbulb;
      case 'garbage':
        return LucideIcons.trash2;
      case 'water issue':
        return LucideIcons.droplets;
      default:
        return Icons.error_outline; // or Icons.warning_amber_rounded
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: () {
          // TODO: Navigate to a detailed issue view screen
        },
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Top Row: Category and Status
              Row(
                children: [
                  Icon(_getCategoryIcon(issue.category), size: 16, color: AppColors.textLight),
                  const SizedBox(width: 8),
                  Text(
                    issue.category,
                    style: const TextStyle(fontSize: 12, color: AppColors.textLight, fontWeight: FontWeight.bold),
                  ),
                  const Spacer(),
                  _StatusBadge(status: issue.status),
                ],
              ),
              const SizedBox(height: 12),

              // Middle: Description
              Text(
                issue.description,
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textDark),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 12),

              // Bottom Row: Date
              Row(
                children: [
                  const Icon(LucideIcons.calendar, size: 14, color: AppColors.textLight),
                  const SizedBox(width: 8),
                  Text(
                    'Reported on ${DateFormat.yMMMd().format(issue.createdAt)}',
                    style: const TextStyle(fontSize: 12, color: AppColors.textLight),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// A private widget for the status badge
class _StatusBadge extends StatelessWidget {
  final String status;
  const _StatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    final Color color;
    final String text;
    switch (status) {
      case 'in_progress':
        color = AppColors.warning;
        text = 'In Progress';
        break;
      case 'resolved':
        color = AppColors.success;
        text = 'Resolved';
        break;
      case 'new':
      default:
        color = AppColors.primary;
        text = 'New';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        text,
        style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold),
      ),
    );
  }
}