part of 'score_bloc.dart';

abstract class ScoreEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class ScoreRequested extends ScoreEvent {}
class ScoreRequestedFromResult extends ScoreEvent {
  final List<ScoreResult> results;

  ScoreRequestedFromResult(this.results);

  @override
  List<Object?> get props => [results];
}