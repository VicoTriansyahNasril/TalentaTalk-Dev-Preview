import 'package:equatable/equatable.dart';

abstract class PronunciationEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class StartRecording extends PronunciationEvent {}

class StopRecording extends PronunciationEvent {}

class FetchContent extends PronunciationEvent {}

class LoadContentQueue extends PronunciationEvent {}
class NextContent extends PronunciationEvent {}


class PlayTts extends PronunciationEvent {
  final String phrase;
  PlayTts(this.phrase);

  @override
  List<Object?> get props => [phrase];
}

class FetchWordByPhoneme extends PronunciationEvent {
  final String phoneme;

  FetchWordByPhoneme(this.phoneme);

  @override
  List<Object?> get props => [phoneme];
}

class FetchWordById extends PronunciationEvent {
  final int id;

  FetchWordById(this.id);
}


class ResetRecordingCompleted extends PronunciationEvent {}
