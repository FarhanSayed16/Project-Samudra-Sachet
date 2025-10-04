import 'package:flutter/material.dart';
import 'package:lucide_flutter/lucide_flutter.dart';
import '../../core/theme/app_colors.dart';
import '../../core/api/api_client.dart';

class SocialMediaScreen extends StatefulWidget {
  const SocialMediaScreen({super.key});

  @override
  State<SocialMediaScreen> createState() => _SocialMediaScreenState();
}

class _SocialMediaScreenState extends State<SocialMediaScreen> {
  List<Map<String, dynamic>> _posts = [];
  bool _isLoading = true;
  String _selectedFilter = 'all';
  String _selectedPlatform = 'all';

  final List<String> _filters = ['all', 'high_relevance', 'recent'];
  final List<String> _platforms = ['all', 'twitter', 'facebook', 'instagram'];

  @override
  void initState() {
    super.initState();
    _loadPosts();
  }

  Future<void> _loadPosts() async {
    setState(() => _isLoading = true);

    try {
      final posts = await ApiClient.getSocialMediaPosts(limit: 50);
      setState(() {
        _posts = posts;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      _showErrorSnackBar('Failed to load posts: ${e.toString()}');
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

  List<Map<String, dynamic>> _getFilteredPosts() {
    List<Map<String, dynamic>> filtered = List.from(_posts);

    // Filter by platform
    if (_selectedPlatform != 'all') {
      filtered = filtered
          .where((post) =>
              post['source']?.toLowerCase() == _selectedPlatform.toLowerCase())
          .toList();
    }

    // Filter by relevance
    if (_selectedFilter == 'high_relevance') {
      filtered = filtered
          .where((post) => (post['relevance_score'] ?? 0) > 0.7)
          .toList();
    } else if (_selectedFilter == 'recent') {
      filtered.sort((a, b) {
        final aTime =
            DateTime.tryParse(a['post_timestamp'] ?? '') ?? DateTime(1970);
        final bTime =
            DateTime.tryParse(b['post_timestamp'] ?? '') ?? DateTime(1970);
        return bTime.compareTo(aTime);
      });
    }

    return filtered;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Social Media'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            onPressed: _loadPosts,
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
                : _posts.isEmpty
                    ? _buildEmptyState()
                    : _buildPostsList(),
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
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  value: _selectedPlatform,
                  decoration: InputDecoration(
                    labelText: 'Platform',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 8,
                    ),
                  ),
                  items: _platforms.map((platform) {
                    return DropdownMenuItem(
                      value: platform,
                      child: Text(platform == 'all'
                          ? 'All Platforms'
                          : platform.toUpperCase()),
                    );
                  }).toList(),
                  onChanged: (value) {
                    setState(() => _selectedPlatform = value!);
                  },
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: DropdownButtonFormField<String>(
                  value: _selectedFilter,
                  decoration: InputDecoration(
                    labelText: 'Filter',
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
                        label = 'All Posts';
                        break;
                      case 'high_relevance':
                        label = 'High Relevance';
                        break;
                      case 'recent':
                        label = 'Most Recent';
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
            LucideIcons.messageCircle,
            size: 64,
            color: AppColors.textSecondary,
          ),
          const SizedBox(height: 16),
          Text(
            'No Social Media Posts',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Check back later for updates',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _loadPosts,
            child: const Text('Refresh'),
          ),
        ],
      ),
    );
  }

  Widget _buildPostsList() {
    final filteredPosts = _getFilteredPosts();

    return RefreshIndicator(
      onRefresh: _loadPosts,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: filteredPosts.length,
        itemBuilder: (context, index) {
          final post = filteredPosts[index];
          return _buildPostCard(post);
        },
      ),
    );
  }

  Widget _buildPostCard(Map<String, dynamic> post) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildPostHeader(post),
            const SizedBox(height: 12),
            _buildPostContent(post),
            const SizedBox(height: 12),
            _buildPostFooter(post),
          ],
        ),
      ),
    );
  }

  Widget _buildPostHeader(Map<String, dynamic> post) {
    return Row(
      children: [
        _getPlatformIcon(post['source']),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                post['author_username'] ?? 'Unknown User',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
              ),
              Text(
                '@${post['author_username'] ?? 'unknown'}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppColors.textSecondary,
                    ),
              ),
            ],
          ),
        ),
        Text(
          _formatDate(post['post_timestamp']),
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppColors.textSecondary,
              ),
        ),
      ],
    );
  }

  Widget _buildPostContent(Map<String, dynamic> post) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (post['post_text'] != null)
          Text(
            post['post_text'],
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        if (post['post_text'] != null && post['media_url'] != null)
          const SizedBox(height: 12),
        if (post['media_url'] != null)
          Container(
            height: 200,
            width: double.infinity,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              color: AppColors.surfaceVariant,
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(
                post['media_url'],
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(LucideIcons.image, color: AppColors.textSecondary),
                        const SizedBox(height: 8),
                        Text(
                          'Image unavailable',
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: AppColors.textSecondary,
                                  ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildPostFooter(Map<String, dynamic> post) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: AppColors.infoLight,
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            post['source']?.toUpperCase() ?? 'UNKNOWN',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppColors.info,
                  fontWeight: FontWeight.w600,
                ),
          ),
        ),
        const Spacer(),
        if (post['relevance_score'] != null)
          Row(
            children: [
              Icon(LucideIcons.star, size: 16, color: AppColors.warning),
              const SizedBox(width: 4),
              Text(
                '${(post['relevance_score'] * 100).toStringAsFixed(0)}%',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppColors.warning,
                      fontWeight: FontWeight.w600,
                    ),
              ),
            ],
          ),
        const SizedBox(width: 12),
        if (post['sentiment'] != null)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color:
                  _getSentimentColor(post['sentiment']).withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              post['sentiment'].toString().toUpperCase(),
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: _getSentimentColor(post['sentiment']),
                    fontWeight: FontWeight.w600,
                  ),
            ),
          ),
      ],
    );
  }

  Widget _getPlatformIcon(String? platform) {
    IconData icon;
    Color color;

    switch (platform?.toLowerCase()) {
      case 'twitter':
        icon = LucideIcons.twitter;
        color = const Color(0xFF1DA1F2);
        break;
      case 'facebook':
        icon = LucideIcons.facebook;
        color = const Color(0xFF1877F2);
        break;
      case 'instagram':
        icon = LucideIcons.instagram;
        color = const Color(0xFFE4405F);
        break;
      default:
        icon = LucideIcons.messageCircle;
        color = AppColors.primary;
    }

    return Icon(icon, color: color, size: 20);
  }

  Color _getSentimentColor(String? sentiment) {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return AppColors.success;
      case 'negative':
        return AppColors.error;
      case 'neutral':
        return AppColors.textSecondary;
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
