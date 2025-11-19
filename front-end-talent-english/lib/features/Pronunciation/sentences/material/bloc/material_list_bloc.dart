import 'package:flutter_bloc/flutter_bloc.dart';
import '../repository/material_repository.dart';
import 'material_list_event.dart';
import 'material_list_state.dart';

class MaterialListBloc extends Bloc<MaterialListEvent, MaterialListState> {
  final MaterialRepository repository;

  MaterialListBloc(this.repository) : super(MaterialListInitial()) {
    on<LoadMaterials>((event, emit) async {
      emit(MaterialListLoading());
      try {
        final materials = await repository.fetchMaterials(category: event.category);
        if (materials.isEmpty) {
          emit(MaterialEmpty());
        } else {
          emit(MaterialListLoaded(materials));
        }
      } catch (e) {
        emit(MaterialListError('Failed to load materials'));
      }
    });

    on<LoadMaterialsForPhonemes>((event, emit) async {
      emit(MaterialListLoading());
      try {
        final materials = await repository.fetchMaterialsForPhonemes(event.phonemes);
        if (materials.isEmpty) {
          emit(MaterialListError('No materials found for phonemes: ${event.phonemes.join(', ')}'));
        } else {
          emit(MaterialListLoaded(materials));
        }
      } catch (e) {
        emit(MaterialListError('Failed to load materials: ${e.toString()}'));
      }
    });
  }
  
}
