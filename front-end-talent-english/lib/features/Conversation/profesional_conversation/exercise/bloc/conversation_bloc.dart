// conversation_bloc.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import 'dart:io';
import '../model/chat_message.dart';
import '../repository/conversation_repository.dart';
import 'conversation_event.dart';
import 'conversation_state.dart';

class ConversationBloc extends Bloc<ConversationEvent, ConversationState> {
  final ConversationRepository repository;
  final List<ChatMessage> _messages = [];

  ConversationBloc(this.repository) : super(ConversationInitial()) {
    on<StartConversationEvent>((event, emit) async {
      emit(ConversationLoading());
      try {
        final topic = await repository.startConversation();
        _messages.clear();
        _messages.add(ChatMessage(message: topic, isUser: false));
        emit(ConversationInProgress(List.from(_messages)));
      } catch (e) {
        emit(ConversationError(e.toString()));
      }
    });

    on<SendUserMessageEvent>((event, emit) async {
      _messages.add(ChatMessage(message: event.message, isUser: true));
      emit(ConversationInProgress(List.from(_messages)));
      try {
        final reply = await repository.sendMessage(event.message, event.duration);
        _messages.add(ChatMessage(message: reply, isUser: false));
        emit(ConversationInProgress(List.from(_messages)));
      } catch (e) {
        emit(ConversationError(e.toString()));
      }
    });

    on<SendAudioMessageEvent>((event, emit) async {
      try {
        print('Processing audio message: ${event.audioPath}');
        
        final audioFile = File(event.audioPath);
        
        if (!audioFile.existsSync()) {
          throw Exception('Audio file not found: ${event.audioPath}');
        }

        final fileSize = await audioFile.length();
        if (fileSize == 0) {
          throw Exception('Audio file is empty');
        }

        print('Audio file verified. Size: $fileSize bytes');

        final transcribedText = await repository.transcribeAudio(event.audioPath);
        
        if (transcribedText.trim().isEmpty) {
          throw Exception('Transcription returned empty text');
        }

        print('Transcription successful: $transcribedText'); 
        
        _messages.add(ChatMessage(message: transcribedText, isUser: true));
        emit(ConversationInProgress(List.from(_messages)));
        
        final reply = await repository.sendMessage(transcribedText, event.duration);
        _messages.add(ChatMessage(message: reply, isUser: false));
        emit(ConversationInProgress(List.from(_messages)));

        print('Conversation exchange completed successfully');
        print('Recording file kept at: ${event.audioPath}');

      } catch (e) {
        print('Error in SendAudioMessageEvent: $e');
        
        _messages.add(ChatMessage(
          message: '[Audio processing failed: ${e.toString()}]', 
          isUser: true
        ));
        emit(ConversationInProgress(List.from(_messages)));
        
        emit(ConversationError('Failed to process audio: ${e.toString()}'));
        
        await Future.delayed(const Duration(seconds: 2));
        emit(ConversationInProgress(List.from(_messages)));
      }
      
    });

    on<FinishConversationEvent>((event, emit) async {
      emit(ConversationLoading());
      try {
        final reportData = await repository.fetchReport();
        emit(ConversationFinished(
          report: reportData['report'],
          saveStatus: reportData['saveStatus'],
          talentId: reportData['talentId'],
        ));
      } catch (e) {
        emit(ConversationError(e.toString()));
      }
    });
  }
}