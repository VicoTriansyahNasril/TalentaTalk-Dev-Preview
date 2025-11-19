import '../model/word_material_model.dart';
import '../service/word_material_service.dart';

class WordMaterialRepository {
  final WordMaterialService service;

  WordMaterialRepository({required this.service});

  Future<List<WordMaterialModel>> fetchWords({String category = 'default'}) {
    return service.fetchWordsByCategory(category);
  }
}
