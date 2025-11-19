import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/constants.dart';
import '../models/home_summary.dart';

class HomeService {
  Future<HomeSummary> fetchHomeSummary() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token') ?? '';

    final response = await http.get(
      Uri.parse('${Env.baseUrl}/home/summary'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    print('Response status: ${response.statusCode}');
    print('Response body: ${response.body}');
    
    if (response.statusCode == 200) {
      final jsonData = json.decode(response.body);
      return HomeSummary.fromJson(jsonData);
    } else if (response.statusCode == 403) {
      try {
        final errorData = json.decode(response.body);
        final errorMessage = errorData['detail'] ?? 'Token expired';
        throw Exception('403: $errorMessage');
      } catch (e) {
        throw Exception('403: Could not validate token: Signature has expired.');
      }
    } else {
      throw Exception('Failed to load home summary: ${response.statusCode}');
    }
  }
}