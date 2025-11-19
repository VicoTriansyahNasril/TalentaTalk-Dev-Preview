abstract class InterviewEvent {}

class StartInterview extends InterviewEvent {}

class SendMessage extends InterviewEvent {
  final String message;
  final String? duration;

  SendMessage(this.message, {this.duration});

  @override
  List<Object?> get props => [message, duration];
}

class SubmitSummary extends InterviewEvent {
  final int talentId;

  SubmitSummary(this.talentId);
}

class FetchSummary extends InterviewEvent {
  
}