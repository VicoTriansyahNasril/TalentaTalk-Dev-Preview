import 'dart:convert';
import 'dart:developer' as dev;
import 'dart:io';
import 'package:http/http.dart' as http;
import '../../../../../core/constants.dart';

class ConversationService {
  final baseUrl = Env.baseUrl;

  Future<String> startConversation() async {
    return "Please start speaking about your chosen topic.";
  }

  Future<String> sendMessage(
    String userInput,
    String duration,
    int topicId,
  ) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/conversation/chat'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'user_input': userInput,
          'duration': duration,
          'topic_id': topicId,
        }),
      );

      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        if (data['data'] != null && data['data']['response'] != null) {
          return data['data']['response'];
        } else {
          return "No response from AI.";
        }
      } else {
        throw Exception('Failed to send message: ${res.body}');
      }
    } catch (e) {
      dev.log("Error sending message: $e");
      rethrow;
    }
  }

  Future<String> transcribeAudio(String audioPath) async {
    try {
      final file = File(audioPath);
      if (!file.existsSync()) {
        throw Exception('Audio file not found at path: $audioPath');
      }

      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/transcribe'),
      );

      final multipartFile = await http.MultipartFile.fromPath(
        'file',
        audioPath,
      );
      request.files.add(multipartFile);

      dev.log("Uploading audio for transcription: $audioPath");

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      dev.log("Transcription status: ${response.statusCode}");
      dev.log("Transcription body: ${response.body}");

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['data']['text'] ?? '';
      } else {
        throw Exception(
          'Transcription failed with status: ${response.statusCode}',
        );
      }
    } catch (e) {
      dev.log("Error transcribing audio: $e");
      rethrow;
    }
  }

  Future<Map<String, dynamic>> fetchReport(String token) async {
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/conversation/report'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (res.statusCode == 200) {
        final body = json.decode(res.body);
        return body['data'];
      } else {
        throw Exception('Failed to fetch report: ${res.statusCode}');
      }
    } catch (e) {
      dev.log("Error fetching report: $e");
      rethrow;
    }
  }
}
