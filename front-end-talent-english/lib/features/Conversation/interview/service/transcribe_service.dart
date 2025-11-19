import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../../../../core/constants.dart';

class TranscriptionService {
  final baseUrl = Env.baseUrl;
  
  Future<String?> transcribeAudio(String audioPath) async {
    try {
      final file = File(audioPath);
      
      if (!await file.exists()) {
        print('❌ Audio file does not exist: $audioPath');
        return null;
      }

      // Create multipart request
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/transcribe'),
      );

      // Add the audio file
      request.files.add(
        await http.MultipartFile.fromPath(
          'file',
          audioPath,
          filename: 'audio.m4a',
        ),
      );

      // Add headers if needed
      request.headers.addAll({
        'Content-Type': 'multipart/form-data',
      });

      print('📤 Sending transcription request to: $baseUrl/transcribe');
      print('📁 Audio file: $audioPath');

      // Send the request
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      print('📥 Transcription response status: ${response.statusCode}');
      print('📥 Transcription response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final transcribedText = data['text'] as String?;
        
        if (transcribedText != null && transcribedText.trim().isNotEmpty) {
          print('✅ Transcription successful: $transcribedText');
          return transcribedText.trim();
        } else {
          print('❌ No text in transcription response');
          return null;
        }
      } else {
        print('❌ Transcription failed with status: ${response.statusCode}');
        print('❌ Error response: ${response.body}');
        return null;
      }
    } catch (e) {
      print('❌ Error during transcription: $e');
      return null;
    }
  }
}