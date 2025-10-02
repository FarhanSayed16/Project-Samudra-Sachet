import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiClient {
  static const String baseUrl = 'http://localhost:8000/api/v1';
  static final Dio _dio = Dio();
  static const FlutterSecureStorage _storage = FlutterSecureStorage();

  static void _setupInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add auth token to requests
          final token = await _storage.read(key: 'access_token');
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401) {
            // Token expired, try to refresh
            final refreshed = await _refreshToken();
            if (refreshed) {
              // Retry the original request
              final token = await _storage.read(key: 'access_token');
              error.requestOptions.headers['Authorization'] = 'Bearer $token';
              final response = await _dio.fetch(error.requestOptions);
              handler.resolve(response);
              return;
            }
          }
          handler.next(error);
        },
      ),
    );
  }

  static Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _storage.read(key: 'refresh_token');
      if (refreshToken == null) return false;

      final response = await _dio.post(
        '$baseUrl/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      if (response.statusCode == 200) {
        await _storage.write(
            key: 'access_token', value: response.data['access_token']);
        return true;
      }
    } catch (e) {
      print('Token refresh failed: $e');
    }
    return false;
  }

  // Authentication endpoints
  static Future<Map<String, dynamic>> login(
      String email, String password) async {
    try {
      _setupInterceptors();
      final response = await _dio.post(
        '$baseUrl/auth/login',
        data: {
          'email': email,
          'password': password,
        },
      );

      return {
        'success': true,
        'access_token': response.data['access_token'],
        'refresh_token': response.data['refresh_token'],
        'user': response.data['user'],
      };
    } catch (e) {
      if (e is DioException) {
        return {
          'success': false,
          'message': e.response?.data['detail'] ?? 'Login failed',
        };
      }
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
      };
    }
  }

  // Reports endpoints
  static Future<List<Map<String, dynamic>>> getPublicReports({
    int limit = 20,
    int skip = 0,
  }) async {
    try {
      _setupInterceptors();
      final response = await _dio.get(
        '$baseUrl/reports/public',
        queryParameters: {
          'limit': limit,
          'skip': skip,
        },
      );

      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      print('Error fetching public reports: $e');
      return [];
    }
  }

  static Future<Map<String, dynamic>> submitReport({
    required String hazardType,
    required double latitude,
    required double longitude,
    String? description,
    int severityLevel = 3,
    String? mediaPath,
  }) async {
    try {
      _setupInterceptors();

      FormData formData = FormData.fromMap({
        'hazard_type': hazardType,
        'latitude': latitude,
        'longitude': longitude,
        'description': description ?? '',
        'severity_level': severityLevel,
      });

      if (mediaPath != null) {
        formData.files.add(MapEntry(
          'media_file',
          await MultipartFile.fromFile(mediaPath),
        ));
      }

      final response = await _dio.post(
        '$baseUrl/reports/',
        data: formData,
      );

      return {
        'success': true,
        'data': response.data,
      };
    } catch (e) {
      if (e is DioException) {
        return {
          'success': false,
          'message': e.response?.data['detail'] ?? 'Failed to submit report',
        };
      }
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
      };
    }
  }

  // Social Media endpoints
  static Future<List<Map<String, dynamic>>> getSocialMediaPosts({
    int limit = 20,
    int skip = 0,
  }) async {
    try {
      _setupInterceptors();
      final response = await _dio.get(
        '$baseUrl/social-media/public',
        queryParameters: {
          'limit': limit,
          'skip': skip,
        },
      );

      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      print('Error fetching social media posts: $e');
      return [];
    }
  }

  // User endpoints
  static Future<Map<String, dynamic>> getUserProfile() async {
    try {
      _setupInterceptors();
      final response = await _dio.get('$baseUrl/users/me');
      return {
        'success': true,
        'data': response.data,
      };
    } catch (e) {
      if (e is DioException) {
        return {
          'success': false,
          'message': e.response?.data['detail'] ?? 'Failed to fetch profile',
        };
      }
      return {
        'success': false,
        'message': 'Network error: ${e.toString()}',
      };
    }
  }

  // Logout
  static Future<void> logout() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
    await _storage.delete(key: 'user_data');
  }
}

