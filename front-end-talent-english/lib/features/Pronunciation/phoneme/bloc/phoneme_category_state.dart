import '../model/phoneme_model.dart';
abstract class PhonemeCategoryState {}

class PhonemeInitial extends PhonemeCategoryState {}

class PhonemeLoading extends PhonemeCategoryState {}

class PhonemeLoaded extends PhonemeCategoryState {
  final List<Phoneme> vowels;
  final List<Phoneme> consonants;

  PhonemeLoaded({required this.vowels, required this.consonants});
}

class PhonemeError extends PhonemeCategoryState {
  final String message;
  PhonemeError(this.message);
}
