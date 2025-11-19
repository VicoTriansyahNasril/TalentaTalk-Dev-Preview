import 'dart:convert';
import 'package:http/http.dart' as http;
import '../model/word_material_model.dart';
import '../../../../../core/constants.dart';
class WordMaterialService {
  final String baseUrl;

  WordMaterialService({this.baseUrl = Env.baseUrl});

  Future<List<WordMaterialModel>> fetchWordsByCategory(String category) async {
    final response = await http.get(Uri.parse('$baseUrl/phoneme/words_by_category/$category'));
    print("categori $category");
    if (response.statusCode == 200) {
      final Map<String, dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
      final List<dynamic> wordList = data['words'] ?? [];

      return wordList.map((json) {
        return WordMaterialModel(
          idWord: json['idContent'],
          word: json['content'],
          phoneme: json['phoneme'],
        );
      }).toList();
    } else {
      throw Exception('Failed to fetch words by category');
    }
  }
}
