import 'dart:developer' as dev;
import 'package:shared_preferences/shared_preferences.dart';
import '../service/conversation_service.dart';
import '../model/report_result.dart';

class ConversationRepository {
  final ConversationService service;
  ConversationRepository({required this.service});

  Future<String> startConversation() => service.startConversation();

  Future<String> sendMessage(String userInput, String duration, int topicId) =>
      service.sendMessage(userInput, duration, topicId);

  Future<String> transcribeAudio(String audioPath) =>
      service.transcribeAudio(audioPath);

  Future<Map<String, dynamic>> fetchReport() async {
    try {
      final token = await _getToken();
      final data = await service.fetchReport(token);

      final reportList =
          (data['report'] as List?)
              ?.map((e) => ReportResult.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [];

      return {
        'report': reportList,
        'saveStatus': {
          'success': data['success'] ?? false,
          'message': data['message'] ?? '',
          'id': data['id'],
        },
        'talentId': data['talent_id'] ?? 0,
      };
    } catch (e) {
      dev.log('Error in fetchReport: $e');
      return {
        'report': <ReportResult>[],
        'saveStatus': {
          'success': false,
          'message': 'Failed to fetch report: ${e.toString()}',
          'id': null,
        },
        'talentId': 0,
      };
    }
  }

  Future<String> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token') ?? '';
    if (token.isEmpty) {
      throw Exception('Authentication token not found');
    }
    return token;
  }
}
