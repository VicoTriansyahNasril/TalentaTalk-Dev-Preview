// lib/features/Auth/repository/auth_repository.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/constants.dart';
import '../model/login_response.dart';
import '../model/onboarding_check.dart';

class AuthRepository {
  Future<LoginResponse> login({required String email, required String password}) async {
    try {
      final response = await http.post(
        Uri.parse('${Env.baseUrl}/login/talent'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return LoginResponse.fromJson(data);
      } else {
        final data = jsonDecode(response.body);
        throw Exception(data['detail'] ?? 'Login failed');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  Future<OnboardingCheckResponse> checkOnboarding({required String token}) async {
    try {
      final response = await http.get(
        Uri.parse('${Env.baseUrl}/pretest/check'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return OnboardingCheckResponse.fromJson(data);
      } else if (response.statusCode == 403) {
        final data = jsonDecode(response.body);
        final errorMessage = data['detail'] ?? 'Token validation failed';
        
        if (errorMessage.contains('Could not validate token: Signature has expired')) {
          throw TokenExpiredException(errorMessage);
        } else {
          throw Exception('Forbidden: $errorMessage');
        }
      } else {
        final data = jsonDecode(response.body);
        throw Exception(data['detail'] ?? 'Failed to check onboarding status');
      }
    } catch (e) {
      if (e is TokenExpiredException) {
      }
      throw Exception('Network error: $e');
    }
  }
}

class TokenExpiredException implements Exception {
  final String message;
  
  TokenExpiredException(this.message);
  
  @override
  String toString() => 'TokenExpiredException: $message';
}