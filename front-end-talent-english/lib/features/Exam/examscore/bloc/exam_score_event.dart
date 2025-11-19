import 'package:equatable/equatable.dart';

abstract class ExamScoreEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class LoadExamScore extends ExamScoreEvent {
  final int examId;

  LoadExamScore(this.examId);

  @override
  List<Object?> get props => [examId];
}
