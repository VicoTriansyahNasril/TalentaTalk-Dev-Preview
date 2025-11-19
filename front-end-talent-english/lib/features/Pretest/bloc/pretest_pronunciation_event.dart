abstract class PracticePronunciationEvent {}

class FetchPracticeSentences extends PracticePronunciationEvent {}

class StartRecording extends PracticePronunciationEvent {}

class StopRecording extends PracticePronunciationEvent {}

class PlayTts extends PracticePronunciationEvent {
  final String phrase;
  
  PlayTts(this.phrase);
}

class MoveToNextSentence extends PracticePronunciationEvent {}

class ClosePracticeResult extends PracticePronunciationEvent {}

class SubmitPracticeScore extends PracticePronunciationEvent {}

class CloseFinalSummary extends PracticePronunciationEvent {}