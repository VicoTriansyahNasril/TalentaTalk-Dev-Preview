import '../model/ptraining_model.dart';

abstract class ConversationTrainingState {}

class TrainingLoading extends ConversationTrainingState {}

class TrainingLoaded extends ConversationTrainingState {
  final List<ConversationTraining> trainings;
  TrainingLoaded(this.trainings);
}

class TrainingError extends ConversationTrainingState {
  final String message;
  TrainingError(this.message);
}
