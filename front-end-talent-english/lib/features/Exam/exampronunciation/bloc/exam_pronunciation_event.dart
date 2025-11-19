import 'package:equatable/equatable.dart';

abstract class PronunciationEvent extends Equatable {
  const PronunciationEvent();

  @override
  List<Object?> get props => [];
}

class StartRecording extends PronunciationEvent {}

class StopRecording extends PronunciationEvent {}

class PlayTts extends PronunciationEvent {
  final String phrase;

  const PlayTts(this.phrase);

  @override
  List<Object?> get props => [phrase];
}


class MoveToNextSentence extends PronunciationEvent {}

class ShowSessionSummary extends PronunciationEvent {}

class CloseSessionSummary extends PronunciationEvent {}

class FetchExamSentences extends PronunciationEvent {
  final int examId;
  
  const FetchExamSentences(this.examId);
}

class RestartExam extends PronunciationEvent {
  final int examId;
  
  const RestartExam(this.examId);
  
  @override
  List<Object?> get props => [examId];
}


class ClearRestartSuccess extends PronunciationEvent {}