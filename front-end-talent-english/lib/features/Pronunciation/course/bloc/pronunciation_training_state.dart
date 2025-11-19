import '../model/ptraining_model.dart';

abstract class PronunciationTrainingState {}

class TrainingLoading extends PronunciationTrainingState {}

class TrainingLoaded extends PronunciationTrainingState {
  final List<PronunciationTraining> trainings;
  TrainingLoaded(this.trainings);
}

class TrainingError extends PronunciationTrainingState {
  final String message;
  TrainingError(this.message);
}
