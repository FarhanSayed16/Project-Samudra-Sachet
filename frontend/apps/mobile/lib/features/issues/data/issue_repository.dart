// File: E:/civic-issue-reporter/apps/mobile/lib/features/issues/data/issue_repository.dart

import 'dart:typed_data';
import 'package:dio/dio.dart';
import '../../../core/api/api_client.dart';
import '../../../core/services/storage_service.dart';
import '../../../data/models/issue.dart';

class IssueRepository {
  final _storageService = StorageService();

  // --- CREATE NEW ISSUE ---
  Future<Issue> createIssue({
    required String description,
    required String category,
    required double latitude,
    required double longitude,
    required Uint8List imageBytes,
    required bool isAnonymous, // 👈 new parameter
  }) async {
    try {
      // --- STEP 0: Get auth token ---
      final token = await _storageService.getToken();
      if (token == null) {
        throw Exception('You are not logged in. Please log in to report an issue.');
      }

      final options = Options(headers: {'Authorization': 'Bearer $token'});
      final filename = "issue_${DateTime.now().millisecondsSinceEpoch}.jpg";

      // --- STEP 1: Get presigned upload URL ---
      final initiateUploadResponse = await dio.post(
        '/issues/initiate-upload',
        queryParameters: {'filename': filename},
        options: options,
      );

      final String? uploadUrl = initiateUploadResponse.data['url'];
      if (uploadUrl == null) {
        throw Exception('Backend did not provide a valid upload URL.');
      }

      // Extract permanent URL (without query params)
      final uri = Uri.parse(uploadUrl);
      final fileUrl = '${uri.scheme}://${uri.host}${uri.path}';

      // --- STEP 2: Upload to MinIO ---
      await dio.put(
        uploadUrl,
        data: Stream.fromIterable(imageBytes.map((e) => [e])),
        options: Options(
          headers: {
            'Content-Length': imageBytes.lengthInBytes,
            'Content-Type': 'image/jpeg',
          },
        ),
      );

      // --- STEP 3: Create issue in DB ---
      final createIssueResponse = await dio.post(
        '/issues',
        data: {
          "description": description,
          "category": category,
          "latitude": latitude,
          "longitude": longitude,
          "image_url": fileUrl,
          "is_anonymous": isAnonymous, // 👈 send new flag
        },
        options: options,
      );

      return Issue.fromJson(createIssueResponse.data);

    } on DioException catch (e) {
      throw Exception('Failed to create issue: ${e.response?.data ?? e.message}');
    }
  }

  // --- GET MY ISSUES ---
  Future<List<Issue>> getMyIssues() async {
    try {
      final token = await _storageService.getToken();
      if (token == null) throw Exception('Not authenticated');

      final response = await dio.get(
        '/users/me/issues',
        options: Options(headers: {'Authorization': 'Bearer $token'}),
      );

      return (response.data as List)
          .map((issueJson) => Issue.fromJson(issueJson))
          .toList();

    } on DioException catch (e) {
      throw Exception('Failed to fetch issues: ${e.response?.data ?? e.message}');
    }
  }

  // --- GET PUBLIC ISSUES ---
  Future<List<Issue>> getPublicIssues() async {
    try {
      // This endpoint is public, so no auth token is needed
      final response = await dio.get('/issues');

      // Convert the list of JSON objects to a list of Issue objects
      return (response.data as List)
          .map((issueJson) => Issue.fromJson(issueJson))
          .toList();

    } on DioException catch (e) {
      throw Exception('Failed to fetch public issues: ${e.response?.data ?? e.message}');
    }
  }
}
