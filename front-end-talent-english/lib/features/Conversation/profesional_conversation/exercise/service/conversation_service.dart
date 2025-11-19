// conversation_service.dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../../../../../core/constants.dart';

class ConversationService {
  final baseUrl = Env.baseUrl;

  Future<String> startConversation() async {
    final res = await http.get(Uri.parse('$baseUrl/conversation/start'));
    if (res.statusCode == 200) {
      return json.decode(res.body)['topic'];
    } else {
      throw Exception('Failed to start conversation');
    }
  }

  Future<String> sendMessage(String userInput, String duration) async {
    final res = await http.post(
      Uri.parse('$baseUrl/conversation/chat'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'user_input': userInput, 'duration': duration}),
    );
    if (res.statusCode == 200) {
      return json.decode(res.body)['response'];
    } else {
      throw Exception('Failed to send message');
    }
  }

  Future<String> transcribeAudio(String audioPath) async {
    try {
      
      final file = File(audioPath);
      
      if (!file.existsSync()) {
        throw Exception('Audio file not found at: $audioPath');
      }

      final fileSize = await file.length();
      
      if (fileSize == 0) {
        throw Exception('Audio file is empty (0 bytes)');
      }

      try {
        await file.openRead().take(1).toList();
      } catch (e) {
        throw Exception('Audio file is not readable: $e');
      }

      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/transcribe'),
      );

      request.headers.addAll({
        'Accept': 'application/json',
      });

      final multipartFile = await http.MultipartFile.fromPath(
        'file',
        audioPath,
        filename: audioPath.split('/').last,
      );
      
      request.files.add(multipartFile);
      
      final streamedResponse = await request.send().timeout(
        const Duration(seconds: 30),
        onTimeout: () {
          throw Exception('Transcription request timed out');
        },
      );


      final response = await http.Response.fromStream(streamedResponse);
      

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        String transcribedText = '';
        if (data is Map<String, dynamic>) {
          transcribedText = data['text'] ?? 
                           data['transcript'] ?? 
                           data['transcription'] ?? 
                           data['result'] ?? '';
        } else if (data is String) {
          transcribedText = data;
        }
        
        if (transcribedText.isEmpty) {
          return 'Audio could not be transcribed';
        }
        
        return transcribedText;
      } else {
        String errorMessage = 'Failed to transcribe audio: ${response.statusCode}';
        
        try {
          final errorData = json.decode(response.body);
          if (errorData is Map<String, dynamic> && errorData.containsKey('error')) {
            errorMessage += ' - ${errorData['error']}';
          }
        } catch (e) {
        }
        
        throw Exception(errorMessage);
      }
    } catch (e) {
      
      if (e is Exception) {
        rethrow;
      } else {
        throw Exception('Transcription error: $e');
      }
    }
  }

  Future<Map<String, dynamic>> fetchReport(String token) async {
    final res = await http.get(
      Uri.parse('$baseUrl/conversation/report'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );
    if (res.statusCode == 200) {
      return json.decode(res.body);
    } else {
      throw Exception('Failed to fetch report');
    }
  }
}