import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../core/constants.dart';
import '../model/exam_score_model.dart';

class ExamScoreRepository {
  final String baseUrl;

  ExamScoreRepository({required this.baseUrl});

  Future<ExamScoreResult> fetchExamScore(int idUjian) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');
    if (token == null) throw Exception("Token not found");

    final response = await http.get(
      Uri.parse('$baseUrl/exam/result/$idUjian'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return ExamScoreResult.fromJson(data);
    } else {
      throw Exception('Failed to fetch exam result: ${response.statusCode}');
    }
  }
}
