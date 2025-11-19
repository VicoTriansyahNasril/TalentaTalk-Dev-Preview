import '../model/conversation_history.dart';
import '../model/interview_history.dart';
import '../model/pronunciation_history.dart';
import '../model/exam_history.dart';

abstract class TrainingHistoryState {}

class TrainingHistoryInitial extends TrainingHistoryState {}

class TrainingHistoryLoading extends TrainingHistoryState {}

class TrainingHistoryLoaded extends TrainingHistoryState {
  final List<PronunciationHistory> pronunciationHistory;
  final List<ConversationHistory> conversationHistory;
  final List<InterviewHistory> interviewHistory;
  final List<ExamHistory> examHistory;

  TrainingHistoryLoaded({
    required this.pronunciationHistory,
    required this.conversationHistory,
    required this.interviewHistory,
    required this.examHistory,
  });
}

class TrainingHistoryError extends TrainingHistoryState {
  final String message;
  TrainingHistoryError(this.message);
}