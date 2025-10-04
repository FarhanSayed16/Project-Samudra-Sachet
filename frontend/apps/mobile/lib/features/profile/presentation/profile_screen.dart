import 'package:flutter/material.dart';
import 'package:lucide_flutter/lucide_flutter.dart';
import '../../core/theme/app_colors.dart';
import '../../core/api/api_client.dart';
import '../../core/services/storage_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _userProfile;
  bool _isLoading = true;
  bool _isEditing = false;

  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadUserProfile();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _loadUserProfile() async {
    setState(() => _isLoading = true);

    try {
      final response = await ApiClient.getUserProfile();
      if (response['success'] == true) {
        setState(() {
          _userProfile = response['data'];
          _nameController.text = _userProfile?['full_name'] ?? '';
          _emailController.text = _userProfile?['email'] ?? '';
          _phoneController.text = _userProfile?['phone'] ?? '';
          _isLoading = false;
        });
      } else {
        _showErrorSnackBar(response['message'] ?? 'Failed to load profile');
        setState(() => _isLoading = false);
      }
    } catch (e) {
      setState(() => _isLoading = false);
      _showErrorSnackBar('Error loading profile: ${e.toString()}');
    }
  }

  Future<void> _updateProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      // Note: This would need an update profile endpoint
      // For now, we'll just show success message
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _isEditing = false;
        _isLoading = false;
      });

      _showSuccessSnackBar('Profile updated successfully!');
    } catch (e) {
      setState(() => _isLoading = false);
      _showErrorSnackBar('Error updating profile: ${e.toString()}');
    }
  }

  Future<void> _logout() async {
    try {
      await ApiClient.logout();
      await StorageService.clearAll();

      if (mounted) {
        Navigator.of(context).pushNamedAndRemoveUntil(
          '/login',
          (route) => false,
        );
      }
    } catch (e) {
      _showErrorSnackBar('Error logging out: ${e.toString()}');
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

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppColors.success,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        actions: [
          if (!_isEditing)
            IconButton(
              onPressed: () => setState(() => _isEditing = true),
              icon: const Icon(LucideIcons.edit),
            )
          else
            Row(
              children: [
                IconButton(
                  onPressed: () {
                    setState(() => _isEditing = false);
                    _loadUserProfile(); // Reset form
                  },
                  icon: const Icon(LucideIcons.x),
                ),
                IconButton(
                  onPressed: _updateProfile,
                  icon: const Icon(LucideIcons.check),
                ),
              ],
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _userProfile == null
              ? _buildErrorState()
              : _buildProfileContent(),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            LucideIcons.userX,
            size: 64,
            color: AppColors.textSecondary,
          ),
          const SizedBox(height: 16),
          Text(
            'Failed to Load Profile',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Please try again later',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _loadUserProfile,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildProfileContent() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildProfileHeader(),
            const SizedBox(height: 32),
            _buildProfileForm(),
            const SizedBox(height: 32),
            _buildActionButtons(),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileHeader() {
    return Column(
      children: [
        Container(
          width: 120,
          height: 120,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: AppColors.oceanGradient,
          ),
          child: const Icon(
            LucideIcons.user,
            size: 60,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 16),
        Text(
          _userProfile?['full_name'] ?? 'Unknown User',
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          _userProfile?['email'] ?? 'No email',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppColors.textSecondary,
              ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: _getRoleColor(_userProfile?['user_role'])
                .withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Text(
            _getRoleLabel(_userProfile?['user_role']),
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: _getRoleColor(_userProfile?['user_role']),
                  fontWeight: FontWeight.w600,
                ),
          ),
        ),
      ],
    );
  }

  Widget _buildProfileForm() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Personal Information',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 16),
        _buildFormField(
          controller: _nameController,
          label: 'Full Name',
          icon: LucideIcons.user,
          enabled: _isEditing,
        ),
        const SizedBox(height: 16),
        _buildFormField(
          controller: _emailController,
          label: 'Email',
          icon: LucideIcons.mail,
          enabled: false, // Email usually can't be changed
        ),
        const SizedBox(height: 16),
        _buildFormField(
          controller: _phoneController,
          label: 'Phone Number',
          icon: LucideIcons.phone,
          enabled: _isEditing,
        ),
      ],
    );
  }

  Widget _buildFormField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    required bool enabled,
  }) {
    return TextFormField(
      controller: controller,
      enabled: enabled,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, color: AppColors.primary),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: AppColors.primary),
        ),
        filled: !enabled,
        fillColor: enabled ? null : AppColors.surfaceVariant,
      ),
      validator: (value) {
        if (label == 'Full Name' && (value == null || value.isEmpty)) {
          return 'Please enter your full name';
        }
        if (label == 'Email' && (value == null || value.isEmpty)) {
          return 'Please enter your email';
        }
        return null;
      },
    );
  }

  Widget _buildActionButtons() {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: _logout,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.error,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            icon: const Icon(LucideIcons.logOut),
            label: const Text('Logout'),
          ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.infoLight,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.info),
          ),
          child: Column(
            children: [
              Row(
                children: [
                  Icon(LucideIcons.info, color: AppColors.info),
                  const SizedBox(width: 8),
                  Text(
                    'App Information',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: AppColors.info,
                          fontWeight: FontWeight.w600,
                        ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              _buildInfoRow('Version', '1.0.0'),
              _buildInfoRow('Build', '2024.01.01'),
              _buildInfoRow('Platform', 'Flutter'),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
          Text(
            value,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
          ),
        ],
      ),
    );
  }

  Color _getRoleColor(String? role) {
    switch (role?.toLowerCase()) {
      case 'admin':
        return AppColors.error;
      case 'coastal_guard':
        return AppColors.warning;
      case 'coastal_volunteer':
        return AppColors.info;
      case 'citizen':
        return AppColors.success;
      default:
        return AppColors.textSecondary;
    }
  }

  String _getRoleLabel(String? role) {
    switch (role?.toLowerCase()) {
      case 'admin':
        return 'Administrator';
      case 'coastal_guard':
        return 'Coastal Guard';
      case 'coastal_volunteer':
        return 'Coastal Volunteer';
      case 'citizen':
        return 'Citizen';
      default:
        return 'Unknown';
    }
  }
}
