import '../model/material_model.dart';
import '../service/material_service.dart';

class MaterialRepository {
  final MaterialService service;
  
  MaterialRepository(this.service);
  
  Future<List<MaterialModel>> fetchMaterials({String category = "default"}) async {
    return await service.fetchMaterialsByCategory(category);
  }
  
  Future<List<MaterialModel>> fetchMaterialsForPhonemes(List<String> phonemes) async {
    List<MaterialModel> allMaterials = [];
    
    List<String> categoryVariations = _generateCategoryVariations(phonemes);
    
    for (String category in categoryVariations) {
      try {
        print('Trying category: $category');
        final materials = await service.fetchMaterialsByCategory(category);
        
        if (materials.isNotEmpty) {
          allMaterials.addAll(materials);
          print('Found ${materials.length} materials for category: $category');
        } else {
          print('No materials found for category: $category');
        }
      } catch (e) {
        print('Error fetching materials for category $category: $e');
      }
    }
    
    if (allMaterials.isEmpty) {
      print('No materials found for any category variations of phonemes: ${phonemes.join(', ')}');
      return [];
    }
    
    final Map<int, MaterialModel> uniqueMaterials = {};
    for (var material in allMaterials) {
      uniqueMaterials[material.id] = material;
    }
    
    final sortedMaterials = uniqueMaterials.values.toList();
    sortedMaterials.sort((a, b) {
      int phonemeCompare = a.phoneme.compareTo(b.phoneme);
      if (phonemeCompare != 0) return phonemeCompare;
      return a.sentence.compareTo(b.sentence);
    });
    
    return sortedMaterials;
  }
  
  List<String> _generateCategoryVariations(List<String> phonemes) {
    if (phonemes.length == 1) {
      return [phonemes[0]];
    }
    
    List<String> variations = [];
    
    List<List<String>> permutations = _generatePermutations(phonemes);
    
    for (List<String> permutation in permutations) {
      variations.add(permutation.join('-'));
    }
    
    return variations;
  }
  
  List<List<String>> _generatePermutations(List<String> list) {
    if (list.length <= 1) {
      return [list];
    }
    
    List<List<String>> result = [];
    
    for (int i = 0; i < list.length; i++) {
      String current = list[i];
      List<String> remaining = List.from(list)..removeAt(i);
      
      List<List<String>> remainingPermutations = _generatePermutations(remaining);
      
      for (List<String> permutation in remainingPermutations) {
        result.add([current, ...permutation]);
      }
    }
    
    return result;
  }
}