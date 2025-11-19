import 'dart:convert';
import 'package:http/http.dart' as http;

class PronunciationService {
  final String baseUrl;

  PronunciationService({required this.baseUrl});

  Future<Map<String, dynamic>> fetchSentenceById(int id) async {
    final url = Uri.parse('$baseUrl/phoneme/sentence_by_id/$id');

    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);

        if (data.containsKey('content')) {
          return data;
        } else {
          throw Exception('⚠️ No word found for the given ID.');
        }
      } else {
        throw Exception('❌ Server error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('❌ Failed to fetch word by ID: $e');
    }
  }
}
