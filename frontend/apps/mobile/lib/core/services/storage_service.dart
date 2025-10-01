// File: lib/core/services/storage_service.dart
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static const _tokenKey = 'auth_token';

  Future<void> saveToken(String token) async {
    if (kIsWeb) {
      // Use SharedPreferences for web
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_tokenKey, token);
    } else {
      // Use FlutterSecureStorage for mobile
      const storage = FlutterSecureStorage();
      await storage.write(key: _tokenKey, value: token);
    }
  }

  Future<String?> getToken() async {
    if (kIsWeb) {
      // Use SharedPreferences for web
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_tokenKey);
    } else {
      // Use FlutterSecureStorage for mobile
      const storage = FlutterSecureStorage();
      return await storage.read(key: _tokenKey);
    }
  }

  Future<void> deleteToken() async {
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_tokenKey);
    } else {
      const storage = FlutterSecureStorage();
      await storage.delete(key: _tokenKey);
    }
  }
}