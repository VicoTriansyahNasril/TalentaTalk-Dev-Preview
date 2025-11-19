import 'package:flutter_bloc/flutter_bloc.dart';
import 'phoneme_category_event.dart';
import 'phoneme_category_state.dart';
import '../repository/phoneme_repository.dart';

class PhonemeCategoryBloc extends Bloc<PhonemeCategoryEvent, PhonemeCategoryState> {
  final PhonemeRepository repository;

  PhonemeCategoryBloc(this.repository) : super(PhonemeInitial()) {
    on<LoadPhonemes>((event, emit) async {
      emit(PhonemeLoading());
      try {
        final phonemes = await repository.fetchPhonemes();
        for (var p in phonemes) {
          print('Phoneme: ${p.phoneme}, Example: ${p.example}, Type: ${p.type}');
        }
        final vowels = phonemes.where((p) => p.type == 'vowel').toList();
        final consonants = phonemes.where((p) => p.type == 'consonant').toList();
        emit(PhonemeLoaded(vowels: vowels, consonants: consonants));
      } catch (e) {
        print('Error fetching phonemes: $e'); 
        emit(PhonemeError(e.toString()));
      }
    });
  }
}
