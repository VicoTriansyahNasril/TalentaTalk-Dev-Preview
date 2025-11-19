import 'package:equatable/equatable.dart';

class PronunciationSentence {
  final int id;
  final String content;
  final String phoneme;
  final String category;

  const PronunciationSentence({
    required this.id,
    required this.content,
    required this.phoneme, 
    required this.category,
  });
}

class PhonemeResult {
  final String targetPhoneme;
  final String userPhoneme;
  final bool isCorrect;
  final String status; 

  const PhonemeResult({
    required this.targetPhoneme,
    required this.userPhoneme,
    required this.isCorrect,
    required this.status,
  });

  factory PhonemeResult.fromJson(Map<String, dynamic> json) {
    return PhonemeResult(
      targetPhoneme: json['target'] ?? '-',
      userPhoneme: json['user'] ?? '-',
      isCorrect: json['status'] == 'correct',
      status: json['status'] ?? '-',
    );
  }
}

class CompletedSentenceResult {
  final PronunciationSentence sentence;
  final double score;
  final List<PhonemeResult> phonemeResults;

  const CompletedSentenceResult({
    required this.sentence,
    required this.score,
    required this.phonemeResults,
  });
}

class PronunciationSentencesState extends Equatable {
  final bool isLoading;
  final bool isRecording;
  final String category;
  final List<PronunciationSentence> sentences;
  final int currentIndex;
  final List<PhonemeResult> phonemeResults;
  final double score;
  final String errorMessage;
  final List<CompletedSentenceResult> completedSentences;
  final bool showSessionSummary;
  final int examId;
  final bool isSubmitting;
  final bool isRestarting;
  final bool justRestarted;

  PronunciationSentence? get currentSentence => 
    currentIndex >= 0 && currentIndex < sentences.length 
      ? sentences[currentIndex] 
      : null;

  double calculateAverageScore() {
    if (completedSentences.isEmpty) return 0.0;
    
    final total = completedSentences.fold<double>(
      0.0, (sum, result) => sum + result.score
    );
    
    return total / completedSentences.length;
  }

  const PronunciationSentencesState({
    this.isLoading = false,
    this.isRecording = false,
    this.category = '',
    this.sentences = const [],
    this.currentIndex = 0,
    this.phonemeResults = const [],
    this.score = 0.0,
    this.errorMessage = '',
    this.completedSentences = const [],
    this.showSessionSummary = false,
    this.examId = 0,
    this.isSubmitting = false,
    this.isRestarting = false,
    this.justRestarted = false,
  });

  PronunciationSentencesState copyWith({
    bool? isLoading,
    bool? isRecording,
    String? category,
    List<PronunciationSentence>? sentences,
    int? currentIndex,
    List<PhonemeResult>? phonemeResults,
    double? score,
    String? errorMessage,
    List<CompletedSentenceResult>? completedSentences,
    bool? showSessionSummary,
    int? examId,
    bool? isSubmitting,
    bool? isRestarting,
    bool? justRestarted,
  }) {
    return PronunciationSentencesState(
      isLoading: isLoading ?? this.isLoading,
      isRecording: isRecording ?? this.isRecording,
      category: category ?? this.category,
      sentences: sentences ?? this.sentences,
      currentIndex: currentIndex ?? this.currentIndex,
      phonemeResults: phonemeResults ?? this.phonemeResults,
      score: score ?? this.score,
      errorMessage: errorMessage ?? this.errorMessage,
      completedSentences: completedSentences ?? this.completedSentences,
      showSessionSummary: showSessionSummary ?? this.showSessionSummary,
      examId: examId ?? this.examId,
      isSubmitting: isSubmitting ?? this.isSubmitting,
      isRestarting: isRestarting ?? this.isRestarting,
      justRestarted: justRestarted ?? this.justRestarted,
    );
  }

  @override
  List<Object?> get props => [
    isLoading, 
    isRecording,
    category,
    sentences,
    currentIndex,
    phonemeResults,
    score,
    errorMessage,
    completedSentences,
    showSessionSummary,
    examId,
    isSubmitting,
    isRestarting,
    justRestarted,
  ];
}