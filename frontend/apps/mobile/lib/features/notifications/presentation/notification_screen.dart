import 'package:flutter/material.dart';
import 'package:lucide_flutter/lucide_flutter.dart';
import '../../core/theme/app_colors.dart';

class NotificationScreen extends StatefulWidget {
  const NotificationScreen({super.key});

  @override
  State<NotificationScreen> createState() => _NotificationScreenState();
}

class _NotificationScreenState extends State<NotificationScreen> {
  List<Map<String, dynamic>> _notifications = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadNotifications();
  }

  Future<void> _loadNotifications() async {
    setState(() => _isLoading = true);

    try {
      // Simulate loading notifications
      await Future.delayed(const Duration(seconds: 1));

      // Mock notifications data
      setState(() {
        _notifications = [
          {
            'id': '1',
            'title': 'New Hazard Report',
            'message':
                'A new tsunami warning has been reported near your location',
            'type': 'hazard',
            'timestamp': DateTime.now().subtract(const Duration(minutes: 30)),
            'isRead': false,
            'priority': 'high',
          },
          {
            'id': '2',
            'title': 'Report Verified',
            'message':
                'Your report about high waves has been verified by coastal guards',
            'type': 'verification',
            'timestamp': DateTime.now().subtract(const Duration(hours: 2)),
            'isRead': true,
            'priority': 'medium',
          },
          {
            'id': '3',
            'title': 'System Update',
            'message': 'The app has been updated with new features',
            'type': 'system',
            'timestamp': DateTime.now().subtract(const Duration(days: 1)),
            'isRead': true,
            'priority': 'low',
          },
        ];
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      _showErrorSnackBar('Failed to load notifications: ${e.toString()}');
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppColors.error,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _markAsRead(String notificationId) {
    setState(() {
      final index = _notifications.indexWhere((n) => n['id'] == notificationId);
      if (index != -1) {
        _notifications[index]['isRead'] = true;
      }
    });
  }

  void _markAllAsRead() {
    setState(() {
      for (var notification in _notifications) {
        notification['isRead'] = true;
      }
    });
  }

  void _deleteNotification(String notificationId) {
    setState(() {
      _notifications.removeWhere((n) => n['id'] == notificationId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        actions: [
          if (_notifications.any((n) => !n['isRead']))
            IconButton(
              onPressed: _markAllAsRead,
              icon: const Icon(LucideIcons.check),
            ),
          IconButton(
            onPressed: _loadNotifications,
            icon: const Icon(LucideIcons.refreshCw),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _notifications.isEmpty
              ? _buildEmptyState()
              : _buildNotificationsList(),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            LucideIcons.bell,
            size: 64,
            color: AppColors.textSecondary,
          ),
          const SizedBox(height: 16),
          Text(
            'No Notifications',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'You\'re all caught up!',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _loadNotifications,
            child: const Text('Refresh'),
          ),
        ],
      ),
    );
  }

  Widget _buildNotificationsList() {
    return RefreshIndicator(
      onRefresh: _loadNotifications,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _notifications.length,
        itemBuilder: (context, index) {
          final notification = _notifications[index];
          return _buildNotificationCard(notification);
        },
      ),
    );
  }

  Widget _buildNotificationCard(Map<String, dynamic> notification) {
    final isRead = notification['isRead'] as bool;
    final priority = notification['priority'] as String;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      color: isRead ? null : AppColors.infoLight.withValues(alpha: 0.3),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: _buildNotificationIcon(notification['type'], priority),
        title: Text(
          notification['title'],
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: isRead ? FontWeight.normal : FontWeight.w600,
              ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              notification['message'],
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textSecondary,
                  ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(
                  LucideIcons.clock,
                  size: 14,
                  color: AppColors.textSecondary,
                ),
                const SizedBox(width: 4),
                Text(
                  _formatTimestamp(notification['timestamp']),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.textSecondary,
                      ),
                ),
                const Spacer(),
                if (!isRead)
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      shape: BoxShape.circle,
                    ),
                  ),
              ],
            ),
          ],
        ),
        trailing: PopupMenuButton<String>(
          onSelected: (value) {
            switch (value) {
              case 'mark_read':
                _markAsRead(notification['id']);
                break;
              case 'delete':
                _deleteNotification(notification['id']);
                break;
            }
          },
          itemBuilder: (context) => [
            if (!isRead)
              const PopupMenuItem(
                value: 'mark_read',
                child: Row(
                  children: [
                    Icon(LucideIcons.check),
                    SizedBox(width: 8),
                    Text('Mark as Read'),
                  ],
                ),
              ),
            const PopupMenuItem(
              value: 'delete',
              child: Row(
                children: [
                  Icon(LucideIcons.trash2, color: AppColors.error),
                  SizedBox(width: 8),
                  Text('Delete'),
                ],
              ),
            ),
          ],
        ),
        onTap: () {
          if (!isRead) {
            _markAsRead(notification['id']);
          }
        },
      ),
    );
  }

  Widget _buildNotificationIcon(String type, String priority) {
    IconData icon;
    Color color;

    switch (type) {
      case 'hazard':
        icon = LucideIcons.triangleAlert;
        color = AppColors.error;
        break;
      case 'verification':
        icon = LucideIcons.checkCircle;
        color = AppColors.success;
        break;
      case 'system':
        icon = LucideIcons.settings;
        color = AppColors.info;
        break;
      default:
        icon = LucideIcons.bell;
        color = AppColors.textSecondary;
    }

    // Adjust color based on priority
    if (priority == 'high') {
      color = AppColors.error;
    } else if (priority == 'medium') {
      color = AppColors.warning;
    }

    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Icon(icon, color: color, size: 20),
    );
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }
}
