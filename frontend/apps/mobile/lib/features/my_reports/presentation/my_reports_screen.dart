// File: E:/civic-issue-reporter/apps/mobile/lib/features/my_reports/presentation/my_reports_screen.dart

import 'package:flutter/material.dart';
import '../../../data/models/issue.dart';
import '../../issues/data/issue_repository.dart';
import 'widgets/issue_list_card.dart'; // 👈 Import the new reusable card

class MyReportsScreen extends StatefulWidget {
  const MyReportsScreen({super.key});

  @override
  State<MyReportsScreen> createState() => _MyReportsScreenState();
}

class _MyReportsScreenState extends State<MyReportsScreen> {
  final IssueRepository _issueRepository = IssueRepository();
  late Future<List<Issue>> _futureIssues;

  @override
  void initState() {
    super.initState();
    _futureIssues = _issueRepository.getMyIssues();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Reported Issues')),
      body: FutureBuilder<List<Issue>>(
        future: _futureIssues,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('You have not reported any issues yet.'));
          }

          final issues = snapshot.data!;
          return ListView.builder(
            itemCount: issues.length,
            itemBuilder: (context, index) {
              final issue = issues[index];
              // 👇 Use the new reusable widget
              return IssueListCard(issue: issue);
            },
          );
        },
      ),
    );
  }
}
