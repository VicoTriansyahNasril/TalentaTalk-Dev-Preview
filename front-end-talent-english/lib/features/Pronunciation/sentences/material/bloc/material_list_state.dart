import '../model/material_model.dart';

abstract class MaterialListState {}

class MaterialListInitial extends MaterialListState {}

class MaterialListLoading extends MaterialListState {}

class MaterialListLoaded extends MaterialListState {
  final List<MaterialModel> materials;

  MaterialListLoaded(this.materials);
}
class MaterialEmpty extends MaterialListState {}

class MaterialListError extends MaterialListState {
  final String message;

  MaterialListError(this.message);
}
