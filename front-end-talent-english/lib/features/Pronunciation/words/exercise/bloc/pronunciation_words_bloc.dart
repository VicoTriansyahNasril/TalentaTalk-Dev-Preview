import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import '../../../sentences/exercise/widgets/pronunciation_result_dialog.dart';
import 'pronunciation_words_event.dart';
import 'pronunciation_words_state.dart';
import '../../../../../services/tts_service.dart';
import 'package:http_parser/http_parser.dart';
import 'package:shared_preferences/shared_preferences.dart';

class PronunciationWordsBloc extends Bloc<PronunciationEvent, PronunciationWordsState> {
  final TtsService ttsService;
  final String baseUrl;

  final AudioRecorder _recorder = AudioRecorder();
  Timer? _timer;
  String? _recordedPath;

  PronunciationWordsBloc({required this.ttsService, required this.baseUrl})
      : super(const PronunciationWordsState()) {
    on<StartRecording>(_onStartRecording);
    on<StopRecording>(_onStopRecording);
    on<PlayTts>(_onPlayTts);
    on<FetchWordByPhoneme>(_onFetchWordByPhoneme);
    on<ResetRecordingCompleted>(_onResetRecordingCompleted);
    on<FetchWordById>(_onFetchWordById);
  }

  Future<void> _onStartRecording(
    StartRecording event, Emitter<PronunciationWordsState> emit) async {
  
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

  Future<void> _onStopRecording(
    StopRecording event,
    Emitter<PronunciationWordsState> emit,
  ) async {
    _timer?.cancel();
    final path = await _recorder.stop();
    emit(state.copyWith(isRecording: false));

    if (path == null) return;

    try {
      await Future.delayed(const Duration(milliseconds: 200));
      final prefs = await SharedPreferences.getInstance();
      final userId = prefs.getString('token');
      if (userId == null) {
        emit(state.copyWith(errorMessage: 'User ID tidak ditemukan di SharedPreferences'));
        return;
      } 
      final file = File(path);
      final fileBytes = await file.readAsBytes();
      final fileLength = fileBytes.length;

      print('🎙️ [SEND] Preparing to send request to /compare_word');
      print('🆔 idContent: ${state.idContent}');
      print('🧑 userId: $userId');
      print('🔤 filter_phonemes: ${state.phonemeCategory}');
      print('📁 audioPath: $path');
      print('📏 fileSize: $fileLength bytes');

      final uri = Uri.parse('$baseUrl/phoneme/compare_word');
      final multipartFile = http.MultipartFile.fromBytes(
        'file',
        fileBytes,
        filename: 'recording.wav',
        contentType: MediaType('audio', 'wav'),
      );

      final request = http.MultipartRequest('POST', uri)
        ..fields['idContent'] = state.idContent
        ..fields['filter_phonemes'] = state.phonemeCategory
        ..files.add(multipartFile)
        ..headers['Authorization'] = 'Bearer $userId';

      final response = await request.send();
      final body = await response.stream.bytesToString();

      print('📥 Response body: $body');

      if (response.statusCode == 200) {
        final data = json.decode(body);

        final similarity = data['similarity_percent'] as String;
        final similarityPercent = double.parse(similarity.replaceAll('%', ''));
        final List<PhonemeResult> phonemeResults = (data['phoneme_comparison'] as List)
          .map((e) => PhonemeResult(
                target: e['target'] ?? "-",
                user: e['symbol'] ?? "-",
                status: e['status'],
              ))
          .toList();

        emit(state.copyWith(
          phonemeComparison: phonemeResults,
          score: similarityPercent/ 100,
          recordingCompleted: true,
        ));
        print('🔄 New state emitted with score: $similarity');
      } else {
        emit(state.copyWith(errorMessage: '❌ Gagal dari server: ${response.statusCode}'));
      }
    } catch (e) {
      emit(state.copyWith(errorMessage: '❌ Gagal kirim ke /compare_word: $e'));
    }
  }


  Future<void> _onPlayTts(PlayTts event, Emitter<PronunciationWordsState> emit) async {
    await ttsService.speak(event.phrase);
  }

  Future<String> _getPath() async {
    final dir = await getApplicationDocumentsDirectory();
    return '${dir.path}/recording.wav';

  }

  Future<void> _onFetchWordByPhoneme(
    FetchWordByPhoneme event,
    Emitter<PronunciationWordsState> emit,
  ) async {
    try {
      print('📢 Fonem yang diminta: ${event.phoneme}');
      final response = await http.get(Uri.parse('$baseUrl/phoneme/random_word/${event.phoneme}'));

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        print('📥 Data dari API: $data');
        if (data['content'] != null && data['phoneme'] != null && data['idContent'] != null) {
          final phrase = data['content'] as String;
          final ipa = data['phoneme'] as String;
          final idContent = data['idContent'].toString();
          final phonemeCategory = data['phoneme_category'] ?? '';

          emit(state.copyWith(
            phrase: phrase,
            ipa: ipa,
            idContent: idContent,
            phonemeCategory: phonemeCategory,
            errorMessage: '',
        
          ));
        } else {
          emit(state.copyWith(errorMessage: '⚠️ Tidak ada materi untuk fonem ini'));
          
        }
      } else {
        emit(state.copyWith(errorMessage: '❌ Server error: ${response.statusCode}'));
      }
    } catch (e) {
      emit(state.copyWith(errorMessage: '❌ Gagal mengambil data: $e'));
    }
  }

  Future<void> _onFetchWordById(
    FetchWordById event,
    Emitter<PronunciationWordsState> emit,
  ) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/phoneme/word_by_id/${event.id}'));

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));

        if (data['content'] != null && data['phoneme'] != null && data['idContent'] != null) {
          emit(state.copyWith(
            phrase: data['content'],
            ipa: data['phoneme'],
            idContent: data['idContent'].toString(),
            phonemeCategory: data['phoneme_category'] ?? '',
            errorMessage: '',
            meaning: data['meaning'] ?? '',
            definition: data['definition'] ?? '',
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

  void _onResetRecordingCompleted(
    ResetRecordingCompleted event, 
    Emitter<PronunciationWordsState> emit
  ) {
    emit(state.copyWith(recordingCompleted: false));
  }

}
