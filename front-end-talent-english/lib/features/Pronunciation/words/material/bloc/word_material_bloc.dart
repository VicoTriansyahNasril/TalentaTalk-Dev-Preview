import 'package:flutter_bloc/flutter_bloc.dart';
import '../repository/word_material_repository.dart';
import 'word_material_event.dart';
import 'word_material_state.dart';

class WordMaterialBloc extends Bloc<WordMaterialEvent, WordMaterialState> {
  final WordMaterialRepository repository;

  WordMaterialBloc(this.repository) : super(WordMaterialInitial()) {
    on<LoadWordMaterials>((event, emit) async {
      emit(WordMaterialLoading());
      try {
        final words = await repository.fetchWords(category: event.category);
        if (words.isEmpty) {
          emit(WordMaterialEmpty());
        } else {
          emit(WordMaterialLoaded(words));
        }
      } catch (e) {
        emit(WordMaterialError('Failed to load word materials'));
      }
    });
  }
}
