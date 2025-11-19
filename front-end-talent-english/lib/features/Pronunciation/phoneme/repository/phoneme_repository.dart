import 'dart:convert';
import 'package:http/http.dart' as http;
import '../model/phoneme_model.dart';

class PhonemeRepository {
  final String baseUrl;

  PhonemeRepository({required this.baseUrl});

  Future<List<Phoneme>> fetchPhonemes() async {
    final response = await http.get(Uri.parse('$baseUrl/phonemes'));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<Phoneme>.from(data.map((item) => Phoneme.fromJson(item)));
    } else {
      throw Exception('Failed to load phonemes');
    }
  }
}
