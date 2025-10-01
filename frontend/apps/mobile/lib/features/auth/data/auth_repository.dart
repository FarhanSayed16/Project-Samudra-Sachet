// File: lib/features/auth/data/auth_repository.dart
import 'package:dio/dio.dart';
import '../../../core/api/api_client.dart';
import '../../../data/models/token.dart';
import '../../../core/services/storage_service.dart'; // 👈 Import new service

class AuthRepository {
  final _storageService = StorageService();

  // 👇 LOGIN
  Future<Token> login(String username, String password) async {
    try {
      final response = await dio.post(
        '/auth/login',
        data: {
          'username': username,
          'password': password,
        },
      );

      final token = Token.fromJson(response.data);

      // Save token securely
      await _storageService.saveToken(token.accessToken);

      return token;
    } on DioException catch (e) {
      throw Exception('Failed to login: ${e.message}');
    }
  }

  // 👇 REGISTER
  Future<void> register({
    required String fullName,
    required String phoneNumber, // Or email, depending on backend
    required String password,
  }) async {
    try {
      await dio.post(
        '/auth/register',
        data: {
          'full_name': fullName,
          'phone_number': phoneNumber,
          'password': password,
        },
      );
      // ✅ On success: user is created in backend.
      // You can redirect to login screen in the UI layer.
    } on DioException catch (e) {
      throw Exception(
        'Failed to register: ${e.response?.data['detail'] ?? e.message}',
      );
    }
  }
}
