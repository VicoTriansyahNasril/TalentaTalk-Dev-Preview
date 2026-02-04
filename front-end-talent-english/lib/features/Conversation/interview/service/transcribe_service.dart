import 'dart:convert';
import 'dart:developer' as dev;
import 'dart:io';
import 'package:http/http.dart' as http;
import '../../../../core/constants.dart';

class TranscriptionService {
  final baseUrl = Env.baseUrl;

  Future<String?> transcribeAudio(String audioPath) async {
    try {
      final file = File(audioPath);

      if (!await file.exists()) {
        dev.log('❌ Audio file does not exist: $audioPath');
        return null;
      }

      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/transcribe'),
      );

      request.files.add(
        await http.MultipartFile.fromPath(
          'file',
          audioPath,
          filename: 'audio.m4a',
        ),
      );

      request.headers.addAll({'Content-Type': 'multipart/form-data'});

      dev.log('📤 Sending transcription request to: $baseUrl/transcribe');
      dev.log('📁 Audio file: $audioPath');

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      dev.log('📥 Transcription response status: ${response.statusCode}');
      dev.log('📥 Transcription response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final transcribedText = data['text'] as String?;

        if (transcribedText != null && transcribedText.trim().isNotEmpty) {
          dev.log('✅ Transcription successful: $transcribedText');
          return transcribedText.trim();
        } else {
          dev.log('❌ No text in transcription response');
          return null;
        }
      } else {
        dev.log('❌ Transcription failed with status: ${response.statusCode}');
        dev.log('❌ Error response: ${response.body}');
        return null;
      }
    } catch (e) {
      dev.log('❌ Error during transcription: $e');
      return null;
    }
  }
}
