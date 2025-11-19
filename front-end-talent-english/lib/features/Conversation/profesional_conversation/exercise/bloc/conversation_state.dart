import 'package:equatable/equatable.dart';
import '../model/chat_message.dart';
import '../model/report_result.dart';

abstract class ConversationState extends Equatable {
  const ConversationState();
  
  @override
  List<Object> get props => [];
}

class ConversationInitial extends ConversationState {}

class ConversationLoading extends ConversationState {}

class ConversationInProgress extends ConversationState {
  final List<ChatMessage> messages;
  
  const ConversationInProgress(this.messages);
  
  @override
  List<Object> get props => [messages];
}

class ConversationFinished extends ConversationState {
  final List<ReportResult> report;
  final Map<String, dynamic> saveStatus;
  final int talentId;
  
  const ConversationFinished({
    required this.report, 
    required this.saveStatus, 
    required this.talentId
  });
  
  @override
  List<Object> get props => [report, saveStatus, talentId];
}

class ConversationError extends ConversationState {
  final String message;
  
  const ConversationError(this.message);
  
  @override
  List<Object> get props => [message];
}