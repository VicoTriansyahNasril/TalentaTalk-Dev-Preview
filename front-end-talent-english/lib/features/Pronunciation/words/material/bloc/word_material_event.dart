abstract class WordMaterialEvent {}

class LoadWordMaterials extends WordMaterialEvent {
  final String category;
  LoadWordMaterials(this.category);
}

