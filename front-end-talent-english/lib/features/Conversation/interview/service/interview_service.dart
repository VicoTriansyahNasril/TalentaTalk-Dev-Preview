import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../core/constants.dart';
import 'dart:developer' as dev;

class InterviewService {
  final baseUrl = Env.baseUrl;
  String? _currentSessionId;

  Future<String?> startInterview() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/interview/start'));

      if (res.statusCode == 200) {
        final body = jsonDecode(res.body);
        final data = body['data'];

        if (data != null && data['session_id'] != null) {
          _currentSessionId = data['session_id'];
          dev.log('✅ Interview Session Started: $_currentSessionId');
          return data['question'];
        }
      }
      dev.log('❌ Start Interview Failed: ${res.body}');
      return null;
    } catch (e) {
      dev.log('❌ Start Interview Error: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>?> sendAnswer(
    String answer,
    String duration,
  ) async {
    if (_currentSessionId == null) {
      dev.log('❌ Error: No Active Session ID');
      return null;
    }

    try {
      final res = await http.post(
        Uri.parse('$baseUrl/interview/answer'),
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': _currentSessionId!,
        },
        body: jsonEncode({'user_input': answer, 'duration': duration}),
      );

      dev.log('📤 Answer Response: ${res.statusCode}');

      if (res.statusCode == 200) {
        final body = jsonDecode(res.body);
        return body['data'];
      }
      return null;
    } catch (e) {
      dev.log('❌ Send Answer Error: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>?> getSummary() async {
    if (_currentSessionId == null) return null;

    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    if (token == null || token.isEmpty) {
      throw Exception('Authentication token not found');
    }

    try {
      final res = await http.post(
        Uri.parse('$baseUrl/interview/summary'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
          'X-Session-ID': _currentSessionId!,
        },
      );

      if (res.statusCode == 200) {
        final body = jsonDecode(res.body);
        _currentSessionId = null;
        return body['data'];
      }
      return null;
    } catch (e) {
      dev.log('❌ Summary Error: $e');
      return null;
    }
  }
}
