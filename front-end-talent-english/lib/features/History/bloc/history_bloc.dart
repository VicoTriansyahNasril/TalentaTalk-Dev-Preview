import 'package:flutter_bloc/flutter_bloc.dart';
import 'history_event.dart';
import 'history_state.dart';
import '../repository/history_repository.dart';

class TrainingHistoryBloc extends Bloc<TrainingHistoryEvent, TrainingHistoryState> {
  final TrainingHistoryRepository repository;

  TrainingHistoryBloc({required this.repository}) : super(TrainingHistoryInitial()) {
    on<LoadTrainingHistory>((event, emit) async {
      emit(TrainingHistoryLoading());
      try {
        final pronunciation = await repository.getPronunciationHistory();
        final conversation = await repository.getConversationHistory();
        final interview = await repository.getInterviewHistory();
        final exam = await repository.getExamHistory();
        emit(TrainingHistoryLoaded(
          pronunciationHistory: pronunciation,
          conversationHistory: conversation,
          interviewHistory: interview,
          examHistory: exam,
        ));
      } catch (e) {
        emit(TrainingHistoryError(e.toString()));
      }
    });

    on<RefreshTrainingHistory>((event, emit) async {
      try {
        final pronunciation = await repository.getPronunciationHistory();
        final conversation = await repository.getConversationHistory();
        final interview = await repository.getInterviewHistory();
        final exam = await repository.getExamHistory();
        emit(TrainingHistoryLoaded(
          pronunciationHistory: pronunciation,
          conversationHistory: conversation,
          interviewHistory: interview,
          examHistory: exam,
        ));
      } catch (e) {
        emit(TrainingHistoryError(e.toString()));
      }
    });
  }
}