import 'package:equatable/equatable.dart';

import '../../../sentences/exercise/widgets/pronunciation_result_dialog.dart';

class PronunciationWordsState extends Equatable {
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
  final bool recordingCompleted;
  final int idTalent;
  final List<PhonemeResult> phonemeComparison;
  final String meaning;
  final String definition;


  const PronunciationWordsState({
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
    this.recordingCompleted = false,
    this.idTalent = 0,
    this.phonemeComparison = const [],
    this.meaning = '',
    this.definition = '',
  });

  PronunciationWordsState copyWith({
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
    bool? recordingCompleted,
    int? idTalent,
    List<PhonemeResult>? phonemeComparison,
    String? meaning,
    String? definition,
  }) {
    return PronunciationWordsState(
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
      recordingCompleted: recordingCompleted ?? this.recordingCompleted, 
      idTalent: idTalent ?? this.idTalent,
      phonemeComparison: phonemeComparison ?? this.phonemeComparison,
      meaning: meaning ?? this.meaning,
      definition: definition ?? this.definition,
    );
  }

  @override
  List<Object?> get props => [
    isRecording, 
    phonemeResult, 
    score, phrase, 
    ipa, 
    idContent, 
    contentQueue, 
    currentIndex, 
    isFinished, 
    errorMessage,
    phonemeCategory, 
    recordingCompleted, 
    idTalent, 
    phonemeComparison,
    meaning,
    definition,
  ];
}
