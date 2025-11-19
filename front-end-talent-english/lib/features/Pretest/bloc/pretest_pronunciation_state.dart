import 'package:equatable/equatable.dart';

class PracticePronunciationState extends Equatable {
  final List<PronunciationSentence> sentences;
  final int currentIndex;
  final bool isLoading;
  final bool isRecording;
  final bool isSubmitting;
  final String errorMessage;
  final double score;
  final List<PhonemeResult> phonemeResults;
  final List<CompletedSentenceResult> completedSentences;
  final bool showPracticeResult;
  final bool showFinalSummary;
  final double averageScore;
  final bool isSubmittingScore;
  final bool shouldNavigateToSummary;

  const PracticePronunciationState({
    this.sentences = const [],
    this.currentIndex = 0,
    this.isLoading = false,
    this.isRecording = false,
    this.isSubmitting = false,
    this.errorMessage = '',
    this.score = 0.0,
    this.phonemeResults = const [],
    this.completedSentences = const [],
    this.showPracticeResult = false,
    this.showFinalSummary = false,
    this.averageScore = 0.0,
    this.isSubmittingScore = false,
    this.shouldNavigateToSummary = false,
  });

  PronunciationSentence? get currentSentence {
    if (currentIndex < sentences.length) {
      return sentences[currentIndex];
    }
    return null;
  }

  PracticePronunciationState copyWith({
    List<PronunciationSentence>? sentences,
    int? currentIndex,
    bool? isLoading,
    bool? isRecording,
    bool? isSubmitting,
    String? errorMessage,
    double? score,
    List<PhonemeResult>? phonemeResults,
    List<CompletedSentenceResult>? completedSentences,
    bool? showPracticeResult,
    bool? showFinalSummary,
    double? averageScore,
    bool? isSubmittingScore,
    bool? shouldNavigateToSummary,
  }) {
    return PracticePronunciationState(
      sentences: sentences ?? this.sentences,
      currentIndex: currentIndex ?? this.currentIndex,
      isLoading: isLoading ?? this.isLoading,
      isRecording: isRecording ?? this.isRecording,
      isSubmitting: isSubmitting ?? this.isSubmitting,
      errorMessage: errorMessage ?? this.errorMessage,
      score: score ?? this.score,
      phonemeResults: phonemeResults ?? this.phonemeResults,
      completedSentences: completedSentences ?? this.completedSentences,
      showPracticeResult: showPracticeResult ?? this.showPracticeResult,
      showFinalSummary: showFinalSummary ?? this.showFinalSummary,
      averageScore: averageScore ?? this.averageScore,
      isSubmittingScore: isSubmittingScore ?? this.isSubmittingScore,
      shouldNavigateToSummary: shouldNavigateToSummary ?? this.shouldNavigateToSummary,
    );
  }

  @override
  List<Object?> get props => [
        sentences,
        currentIndex,
        isLoading,
        isRecording,
        isSubmitting,
        errorMessage,
        score,
        phonemeResults,
        completedSentences,
        showPracticeResult,
        showFinalSummary,
        averageScore,
        isSubmittingScore,
        shouldNavigateToSummary,
      ];
}

class PronunciationSentence extends Equatable {
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

  factory PronunciationSentence.fromJson(Map<String, dynamic> json) {
    return PronunciationSentence(
      id: json['id'] is int ? json['id'] : int.tryParse(json['id'].toString()) ?? 0,
      content: json['kalimat'] as String? ?? '',
      phoneme: json['fonem'] as String? ?? '',
      category: json['kategori'] as String? ?? '',
    );
  }

  @override
  List<Object?> get props => [id, content, phoneme, category];
}

class PhonemeResult extends Equatable {
  final String targetPhoneme;
  final String userPhoneme;
  final bool isCorrect;

  const PhonemeResult({
    required this.targetPhoneme,
    required this.userPhoneme,
    required this.isCorrect,
  });

  factory PhonemeResult.fromJson(Map<String, dynamic> json) {
    return PhonemeResult(
      targetPhoneme: json['target_phoneme'] as String? ?? '',
      userPhoneme: json['user_phoneme'] as String? ?? '',
      isCorrect: json['is_correct'] as bool? ?? false,
    );
  }

  @override
  List<Object?> get props => [targetPhoneme, userPhoneme, isCorrect];
}

class CompletedSentenceResult extends Equatable {
  final PronunciationSentence sentence;
  final double score;
  final List<PhonemeResult> phonemeResults;

  const CompletedSentenceResult({
    required this.sentence,
    required this.score,
    required this.phonemeResults,
  });

  @override
  List<Object?> get props => [sentence, score, phonemeResults];
}