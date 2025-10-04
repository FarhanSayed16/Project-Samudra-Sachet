import 'package:flutter/material.dart';
import 'package:lucide_flutter/lucide_flutter.dart';
import '../../core/theme/app_colors.dart';
import '../../core/api/api_client.dart';

class MyReportsScreen extends StatefulWidget {
  const MyReportsScreen({super.key});

  @override
  State<MyReportsScreen> createState() => _MyReportsScreenState();
}

class _MyReportsScreenState extends State<MyReportsScreen> {
  List<Map<String, dynamic>> _reports = [];
  bool _isLoading = true;
  String _selectedFilter = 'all';

  final List<String> _filters = ['all', 'pending', 'verified', 'rejected'];

  @override
  void initState() {
    super.initState();
    _loadReports();
  }

  Future<void> _loadReports() async {
    setState(() => _isLoading = true);

    try {
      // Note: This would need a user-specific reports endpoint
      // For now, we'll use the public reports endpoint
      final reports = await ApiClient.getPublicReports(limit: 50);
      setState(() {
        _reports = reports;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      _showErrorSnackBar('Failed to load reports: ${e.toString()}');
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

  List<Map<String, dynamic>> _getFilteredReports() {
    if (_selectedFilter == 'all') return _reports;

    return _reports
        .where((report) =>
            report['status']?.toLowerCase() == _selectedFilter.toLowerCase())
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Reports'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            onPressed: _loadReports,
            icon: const Icon(LucideIcons.refreshCw),
          ),
        ],
      ),
      body: Column(
        children: [
          _buildFilters(),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _reports.isEmpty
                    ? _buildEmptyState()
                    : _buildReportsList(),
          ),
        ],
      ),
    );
  }

  Widget _buildFilters() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        border: Border(
          bottom: BorderSide(color: AppColors.border),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: DropdownButtonFormField<String>(
              value: _selectedFilter,
              decoration: InputDecoration(
                labelText: 'Filter by Status',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 8,
                ),
              ),
              items: _filters.map((filter) {
                String label;
                switch (filter) {
                  case 'all':
                    label = 'All Reports';
                    break;
                  case 'pending':
                    label = 'Pending';
                    break;
                  case 'verified':
                    label = 'Verified';
                    break;
                  case 'rejected':
                    label = 'Rejected';
                    break;
                  default:
                    label = filter;
                }
                return DropdownMenuItem(
                  value: filter,
                  child: Text(label),
                );
              }).toList(),
              onChanged: (value) {
                setState(() => _selectedFilter = value!);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            LucideIcons.fileText,
            size: 64,
            color: AppColors.textSecondary,
          ),
          const SizedBox(height: 16),
          Text(
            'No Reports Found',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Submit your first hazard report',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () {
              // Navigate to report screen
              Navigator.of(context).pushNamed('/report');
            },
            icon: const Icon(LucideIcons.plus),
            label: const Text('Create Report'),
          ),
        ],
      ),
    );
  }

  Widget _buildReportsList() {
    final filteredReports = _getFilteredReports();

    return RefreshIndicator(
      onRefresh: _loadReports,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: filteredReports.length,
        itemBuilder: (context, index) {
          final report = filteredReports[index];
          return _buildReportCard(report);
        },
      ),
    );
  }

  Widget _buildReportCard(Map<String, dynamic> report) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildReportHeader(report),
            const SizedBox(height: 12),
            _buildReportContent(report),
            const SizedBox(height: 12),
            _buildReportFooter(report),
          ],
        ),
      ),
    );
  }

  Widget _buildReportHeader(Map<String, dynamic> report) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color:
                _getHazardColor(report['hazard_type']).withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            report['hazard_type'] ?? 'Unknown',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: _getHazardColor(report['hazard_type']),
                  fontWeight: FontWeight.w600,
                ),
          ),
        ),
        const Spacer(),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: _getStatusColor(report['status']).withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            report['status'] ?? 'Unknown',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: _getStatusColor(report['status']),
                  fontWeight: FontWeight.w600,
                ),
          ),
        ),
      ],
    );
  }

  Widget _buildReportContent(Map<String, dynamic> report) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (report['description'] != null && report['description'].isNotEmpty)
          Text(
            report['description'],
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        const SizedBox(height: 8),
        Row(
          children: [
            Icon(LucideIcons.mapPin, size: 16, color: AppColors.textSecondary),
            const SizedBox(width: 4),
            Text(
              '${report['latitude']?.toStringAsFixed(4) ?? 'N/A'}, ${report['longitude']?.toStringAsFixed(4) ?? 'N/A'}',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.textSecondary,
                  ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildReportFooter(Map<String, dynamic> report) {
    return Row(
      children: [
        Icon(LucideIcons.clock, size: 16, color: AppColors.textSecondary),
        const SizedBox(width: 4),
        Text(
          _formatDate(report['created_at']),
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppColors.textSecondary,
              ),
        ),
        const Spacer(),
        if (report['severity_level'] != null)
          Row(
            children: [
              Icon(LucideIcons.alertTriangle,
                  size: 16, color: AppColors.warning),
              const SizedBox(width: 4),
              Text(
                'Level ${report['severity_level']}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppColors.warning,
                      fontWeight: FontWeight.w600,
                    ),
              ),
            ],
          ),
      ],
    );
  }

  Color _getHazardColor(String? hazardType) {
    switch (hazardType?.toLowerCase()) {
      case 'high_waves':
        return AppColors.warning;
      case 'storm':
        return AppColors.danger;
      case 'tsunami':
        return AppColors.error;
      case 'flooding':
        return AppColors.info;
      default:
        return AppColors.textSecondary;
    }
  }

  Color _getStatusColor(String? status) {
    switch (status?.toLowerCase()) {
      case 'verified':
        return AppColors.success;
      case 'pending':
        return AppColors.warning;
      case 'rejected':
        return AppColors.error;
      default:
        return AppColors.textSecondary;
    }
  }

  String _formatDate(String? dateString) {
    if (dateString == null) return 'Unknown';
    try {
      final date = DateTime.parse(dateString);
      final now = DateTime.now();
      final difference = now.difference(date);

      if (difference.inDays > 0) {
        return '${difference.inDays}d ago';
      } else if (difference.inHours > 0) {
        return '${difference.inHours}h ago';
      } else if (difference.inMinutes > 0) {
        return '${difference.inMinutes}m ago';
      } else {
        return 'Just now';
      }
    } catch (e) {
      return 'Unknown';
    }
  }
}
