import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'exam_pronunciation_event.dart';
import 'exam_pronunciation_state.dart';
import '../../../../../services/tts_service.dart';

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
    on<FetchExamSentences>(_onFetchExamSentences);
    on<MoveToNextSentence>(_onMoveToNextSentence);
    on<ShowSessionSummary>(_onShowSessionSummary);
    on<CloseSessionSummary>(_onCloseSessionSummary);
    on<RestartExam>(_onRestartExam);
    on<ClearRestartSuccess>(_onClearRestartSuccess);
  }

  Future<void> _onStartRecording(
    StartRecording event, Emitter<PronunciationSentencesState> emit) async {
  
    if (await _recorder.hasPermission()) {
      if (_recordedPath != null) {
        final oldFile = File(_recordedPath!);
        if (await oldFile.exists()) {
          await oldFile.delete();
          print('🗑️ Deleting old recording: $_recordedPath');
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
    Emitter<PronunciationSentencesState> emit,
  ) async {
    _timer?.cancel();
    final path = await _recorder.stop();
    emit(state.copyWith(isRecording: false));
    emit(state.copyWith(isSubmitting: true));
    print('🕒 isSubmitting: ${state.isSubmitting}');
    if (path == null || state.currentSentence == null || state.examId == null) return;

    try {
      print('🎙️ Sending recording for evaluation (with examId: ${state.examId})');
      print('🎙️ Sen kalimat: ${state.currentSentence!.id})');
      
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      if (token == null) {
        emit(state.copyWith(errorMessage: 'User token not found'));
        return;
      }
      
      final uri = Uri.parse('$baseUrl/exam/compare');
      final request = http.MultipartRequest('POST', uri)
        ..fields['idContent'] = state.currentSentence!.id.toString()
        ..fields['idUjian'] = state.examId.toString()
        ..files.add(await http.MultipartFile.fromPath('file', path))
        ..headers['Authorization'] = 'Bearer $token';

      final response = await request.send();
      final body = await response.stream.bytesToString();
      print('📥 Response from /exam/compare: $body');

      if (response.statusCode == 200) {
        final data = json.decode(body);

        final similarityPercentStr = data['similarity_percent'] as String;
        print('🔍 Raw similarity percent: $similarityPercentStr (type: ${similarityPercentStr.runtimeType})');
        final similarityPercent = double.tryParse(similarityPercentStr.replaceAll('%', '')) ?? 0.0;

        final phonemeComparison = (data['phoneme_comparison'] as List)
            .map((e) => PhonemeResult.fromJson(e))
            .toList();

        final completedSentence = CompletedSentenceResult(
          sentence: state.currentSentence!,
          score: similarityPercent / 100,
          phonemeResults: phonemeComparison,
        );

        emit(state.copyWith(
          completedSentences: [...state.completedSentences, completedSentence],
          score: similarityPercent / 100,
          phonemeResults: phonemeComparison,
          isSubmitting: false,
        ));
      } else {
        emit(state.copyWith(errorMessage: '❌ Server error: ${response.statusCode}', isSubmitting: false,));
      }
    } catch (e) {
      emit(state.copyWith(errorMessage: '❌ Failed to evaluate recording: $e', isSubmitting: false,));
    }
  }

  
  Future<void> _onPlayTts(PlayTts event, Emitter<PronunciationSentencesState> emit) async {
    await ttsService.speak(event.phrase);
  }

  Future<String> _getPath() async {
    final dir = await getApplicationDocumentsDirectory();
    return '${dir.path}/recording.wav';
  }

  Future<void> _onFetchExamSentences(
    FetchExamSentences event, 
    Emitter<PronunciationSentencesState> emit
  ) async {
    try {
      emit(state.copyWith(isLoading: true));
      
      final uri = Uri.parse('$baseUrl/exam/start/${event.examId}');
      
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      
      if (token == null) {
        emit(state.copyWith(
          errorMessage: 'User token not found in SharedPreferences',
          isLoading: false
        ));
        return;
      }
      
      final response = await http.get(
        uri,
        headers: {'Authorization': 'Bearer $token'},
      );
      
      if (response.statusCode == 200) {
        final responseData = json.decode(utf8.decode(response.bodyBytes));
        print("$responseData");
        final examId = responseData['id_ujianfonem'];
        if (responseData.containsKey('error')) {
          emit(state.copyWith(
            errorMessage: responseData['error'],
            isLoading: false
          ));
          return;
        }
        
        final List<dynamic> data = responseData['data'];
        
        if (data.isEmpty) {
          emit(state.copyWith(
            errorMessage: 'No sentences found for this exam',
            isLoading: false
          ));
          return;
        }
        
        final List<PronunciationSentence> sentences = [];
        
        for (var item in data) {
          try {
            final id = item['id'];
            final content = item['kalimat'] as String? ?? '';
            final phoneme = item['fonem'] as String? ?? '';
            final category = item['kategori'] as String? ?? '';
            
            print('📥Processing exam item: $item');
            
            if (content.isNotEmpty) {
              sentences.add(PronunciationSentence(
                id: id is int ? id : int.tryParse(id.toString()) ?? 0,
                content: content,
                phoneme: phoneme,
                category: category,
              ));
            }
          } catch (e) {
            print('❌ Error parsing exam item: $e, Item: $item');
          }
        }
        
        if (sentences.isEmpty) {
          emit(state.copyWith(
            errorMessage: 'Could not parse any valid sentences from the exam response',
            isLoading: false
          ));
          return;
        }
        
        emit(state.copyWith(
          sentences: sentences,
          currentIndex: 0,
          isLoading: false,
          errorMessage: '',
          examId: examId,
          justRestarted: false,
        ));
        
        print('📥 Fetched ${sentences.length} sentences for exam ${event.examId}');
      } else {
        emit(state.copyWith(
          errorMessage: 'Failed to fetch exam sentences: Status ${response.statusCode}',
          isLoading: false
        ));
      }
    } catch (e) {
      print('❌ Error fetching exam sentences: $e');
      emit(state.copyWith(
        errorMessage: 'Failed to fetch exam sentences: $e',
        isLoading: false
      ));
    }
  }

  void _onMoveToNextSentence(
    MoveToNextSentence event, 
    Emitter<PronunciationSentencesState> emit
  ) {
    final nextIndex = state.currentIndex + 1;
    
    if (nextIndex < state.sentences.length) {
      emit(state.copyWith(
        currentIndex: nextIndex,
        phonemeResults: const [],
        score: 0.0,
      ));
    } else {
      emit(state.copyWith(
        showSessionSummary: true,
        phonemeResults: const [],
        score: 0.0,
      ));
    }
  }
  
  void _onShowSessionSummary(
    ShowSessionSummary event,
    Emitter<PronunciationSentencesState> emit
  ) {
    emit(state.copyWith(showSessionSummary: true));
  }
  
  void _onCloseSessionSummary(
    CloseSessionSummary event,
    Emitter<PronunciationSentencesState> emit
  ) {
    emit(state.copyWith(showSessionSummary: false));
  }


  Future<void> _onRestartExam(
    RestartExam event,
    Emitter<PronunciationSentencesState> emit
  ) async {
    try {
      emit(state.copyWith(isRestarting: true));
      
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      
      if (token == null) {
        emit(state.copyWith(
          errorMessage: 'User token not found',
          isRestarting: false
        ));
        return;
      }
      final deleteUri = Uri.parse('$baseUrl/exam/delete/${state.examId}');
      final deleteResponse = await http.delete(
        deleteUri,
        headers: {'Authorization': 'Bearer $token'},
      );

      if (deleteResponse.statusCode != 200) {
        final errorData = json.decode(deleteResponse.body);
        emit(state.copyWith(
          errorMessage: 'Failed to reset exam: ${errorData['detail'] ?? 'Unknown error'}',
          isRestarting: false
        ));
        return;
      }

      print('🔄 Exam details deleted successfully');

      final startUri = Uri.parse('$baseUrl/exam/start/${event.examId}');
      final startResponse = await http.get(
        startUri,
        headers: {'Authorization': 'Bearer $token'},
      );

      if (startResponse.statusCode == 200) {
        final responseData = json.decode(utf8.decode(startResponse.bodyBytes));
        print("🔄 Restart response: $responseData");
        
        final examId = responseData['id_ujianfonem'];
        
        if (responseData.containsKey('error')) {
          emit(state.copyWith(
            errorMessage: responseData['error'],
            isRestarting: false
          ));
          return;
        }
        
        final List<dynamic> data = responseData['data'];
        
        if (data.isEmpty) {
          emit(state.copyWith(
            errorMessage: 'No sentences found for restarted exam',
            isRestarting: false
          ));
          return;
        }
        
        final List<PronunciationSentence> sentences = [];
        
        for (var item in data) {
          try {
            final id = item['id'];
            final content = item['kalimat'] as String? ?? '';
            final phoneme = item['fonem'] as String? ?? '';
            final category = item['kategori'] as String? ?? '';
            
            if (content.isNotEmpty) {
              sentences.add(PronunciationSentence(
                id: id is int ? id : int.tryParse(id.toString()) ?? 0,
                content: content,
                phoneme: phoneme,
                category: category,
              ));
            }
          } catch (e) {
            print('❌ Error parsing restart exam item: $e, Item: $item');
          }
        }
        
        if (sentences.isEmpty) {
          emit(state.copyWith(
            errorMessage: 'Could not parse any valid sentences from restarted exam',
            isRestarting: false
          ));
          return;
        }
        
        emit(state.copyWith(
          sentences: sentences,
          currentIndex: 0,
          phonemeResults: const [],
          score: 0.0,
          completedSentences: const [],
          showSessionSummary: false,
          isRestarting: false,
          errorMessage: '',
          examId: examId,
          justRestarted: true,
        ));
        
        print('🔄 Exam restarted successfully with ${sentences.length} sentences');
        
      } else {
        emit(state.copyWith(
          errorMessage: 'Failed to restart exam: Status ${startResponse.statusCode}',
          isRestarting: false
        ));
      }
      
    } catch (e) {
      print('❌ Error restarting exam: $e');
      emit(state.copyWith(
        errorMessage: 'Failed to restart exam: $e',
        isRestarting: false
      ));
    }
  }

  void _onClearRestartSuccess(
    ClearRestartSuccess event,
    Emitter<PronunciationSentencesState> emit
  ) {
    emit(state.copyWith(justRestarted: false));
  }
}