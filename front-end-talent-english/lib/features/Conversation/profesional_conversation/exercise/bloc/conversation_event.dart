abstract class ConversationEvent {}

class StartConversationEvent extends ConversationEvent {}

class SendUserMessageEvent extends ConversationEvent {
  final String message;
  final String duration;

  SendUserMessageEvent(this.message, this.duration);
}

class SendAudioMessageEvent extends ConversationEvent {
  final String audioPath;
  final String duration;

  SendAudioMessageEvent(this.audioPath, this.duration);
}

class FinishConversationEvent extends ConversationEvent {}
