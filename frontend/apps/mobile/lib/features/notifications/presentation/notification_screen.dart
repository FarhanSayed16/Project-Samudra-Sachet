// File: E:/civic-issue-reporter/apps/mobile/lib/features/notifications/presentation/notification_screen.dart

import 'package:flutter/material.dart';
import 'package:timeago/timeago.dart' as timeago;
import '../../../core/theme/app_colors.dart';

class NotificationScreen extends StatelessWidget {
  const NotificationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Mock data for the notification list
    final List<Map<String, dynamic>> notifications = [
      {'type': 'resolved', 'actor': 'Nagar Sevak', 'issue': 'irregular water supply issue', 'time': DateTime.now().subtract(const Duration(hours: 1))},
      {'type': 'repost', 'actor': 'Robert Doe', 'issue': 'irregular water supply issue', 'time': DateTime.now().subtract(const Duration(hours: 3))},
      {'type': 'upvote', 'actor': 'Alok Chauhan', 'issue': 'irregular water supply issue', 'time': DateTime.now().subtract(const Duration(hours: 5))},
      {'type': 'status_update', 'actor': 'Nagar Sevak', 'issue': 'Your issue is under review, assigned to municipal officer', 'time': DateTime.now().subtract(const Duration(hours: 7))},
    ];

    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Notification'),
          actions: [IconButton(icon: const Icon(Icons.settings_outlined), onPressed: () {})],
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Recent activity'),
              Tab(text: 'Unread'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            // Recent Activity Tab
            _NotificationList(notifications: notifications),
            // Unread Tab (using same data for demo)
            _NotificationList(notifications: notifications.where((n) => n['type'] != 'resolved').toList()),
          ],
        ),
      ),
    );
  }
}

class _NotificationList extends StatelessWidget {
  final List<Map<String, dynamic>> notifications;
  const _NotificationList({required this.notifications});

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      itemCount: notifications.length + 1, // +1 for the footer
      separatorBuilder: (context, index) => const Divider(height: 1),
      itemBuilder: (context, index) {
        if (index == notifications.length) {
          return const Padding(
            padding: EdgeInsets.symmetric(vertical: 24.0),
            child: Text(
              "That's all your notification from last 30 days",
              textAlign: TextAlign.center,
              style: TextStyle(color: AppColors.textLight),
            ),
          );
        }
        final notification = notifications[index];
        return _NotificationItem(notification: notification);
      },
    );
  }
}

class _NotificationItem extends StatelessWidget {
  final Map<String, dynamic> notification;
  const _NotificationItem({required this.notification});

  @override
  Widget build(BuildContext context) {
    String message = '';
    switch(notification['type']) {
      case 'resolved': message = 'resolved'; break;
      case 'repost': message = 'reposted the'; break;
      case 'upvote': message = 'upvoted the'; break;
      case 'status_update': message = ''; break;
    }

    return ListTile(
      leading: CircleAvatar(
        backgroundColor: AppColors.primary.withOpacity(0.1),
        foregroundColor: AppColors.primary,
        child: Text(
          notification['actor'].split(' ').map((e) => e[0]).join(),
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
      title: RichText(
        text: TextSpan(
          style: DefaultTextStyle.of(context).style,
          children: <TextSpan>[
            TextSpan(text: notification['actor'], style: const TextStyle(fontWeight: FontWeight.bold)),
            TextSpan(text: ' $message '),
            TextSpan(text: notification['issue']),
          ],
        ),
      ),
      subtitle: Padding(
        padding: const EdgeInsets.only(top: 4.0),
        child: Text(timeago.format(notification['time'])),
      ),
    );
  }
}