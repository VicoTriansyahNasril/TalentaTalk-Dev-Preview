import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../core/constants.dart';

class InterviewService {
  final baseUrl = Env.baseUrl;
  String? _sessionCookie;

  Future<String?> startInterview() async {
    final res = await http.get(Uri.parse('$baseUrl/interview/start'));
    if (res.statusCode == 200) {
       _sessionCookie = res.headers['set-cookie'];
      final data = jsonDecode(res.body);
      return data['question'];
    }
    return null;
  }

  Future<Map<String, dynamic>?> sendAnswer(String answer, String duration) async {
    final res = await http.post(
      Uri.parse('$baseUrl/interview/answer'),
      headers: {'Content-Type': 'application/json',if (_sessionCookie != null) 'cookie': _sessionCookie!,},
      body: jsonEncode({'answer': answer, 'duration': duration}),
    );

    if (res.statusCode == 200) {
      if (res.headers['set-cookie'] != null) {
        _sessionCookie = res.headers['set-cookie'];
      }
      return jsonDecode(res.body);
    }
    return null;
  }

  Future<Map<String, dynamic>?> getSummary() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    if (token == null || token.isEmpty) {
      throw Exception('Authentication token not found');
    }

    final res = await http.post(
      Uri.parse('$baseUrl/interview/summary'),
      headers: {
        'Content-Type': 'application/json',
        if (_sessionCookie != null) 'cookie': _sessionCookie!,
        'Authorization': 'Bearer $token',
      },
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    return null;
  }

}
