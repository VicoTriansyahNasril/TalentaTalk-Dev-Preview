abstract class ExamMaterialEvent {}

class LoadMaterials extends ExamMaterialEvent {
  final String category;
  LoadMaterials(this.category);
}


class LoadMultipleMaterials extends ExamMaterialEvent {
  final List<String> phonemes;
  LoadMultipleMaterials(this.phonemes);
}