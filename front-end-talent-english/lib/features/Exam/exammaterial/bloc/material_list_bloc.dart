import 'package:flutter_bloc/flutter_bloc.dart';
import '../model/material_model.dart';
import '../repository/material_repository.dart';
import 'material_list_event.dart';
import 'material_list_state.dart';

class ExamMaterialBloc extends Bloc<ExamMaterialEvent, ExamMaterialState> {
  final MaterialRepository repository;

  ExamMaterialBloc(this.repository) : super(ExamMaterialInitial()) {
    on<LoadMaterials>((event, emit) async {
      emit(ExamMaterialLoading());
      try {
        final materials = await repository.fetchMaterials(category: event.category);
        if (materials.isEmpty) {
          emit(MaterialEmpty());
        } else {
          emit(ExamMaterialLoaded(materials));
        }
      } catch (e) {
        emit(ExamMaterialError('Failed to load materials'));
      }
    });

    on<LoadMultipleMaterials>((event, emit) async {
      emit(ExamMaterialLoading());
      try {
        final materials = await repository.fetchMaterialsForPhonemes(event.phonemes);
        
        if (materials.isEmpty) {
          emit(ExamMaterialError('No materials found for phonemes: ${event.phonemes.join(', ')}'));
        } else {
          emit(ExamMaterialLoaded(materials));
        }
      } catch (e) {
        emit(ExamMaterialError('Failed to load materials: ${e.toString()}'));
      }
    });
  }
}