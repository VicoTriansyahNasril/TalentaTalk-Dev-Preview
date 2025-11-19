import 'package:equatable/equatable.dart';
import '../model/exam_score_model.dart';

abstract class ExamScoreState extends Equatable {
  @override
  List<Object?> get props => [];
}

class ExamScoreInitial extends ExamScoreState {}

class ExamScoreLoading extends ExamScoreState {}

class ExamScoreLoaded extends ExamScoreState {
  final ExamScoreResult result;

  ExamScoreLoaded(this.result);

  @override
  List<Object?> get props => [result];
}

class ExamScoreError extends ExamScoreState {
  final String message;

  ExamScoreError(this.message);

  @override
  List<Object?> get props => [message];
}
