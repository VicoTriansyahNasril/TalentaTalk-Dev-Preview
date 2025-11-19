import 'package:equatable/equatable.dart';
import '../widgets/pronunciation_result_dialog.dart';

class PronunciationSentencesState extends Equatable {
  final bool isRecording;
  final String phonemeResult;
  final double score;
  final String phrase;
  final String ipa;
  final String idContent;
  final List<int> contentQueue;
  final int currentIndex;
  final bool isFinished;
  final String errorMessage;
  final String phonemeCategory;
  final List<PhonemeResult> phonemeResults;

  const PronunciationSentencesState({
    this.isRecording = false,
    this.phonemeResult = '',
    this.score = 0.0,
    this.phrase = '',
    this.ipa = '',
    this.idContent = '',
    this.contentQueue = const [],
    this.currentIndex = 0,
    this.isFinished = false,
    this.errorMessage = '',
    this.phonemeCategory = '',
    this.phonemeResults = const [],
  });

  PronunciationSentencesState copyWith({
    bool? isRecording,
    String? phonemeResult,
    double? score,
    String? phrase,
    String? ipa,
    String? idContent,
    List<int>? contentQueue,
    int? currentIndex,
    bool? isFinished,
    String? errorMessage,
    String? phonemeCategory,
    List<PhonemeResult>? phonemeResults,
    
  }) {
    return PronunciationSentencesState(
      isRecording: isRecording ?? this.isRecording,
      phonemeResult: phonemeResult ?? this.phonemeResult,
      score: score ?? this.score,
      phrase: phrase ?? this.phrase,
      ipa: ipa ?? this.ipa,
      idContent: idContent ?? this.idContent,
      contentQueue: contentQueue ?? this.contentQueue,
      currentIndex: currentIndex ?? this.currentIndex,
      isFinished: isFinished ?? this.isFinished,
      errorMessage: errorMessage ?? this.errorMessage,
      phonemeCategory: phonemeCategory ?? this.phonemeCategory,
      phonemeResults: phonemeResults ?? this.phonemeResults,
    );
  }

  @override
  List<Object?> get props => [
        phrase,
        ipa,
        idContent,
        phonemeCategory,
        isRecording,
        phonemeResult,
        phonemeResults,
        score,
        errorMessage,
      ];
}
