import '../model/word_material_model.dart';

abstract class WordMaterialState {}

class WordMaterialInitial extends WordMaterialState {}

class WordMaterialLoading extends WordMaterialState {}

class WordMaterialLoaded extends WordMaterialState {
  final List<WordMaterialModel> words;

  WordMaterialLoaded(this.words);
}

class WordMaterialEmpty extends WordMaterialState {}

class WordMaterialError extends WordMaterialState {
  final String message;

  WordMaterialError(this.message);
}
