// File: E:/civic-issue-reporter/apps/mobile/lib/core/api/api_client.dart

import 'package:dio/dio.dart';

final dio = Dio(
  BaseOptions(
    // ⚠️ IMPORTANT:
    // - If you're running on Android Emulator: use http://10.0.2.2:8585/
    // - If you're running on iOS Simulator: use http://127.0.0.1:8585/
    // - If you're running Flutter Web: http://localhost:8585/
    // baseUrl: 'http://localhost:8585/',
    baseUrl: 'https://3blkgv75-8585.inc1.devtunnels.ms/',

    // ⬆️ Increased timeouts to handle slower connections and image uploads
    connectTimeout: const Duration(seconds: 15), // was 5
    receiveTimeout: const Duration(seconds: 30), // was 3
    sendTimeout: const Duration(seconds: 30),
  ),
);
