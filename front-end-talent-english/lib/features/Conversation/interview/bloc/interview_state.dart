import 'package:equatable/equatable.dart';
import '../model/chat_message.dart';
import '../model/interview_summary.dart';

class InterviewState extends Equatable {
  final List<ChatMessage> messages;
  final bool isLoading;
  final InterviewSummary? summary;
  final bool interviewCompleted;

  const InterviewState({
    required this.messages,
    this.isLoading = false,
    this.summary,
    this.interviewCompleted = false,
  });

  InterviewState copyWith({
    List<ChatMessage>? messages,
    bool? isLoading,
    InterviewSummary? summary,
    bool? interviewCompleted,
  }) {
    return InterviewState(
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
      summary: summary ?? this.summary,
      interviewCompleted: interviewCompleted ?? this.interviewCompleted,
    );
  }

  @override
  List<Object?> get props => [messages, isLoading, summary, interviewCompleted];
}

