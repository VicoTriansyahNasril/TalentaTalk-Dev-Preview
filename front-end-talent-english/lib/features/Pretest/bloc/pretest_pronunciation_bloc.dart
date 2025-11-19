import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'pretest_pronunciation_event.dart';
import 'pretest_pronunciation_state.dart';
import '../../../../../services/tts_service.dart';

class PracticePronunciationBloc extends Bloc<PracticePronunciationEvent, PracticePronunciationState> {
  final TtsService ttsService;
  final String baseUrl;

  final AudioRecorder _recorder = AudioRecorder();
  Timer? _timer;
  String? _recordedPath;

  PracticePronunciationBloc({required this.ttsService, required this.baseUrl})
      : super(const PracticePronunciationState()) {
    on<StartRecording>(_onStartRecording);
    on<StopRecording>(_onStopRecording);
    on<PlayTts>(_onPlayTts);
    on<FetchPracticeSentences>(_onFetchPracticeSentences);
    on<MoveToNextSentence>(_onMoveToNextSentence);
    on<ClosePracticeResult>(_onClosePracticeResult);
    on<SubmitPracticeScore>(_onSubmitPracticeScore);
    on<CloseFinalSummary>(_onCloseFinalSummary);
  }

  Future<void> _onStartRecording(
    StartRecording event, 
    Emitter<PracticePronunciationState> emit
  ) async {
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
    Emitter<PracticePronunciationState> emit,
  ) async {
    _timer?.cancel();
    final path = await _recorder.stop();
    emit(state.copyWith(isRecording: false, isSubmitting: true));
    
    if (path == null || state.currentSentence == null) return;

    try {
      print('🎙️ Sending recording for practice evaluation');
      print('🎙️ Sentence ID: ${state.currentSentence!.id}');
      
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      if (token == null) {
        emit(state.copyWith(
          errorMessage: 'User token not found',
          isSubmitting: false,
        ));
        return;
      }
      
      final uri = Uri.parse('$baseUrl/pretest/compare');
      final request = http.MultipartRequest('POST', uri)
        ..fields['idContent'] = state.currentSentence!.id.toString()
        ..files.add(await http.MultipartFile.fromPath('file', path))
        ..headers['Authorization'] = 'Bearer $token';

      final response = await request.send();
      final body = await response.stream.bytesToString();
      print('📥 Response from /compare: $body');

      if (response.statusCode == 200) {
        final data = json.decode(body);

        final similarityPercentStr = data['similarity_percent'] as String;
        print('🔍 Raw similarity percent: $similarityPercentStr');
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
          showPracticeResult: false,
        ));
      } else {
        emit(state.copyWith(
          errorMessage: '❌ Server error: ${response.statusCode}', 
          isSubmitting: false,
        ));
      }
    } catch (e) {
      emit(state.copyWith(
        errorMessage: '❌ Failed to evaluate recording: $e', 
        isSubmitting: false,
      ));
    }
  }

  Future<void> _onPlayTts(
    PlayTts event, 
    Emitter<PracticePronunciationState> emit
  ) async {
    await ttsService.speak(event.phrase);
  }

  Future<String> _getPath() async {
    final dir = await getApplicationDocumentsDirectory();
    return '${dir.path}/recording.wav';
  }

  Future<void> _onFetchPracticeSentences(
    FetchPracticeSentences event, 
    Emitter<PracticePronunciationState> emit
  ) async {
    try {
      emit(state.copyWith(isLoading: true));
      
      final uri = Uri.parse('$baseUrl/pretest/start');
      
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
        print("Practice response: $responseData");
        
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
            errorMessage: 'No sentences found for practice',
            isLoading: false
          ));
          return;
        }
        
        final List<PronunciationSentence> sentences = [];
        
        final practiceData = data.take(10).toList();
        
        for (var item in practiceData) {
          try {
            final id = item['id'];
            final content = item['kalimat'] as String? ?? '';
            final phoneme = item['fonem'] as String? ?? '';
            final category = item['kategori'] as String? ?? '';
            
            print('📥 Processing practice item: $item');
            
            if (content.isNotEmpty) {
              sentences.add(PronunciationSentence(
                id: id is int ? id : int.tryParse(id.toString()) ?? 0,
                content: content,
                phoneme: phoneme,
                category: category,
              ));
            }
          } catch (e) {
            print('❌ Error parsing practice item: $e, Item: $item');
          }
        }
        
        if (sentences.isEmpty) {
          emit(state.copyWith(
            errorMessage: 'Could not parse any valid sentences for practice',
            isLoading: false
          ));
          return;
        }
        
        emit(state.copyWith(
          sentences: sentences,
          currentIndex: 0,
          isLoading: false,
          errorMessage: '',
        ));
        
        print('📥 Fetched ${sentences.length} sentences for practice');
      } else {
        emit(state.copyWith(
          errorMessage: 'Failed to fetch practice sentences: Status ${response.statusCode}',
          isLoading: false
        ));
      }
    } catch (e) {
      print('❌ Error fetching practice sentences: $e');
      emit(state.copyWith(
        errorMessage: 'Failed to fetch practice sentences: $e',
        isLoading: false
      ));
    }
  }

  void _onMoveToNextSentence(
    MoveToNextSentence event, 
    Emitter<PracticePronunciationState> emit
  ) {
    final nextIndex = state.currentIndex + 1;
    
    emit(state.copyWith(showPracticeResult: false));
    
    if (nextIndex < state.sentences.length) {
      emit(state.copyWith(
        currentIndex: nextIndex,
        phonemeResults: const [],
        score: 0.0,
      ));
    } else {
      final totalScore = state.completedSentences
          .map((e) => e.score)
          .reduce((a, b) => a + b);
      final averageScore = totalScore / state.completedSentences.length;
      
      emit(state.copyWith(
        shouldNavigateToSummary: true,
        averageScore: averageScore,
        phonemeResults: const [],
        score: 0.0,
        showFinalSummary: false,
      ));
      
      add(SubmitPracticeScore());
    }
  }
  
  void _onClosePracticeResult(
    ClosePracticeResult event,
    Emitter<PracticePronunciationState> emit
  ) {
    emit(state.copyWith(showPracticeResult: false));
  }
  
  Future<void> _onSubmitPracticeScore(
    SubmitPracticeScore event,
    Emitter<PracticePronunciationState> emit
  ) async {
    try {
      emit(state.copyWith(isSubmittingScore: true));
      
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');
      final scorePercent = (state.averageScore * 100).toStringAsFixed(2);
      print('📤 Submitting pretest score: $scorePercent%');
      
      if (token == null) {
        emit(state.copyWith(
          errorMessage: 'User token not found',
          isSubmittingScore: false,
        ));
        return;
      }
      
      final uri = Uri.parse('$baseUrl/pretest/submit');
      final response = await http.post(
        uri,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'score': double.parse(scorePercent),
        }),
      );
      print('📤 Submitting pretest score: ${state.averageScore}');
      
      if (response.statusCode == 200) {
        print('✅ Practice score submitted successfully');
        emit(state.copyWith(isSubmittingScore: false));
      } else {
        print('❌ Failed to submit practice score: ${response.statusCode}');
        emit(state.copyWith(
          errorMessage: 'Failed to submit score',
          isSubmittingScore: false,
        ));
      }
    } catch (e) {
      print('❌ Error submitting practice score: $e');
      emit(state.copyWith(
        errorMessage: 'Failed to submit score: $e',
        isSubmittingScore: false,
      ));
    }
  }
  
  void _onCloseFinalSummary(
    CloseFinalSummary event,
    Emitter<PracticePronunciationState> emit
  ) {
    emit(state.copyWith(
      showFinalSummary: false,
      shouldNavigateToSummary: false,
    ));
  }

  @override
  Future<void> close() {
    _timer?.cancel();
    _recorder.dispose();
    return super.close();
  }
}