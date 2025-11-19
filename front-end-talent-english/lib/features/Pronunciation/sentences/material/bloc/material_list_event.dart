abstract class MaterialListEvent {}

class LoadMaterials extends MaterialListEvent {
  final String category;
  LoadMaterials(this.category);
}

class LoadMaterialsForPhonemes extends MaterialListEvent {
  final List<String> phonemes;
  LoadMaterialsForPhonemes(this.phonemes);
}