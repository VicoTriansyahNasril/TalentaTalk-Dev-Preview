import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/constants.dart';

class TrainingHistoryService {
  Future<List<dynamic>> fetchData(String endpoint) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token') ?? '';

    final response = await http.get(
      Uri.parse('${Env.baseUrl}/history/$endpoint'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      return data['data'];
    } else {
      throw Exception('Failed to fetch $endpoint history');
    }
  }
}
