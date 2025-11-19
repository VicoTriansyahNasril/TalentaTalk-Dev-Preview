import 'package:equatable/equatable.dart';

abstract class PronunciationEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class StartRecording extends PronunciationEvent {}

class StopRecording extends PronunciationEvent {}

class LoadContentQueue extends PronunciationEvent {}
class NextContent extends PronunciationEvent {}


class PlayTts extends PronunciationEvent {
  final String phrase;
  PlayTts(this.phrase);

  @override
  List<Object?> get props => [phrase];
}

class FetchSentenceByPhoneme extends PronunciationEvent {
  final String phoneme;

  FetchSentenceByPhoneme(this.phoneme);

  @override
  List<Object?> get props => [phoneme];
}

class FetchSentenceById extends PronunciationEvent {
  final int id;

  FetchSentenceById(this.id);
}

class ClearResults extends PronunciationEvent {}

