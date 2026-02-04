abstract class ConversationEvent {}

class StartConversationEvent extends ConversationEvent {
  final int topicId;
  StartConversationEvent({this.topicId = 1});
}

class SendUserMessageEvent extends ConversationEvent {
  final String message;
  final String duration;
  final int topicId;

  SendUserMessageEvent(this.message, this.duration, {this.topicId = 1});
}

class SendAudioMessageEvent extends ConversationEvent {
  final String audioPath;
  final String duration;
  final int topicId;

  SendAudioMessageEvent(this.audioPath, this.duration, {this.topicId = 1});
}

class FinishConversationEvent extends ConversationEvent {}