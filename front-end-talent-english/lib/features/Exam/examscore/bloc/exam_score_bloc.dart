import 'package:flutter_bloc/flutter_bloc.dart';
import '../repository/exam_score_repository.dart';
import 'exam_score_event.dart';
import 'exam_score_state.dart';

class ExamScoreBloc extends Bloc<ExamScoreEvent, ExamScoreState> {
  final ExamScoreRepository repository;

  ExamScoreBloc(this.repository) : super(ExamScoreInitial()) {
    on<LoadExamScore>((event, emit) async {
      emit(ExamScoreLoading());
      try {
        final result = await repository.fetchExamScore(event.examId);
        emit(ExamScoreLoaded(result));
      } catch (e) {
        emit(ExamScoreError(e.toString()));
      }
    });
  }
}
