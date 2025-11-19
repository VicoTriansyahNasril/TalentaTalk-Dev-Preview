import '../model/chat_message.dart';
import '../model/interview_summary.dart'; // buat model ringkasan
import '../service/interview_service.dart';

class InterviewRepository {
  final InterviewService service;

  InterviewRepository({required this.service});

  Future<ChatMessage?> startInterview() async {
    final question = await service.startInterview();
    if (question != null) {
      return ChatMessage(message: question, isUser: false);
    }
    return null;
  }

  Future<(List<ChatMessage>, bool)> sendAnswer(String answer, String duration) async {
    final response = await service.sendAnswer(answer, duration);
    if (response == null) return (<ChatMessage>[], false);
    
    final List<ChatMessage> messages = [];
    if (response['feedback'] != null) {
      messages.add(ChatMessage(message: response['feedback'], isUser: false));
    }
    if (response['ai_feedback'] != null) {
      messages.add(ChatMessage(message: response['ai_feedback'], isUser: false));
    }
    if (response['question'] != null) {
      messages.add(ChatMessage(message: response['question'], isUser: false));
    } else if (response['message'] != null) {
     
      messages.add(ChatMessage(message: response['message'], isUser: false));
    }
    final bool isCompleted = response['interview_completed'] == true || response['status'] == 'completed';
    return (messages, isCompleted);
  }

  Future<InterviewSummary?> fetchSummary() async {
    final json = await service.getSummary();
    if (json != null && json['success'] == true) {
      return InterviewSummary.fromJson(json);
    }
    return null;
  }
}
