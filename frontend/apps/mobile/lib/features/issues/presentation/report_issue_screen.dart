// File: E:/civic-issue-reporter/apps/mobile/lib/features/issues/presentation/report_issue_screen.dart

import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart'; // For reverse geocoding
import 'package:image_picker/image_picker.dart';
import 'package:lucide_flutter/lucide_flutter.dart';
import 'package:share_plus/share_plus.dart'; // For social sharing
import '../../../core/theme/app_colors.dart';
import '../data/issue_repository.dart';

class ReportIssueScreen extends StatefulWidget {
  const ReportIssueScreen({super.key});

  @override
  State<ReportIssueScreen> createState() => _ReportIssueScreenState();
}

class _ReportIssueScreenState extends State<ReportIssueScreen> {
  final _formKey = GlobalKey<FormState>();
  final _descriptionController = TextEditingController();
  final _issueRepository = IssueRepository();

  Uint8List? _imageBytes;
  String? _imageFileName;
  Position? _currentPosition;
  String _locationDisplay = 'Fetching location...'; // Display for location
  String _selectedCategory = 'Pothole'; // Default category
  String _selectedUrgency = 'Medium'; // Default urgency
  bool _postAnonymously = false;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    final pickedFile = await ImagePicker().pickImage(source: source, imageQuality: 80);
    if (pickedFile != null) {
      final bytes = await pickedFile.readAsBytes();
      setState(() {
        _imageBytes = bytes;
        _imageFileName = pickedFile.name;
      });
    }
  }

  Future<void> _getCurrentLocation() async {
    // ... (permission logic remains the same)
    setState(() { _locationDisplay = 'Getting your precise location...'; });
    try {
      Position position = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
      setState(() { _currentPosition = position; });

      // --- UPDATED Resilient Geocoding ---
      try {
        List<Placemark> placemarks = await placemarkFromCoordinates(position.latitude, position.longitude);
        if (placemarks.isNotEmpty) {
          Placemark place = placemarks.first;
          setState(() {
            _locationDisplay = "${place.locality}, ${place.administrativeArea}";
          });
        }
      } catch (e) {
        // If reverse geocoding fails, just show the coordinates
        setState(() {
          _locationDisplay = 'Location: ${position.latitude.toStringAsFixed(4)}, ${position.longitude.toStringAsFixed(4)}';
        });
      }
      // --- End of Update ---

    } catch (e) {
      if (mounted) _showSnackBar('Failed to get location: $e', isError: true);
    }
  }
  Future<void> _reverseGeocode(Position position) async {
    try {
      List<Placemark> placemarks = await placemarkFromCoordinates(position.latitude, position.longitude);
      if (placemarks.isNotEmpty) {
        Placemark place = placemarks.first;
        setState(() {
          _locationDisplay = "${place.locality}, ${place.administrativeArea}";
        });
      } else {
        setState(() { _locationDisplay = 'Location: ${position.latitude.toStringAsFixed(4)}, ${position.longitude.toStringAsFixed(4)}'; });
      }
    } catch (e) {
      if (mounted) _showSnackBar('Failed to reverse geocode: $e', isError: true);
      setState(() { _locationDisplay = 'Location: ${position.latitude.toStringAsFixed(4)}, ${position.longitude.toStringAsFixed(4)}'; });
    }
  }

  // --- NEW: Simulate AI description generation ---
  void _magicWrite() async {
    if (_descriptionController.text.isNotEmpty) {
      _showSnackBar('AI Magic Write not yet implemented. Try writing more or clear the field!', isError: true);
      return;
    }
    setState(() { _isLoading = true; });
    await Future.delayed(const Duration(seconds: 2)); // Simulate AI processing
    setState(() {
      _descriptionController.text = "Detected a large pothole near the main road. It's causing traffic congestion and is a hazard for motorists.";
      _selectedCategory = 'Pothole'; // AI suggests category
      _selectedUrgency = 'High'; // AI suggests urgency
      _isLoading = false;
    });
    if (mounted) _showSnackBar('AI has generated a description!');
  }

  // --- NEW: Simulate Social Sharing ---
  void _shareIssue(String platform) {
    // In a real app, you'd integrate with platform-specific sharing APIs.
    // For now, we'll use share_plus as a general share intent.
    final String textToShare = 'I just reported an issue: "${_descriptionController.text}" via Civic Reporter app! #CivicIssue #${_selectedCategory}';
    Share.share(textToShare, subject: 'New Civic Issue Report');
    _showSnackBar('Sharing to $platform (via generic share intent)...');
  }

  void _submitIssue() async {
    if (!_formKey.currentState!.validate()) return;
    if (_imageBytes == null) {
      _showSnackBar('Please add an image of the issue.', isError: true);
      return;
    }
    if (_currentPosition == null) {
      _showSnackBar('Please wait for your location to be fetched.', isError: true);
      _getCurrentLocation(); // Try fetching again
      return;
    }

    setState(() { _isLoading = true; });
    try {
      await _issueRepository.createIssue(
        description: _descriptionController.text.trim(),
        category: _selectedCategory,
        latitude: _currentPosition!.latitude,
        longitude: _currentPosition!.longitude,
        imageBytes: _imageBytes!,
        isAnonymous: _postAnonymously,
      );

      if (mounted) {
        _showSnackBar('Issue reported successfully!');
        Navigator.of(context).pop(); // Go back after reporting
      }
    } catch (e) {
      if (mounted) _showSnackBar('Failed to report issue: ${e.toString()}', isError: true);
    } finally {
      if(mounted) setState(() { _isLoading = false; });
    }
  }

  void _showSnackBar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? AppColors.error : AppColors.success,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Report an Issue'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Location Bar
              GestureDetector(
                onTap: _getCurrentLocation, // Make location bar refreshable
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(30),
                      border: Border.all(color: Colors.grey.shade300)
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(LucideIcons.mapPin, color: AppColors.primary, size: 16),
                      const SizedBox(width: 8),
                      Expanded(child: Text(_locationDisplay, style: const TextStyle(fontWeight: FontWeight.w500), textAlign: TextAlign.center)),
                      if (_currentPosition == null && !_isLoading) // Show refresh if location not set
                        const Icon(Icons.refresh, color: AppColors.textLight, size: 16),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Image Buttons
              Row(
                children: [
                  Expanded(child: _ImageButton(icon: LucideIcons.image, text: 'Add from gallery', onTap: () => _pickImage(ImageSource.gallery))),
                  const SizedBox(width: 16),
                  Expanded(child: _ImageButton(icon: LucideIcons.camera, text: 'Take photo', onTap: () => _pickImage(ImageSource.camera))),
                ],
              ),
              if (_imageBytes != null)
                Padding(
                  padding: const EdgeInsets.only(top: 16.0),
                  child: Stack(
                    alignment: Alignment.topRight,
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: Image.memory(_imageBytes!, fit: BoxFit.cover, width: double.infinity, height: 200),
                      ),
                      IconButton(
                        icon: const Icon(Icons.cancel, color: Colors.white),
                        onPressed: () => setState(() { _imageBytes = null; _imageFileName = null; }),
                      ),
                    ],
                  ),
                ),
              const SizedBox(height: 24),

              // Description Field
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  hintText: 'Description',
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(12)), borderSide: BorderSide.none),
                ),
                maxLines: 4,
                validator: (value) => (value?.isEmpty ?? true) ? 'Please enter a description' : null,
              ),
              const SizedBox(height: 16),

              // AI Suggestion Button
              ElevatedButton.icon(
                onPressed: _isLoading ? null : _magicWrite,
                icon: const Icon(LucideIcons.sparkles, color: Colors.white),
                label: const Text("AI Suggestion: AI AUTO DETECT", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  elevation: 0,
                ),
              ),
              const SizedBox(height: 16),

              // Category Dropdown
              DropdownButtonFormField<String>(
                value: _selectedCategory,
                items: ['Pothole', 'Streetlight', 'Garbage', 'Water Leakage'].map((v) => DropdownMenuItem(value: v, child: Text(v))).toList(),
                onChanged: (val) => setState(() => _selectedCategory = val!),
                decoration: InputDecoration(
                  prefixIcon: const Icon(LucideIcons.layoutGrid, color: AppColors.textLight),
                  labelText: 'Category (AI auto fetch)',
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                ),
              ),
              const SizedBox(height: 16),

              // Urgency Dropdown
              DropdownButtonFormField<String>(
                value: _selectedUrgency,
                items: ['High', 'Medium', 'Low'].map((v) => DropdownMenuItem(value: v, child: Text(v))).toList(),
                onChanged: (val) => setState(() => _selectedUrgency = val!),
                decoration: InputDecoration(
                  prefixIcon: const Icon(LucideIcons.flag, color: AppColors.textLight),
                  labelText: 'Urgency',
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                ),
              ),
              const SizedBox(height: 24),

              // Social Sharing Dropdown
              _buildShareOnDropdown(),
              const SizedBox(height: 24),

              // Anonymous Toggle
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12)),
                child: SwitchListTile(
                  title: const Text('Post Anonymously', style: TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: const Text('Your personal details will not be shown on the public feed.'),
                  value: _postAnonymously,
                  onChanged: (val) => setState(() => _postAnonymously = val),
                  activeColor: AppColors.primary,
                ),
              ),
              const SizedBox(height: 24),

              // Submit Button
              _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : ElevatedButton(
                onPressed: _submitIssue,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [Text('POST ISSUE', style: TextStyle(fontSize: 16)), SizedBox(width: 8), Icon(Icons.arrow_forward)],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildShareOnDropdown() {
    return Container(
      decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.shade300)
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          isExpanded: true,
          icon: const Icon(Icons.keyboard_arrow_down, color: AppColors.textLight),
          hint: Padding(
            padding: const EdgeInsets.only(left: 16.0),
            child: Row(
              children: [
                const Icon(LucideIcons.share2, color: AppColors.textLight),
                const SizedBox(width: 12),
                Text('Also Share on', style: Theme.of(context).textTheme.titleMedium?.copyWith(color: AppColors.textDark)),
              ],
            ),
          ),
          items: <String>['Facebook', 'Instagram', 'X (Twitter)', 'WhatsApp Status'].map((String value) {
            return DropdownMenuItem<String>(
              value: value,
              child: Padding(
                padding: const EdgeInsets.only(left: 16.0),
                child: Text(value),
              ),
            );
          }).toList(),
          onChanged: (String? newValue) {
            if (newValue != null) {
              _shareIssue(newValue);
            }
          },
        ),
      ),
    );
  }
}

// Helper widget for the two image buttons
class _ImageButton extends StatelessWidget {
  final IconData icon;
  final String text;
  final VoidCallback onTap;
  const _ImageButton({required this.icon, required this.text, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.shade300),
        ),
        child: Column(
          children: [
            Icon(icon, color: AppColors.primary, size: 28),
            const SizedBox(height: 8),
            Text(text, style: const TextStyle(fontWeight: FontWeight.w500)),
          ],
        ),
      ),
    );
  }
}