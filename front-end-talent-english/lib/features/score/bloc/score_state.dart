part of 'score_bloc.dart';

abstract class ScoreState extends Equatable {
  @override
  List<Object?> get props => [];
}

class ScoreLoading extends ScoreState {}

class ScoreLoaded extends ScoreState {
  final double score;
  final List<List<HighlightSegment>> segments;
  final List<ScoreResult> results; 

  ScoreLoaded({
    required this.score, 
    required this.segments,
    required this.results,
  });

  @override
  List<Object?> get props => [score, segments, results];
}

class ScoreError extends ScoreState {
  final String message;

  ScoreError(this.message);

  @override
  List<Object?> get props => [message];
}
