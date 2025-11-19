import '../model/pronunciation_history.dart';
import '../model/conversation_history.dart';
import '../model/interview_history.dart';
import '../model/exam_history.dart';
import '../service/history_service.dart';

class TrainingHistoryRepository {
  final TrainingHistoryService service;
  
  TrainingHistoryRepository({required this.service});
  
  Future<List<PronunciationHistory>> getPronunciationHistory() async {
    final data = await service.fetchData('phoneme');
    return data.map((e) => PronunciationHistory.fromJson(e)).toList();
  }
  
  Future<List<ConversationHistory>> getConversationHistory() async {
    final data = await service.fetchData('conversation');
    return data.map((e) => ConversationHistory.fromJson(e)).toList();
  }
  
  Future<List<InterviewHistory>> getInterviewHistory() async {
    final data = await service.fetchData('interview');
    return data.map((e) => InterviewHistory.fromJson(e)).toList();
  }
  
  Future<List<ExamHistory>> getExamHistory() async {
    final data = await service.fetchData('exam');
    return data.map((e) => ExamHistory.fromJson(e)).toList();
  }
}