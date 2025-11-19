import 'dart:convert';
import 'package:http/http.dart' as http;
import '../model/material_model.dart';

class MaterialService {
  final String baseUrl;

  MaterialService({required this.baseUrl});

  Future<List<MateriUjian>> fetchMaterialsByCategory(String category) async {
    final response = await http.get(Uri.parse('$baseUrl/exam/exam_by_category/$category'));

    if (response.statusCode == 200) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      print("$data");
      if (data['sentences'] != null) {
        return List<MateriUjian>.from(
          data['sentences'].map((json) => MateriUjian.fromJson(json)),
        );
      } else {
        return [];
      }
    } else {
      throw Exception('Failed to load materials');
    }
  }
  
}
