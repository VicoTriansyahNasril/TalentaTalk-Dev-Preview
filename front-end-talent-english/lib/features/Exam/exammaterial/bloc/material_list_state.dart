import '../model/material_model.dart';

abstract class ExamMaterialState {}

class ExamMaterialInitial extends ExamMaterialState {}

class ExamMaterialLoading extends ExamMaterialState {}

class ExamMaterialLoaded extends ExamMaterialState {
  final List<MateriUjian> materials;

  ExamMaterialLoaded(this.materials);
}
class MaterialEmpty extends ExamMaterialState {}

class ExamMaterialError extends ExamMaterialState {
  final String message;

  ExamMaterialError(this.message);
}
