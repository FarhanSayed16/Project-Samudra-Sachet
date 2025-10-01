// File: E:/civic-issue-reporter/apps/mobile/lib/features/home/presentation/home_screen.dart
import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../data/models/issue.dart';
import '../../issues/data/issue_repository.dart';
import '../../profile/presentation/profile_screen.dart';
import '../../notifications/presentation/notification_screen.dart'; // 👈 Import NotificationScreen
import 'widgets/issue_card.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final IssueRepository _issueRepository = IssueRepository();
  late Future<List<Issue>> _futureIssues;

  String _activeFilter = 'My locality';
  final List<String> _filters = ['My locality', 'highly voted', 'India'];

  @override
  void initState() {
    super.initState();
    _futureIssues = _issueRepository.getPublicIssues();
  }

  void _onFilterTapped(String filter) {
    setState(() {
      _activeFilter = filter;
    });
    // TODO: Add logic to refetch issues based on the new filter
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('$filter selected')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            _buildCustomHeader(),

            // 🔹 Filters Row
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: _filters.map((filter) {
                  return _FilterPill(
                    text: filter,
                    isActive: filter == _activeFilter,
                    onTap: () => _onFilterTapped(filter),
                  );
                }).toList(),
              ),
            ),

            // 🔹 Issue List
            Expanded(
              child: FutureBuilder<List<Issue>>(
                future: _futureIssues,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (snapshot.hasError) {
                    return Center(child: Text('Error: ${snapshot.error}'));
                  }
                  if (!snapshot.hasData || snapshot.data!.isEmpty) {
                    return const Center(
                        child: Text('No issues found in your area.'));
                  }

                  final issues = snapshot.data!;
                  return ListView.builder(
                    itemCount: issues.length,
                    itemBuilder: (context, index) {
                      return IssueCard(issue: issues[index]);
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  // --- UPDATED Custom Header ---
  Widget _buildCustomHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(bottom: BorderSide(color: Color(0xFFEEEEEE))),
      ),
      child: Row(
        children: [
          // 👇 Profile Avatar -> ProfileScreen
          GestureDetector(
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (context) => const ProfileScreen()),
              );
            },
            child: const CircleAvatar(
              backgroundColor: AppColors.primary,
              child: Icon(Icons.person, color: Colors.white, size: 20),
            ),
          ),
          const SizedBox(width: 12),

          // 👇 Search Bar
          Expanded(
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Search',
                prefixIcon: const Icon(Icons.search,
                    color: AppColors.textLight, size: 20),
                filled: true,
                fillColor: AppColors.background,
                contentPadding: EdgeInsets.zero,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(30),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),

          // 👇 Notification Bell -> NotificationScreen
          IconButton(
            icon: const Icon(Icons.notifications_none,
                color: AppColors.textDark),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                    builder: (context) => const NotificationScreen()),
              );
            },
          ),
        ],
      ),
    );
  }
}

// --- FilterPill widget ---
class _FilterPill extends StatelessWidget {
  final String text;
  final bool isActive;
  final VoidCallback onTap;

  const _FilterPill({
    required this.text,
    this.isActive = false,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12.0),
        child: Text(
          text,
          style: TextStyle(
            fontSize: 16,
            fontWeight: isActive ? FontWeight.bold : FontWeight.w500,
            color: isActive ? AppColors.primary : AppColors.textLight,
          ),
        ),
      ),
    );
  }
}
