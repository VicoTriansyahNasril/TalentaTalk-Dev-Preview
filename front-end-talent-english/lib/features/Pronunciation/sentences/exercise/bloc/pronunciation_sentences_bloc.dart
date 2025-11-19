
import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:convert';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'pronunciation_sentences_event.dart';
import 'pronunciation_sentences_state.dart';
import '../../../../../services/tts_service.dart';
import '../widgets/pronunciation_result_dialog.dart';

class PronunciationSentencesBloc extends Bloc<PronunciationEvent, PronunciationSentencesState> {
  final TtsService ttsService;
  final String baseUrl;

  final AudioRecorder _recorder = AudioRecorder();
  Timer? _timer;
  String? _recordedPath;

  PronunciationSentencesBloc({required this.ttsService, required this.baseUrl})
      : super(const PronunciationSentencesState()) {
    on<StartRecording>(_onStartRecording);
    on<StopRecording>(_onStopRecording);
    on<PlayTts>(_onPlayTts);
    on<FetchSentenceByPhoneme>(_onFetchSentenceByPhoneme);
    on<FetchSentenceById>(_onFetchSentenceById);
    on<ClearResults>(_onClearResults);
  }

  Future<void> _onStartRecording(
    StartRecording event, Emitter<PronunciationSentencesState> emit) async {
  
    if (await _recorder.hasPermission()) {

      if (_recordedPath != null) {
        final oldFile = File(_recordedPath!);
        if (await oldFile.exists()) {
          await oldFile.delete();
          print('🗑️ Rekaman lama dihapus: $_recordedPath');
        }
      }

      final path = await _getPath();

      await _recorder.start(
        RecordConfig(
          encoder: AudioEncoder.wav,
          sampleRate: 16000,
          numChannels: 1,
        ),              
        path: path,
      );

      _recordedPath = path;

      emit(state.copyWith(isRecording: true));
    }
  }

  Future<void> _onStopRecording(StopRecording event, Emitter<PronunciationSentencesState> emit) async {
    _timer?.cancel();
    final path = await _recorder.stop();
    emit(state.copyWith(isRecording: false));

    if (path == null) return;

    try {
      print('Stop mulai dan Mengirim rekaman ke /hasil_controller dengan idContent: ${state.idContent}');

      final prefs = await SharedPreferences.getInstance();
      final userId = prefs.getString('token');
      if (userId == null) {
        emit(state.copyWith(errorMessage: 'User ID tidak ditemukan di SharedPreferences'));
        return;
      } 
      final uri = Uri.parse('$baseUrl/phoneme/compare');
      final request = http.MultipartRequest('POST', uri)
        ..fields['idContent'] = state.idContent
        ..files.add(await http.MultipartFile.fromPath('file', path))
        ..headers['Authorization'] = 'Bearer $userId';
      
      final response = await request.send();
      final body = await response.stream.bytesToString();
      print('📥 Response body: $body');

      if (response.statusCode == 200) {
        final data = json.decode(body);
        
        final similarityPercentStr = data['similarity_percent'] as String;
        final similarityPercent = double.parse(similarityPercentStr.replaceAll('%', ''));
        
        final List<PhonemeResult> phonemeComparison = (data['phoneme_comparison'] as List)
            .map((item) => PhonemeResult.fromJson(item as Map<String, dynamic>))
            .toList();
        
        emit(state.copyWith(
          phonemeResults: phonemeComparison,
          score: similarityPercent / 100,
          phonemeResult: 'Score: ${similarityPercentStr}',
        ));
        
        print('📤 Menampilkan hasil /compare dengan idContent: ${state.idContent}');
      }
    } catch (e) {
      print('❌ Gagal kirim ke /compare: $e');
      emit(state.copyWith(errorMessage: 'Failed to process recording: $e'));
    }
  }
  

  Future<void> _onPlayTts(PlayTts event, Emitter<PronunciationSentencesState> emit) async {
    await ttsService.speak(event.phrase);
  }

  Future<String> _getPath() async {
    final dir = await getApplicationDocumentsDirectory();
    return '${dir.path}/recording.wav';

  }

  void _onClearResults(ClearResults event, Emitter<PronunciationSentencesState> emit) {
    emit(state.copyWith(
      phonemeResults: const [],
      phonemeResult: '', 
      score: 0.0,
    ));
  }


  Future<void> _onFetchSentenceByPhoneme(
    FetchSentenceByPhoneme event,
    Emitter<PronunciationSentencesState> emit,
  ) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/phoneme/random_sentence/${event.phoneme}'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['content'] != null && data['phoneme'] != null) {
          final phrase = data['content'] as String;
          final ipa = data['phoneme'] as String;
          emit(state.copyWith(phrase: phrase, ipa: ipa));
        } else {
          print("⚠️ Tidak ada data untuk fonem tersebut");
        }
      } else {
        print('❌ Server error: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Error mengambil kalimat berdasarkan fonem: $e');
    }
  }

  Future<void> _onFetchSentenceById(
    FetchSentenceById event,
    Emitter<PronunciationSentencesState> emit,
  ) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/phoneme/sentence_by_id/${event.id}'));

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));

        if (data['content'] != null && data['phoneme'] != null && data['idContent'] != null) {
          emit(state.copyWith(
            phrase: data['content'],
            ipa: data['phoneme'],
            idContent: data['idContent'].toString(),
            phonemeCategory: data['phoneme_category'] ?? '',
            errorMessage: '',
          ));
        } else {
          emit(state.copyWith(errorMessage: '⚠️ No word found for the given ID.'));
        }
      } else {
        emit(state.copyWith(errorMessage: '❌ Server error: ${response.statusCode}'));
      }
    } catch (e) {
      emit(state.copyWith(errorMessage: '❌ Failed to fetch word by ID: $e'));
    }
  }

}
