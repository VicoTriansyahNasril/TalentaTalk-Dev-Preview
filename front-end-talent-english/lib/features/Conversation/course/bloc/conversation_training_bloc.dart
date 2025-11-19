import 'package:flutter_bloc/flutter_bloc.dart';
import 'conversation_training_event.dart';
import 'conversation_training_state.dart';
import '../model/ptraining_model.dart';
import 'package:flutter/material.dart';

class ConversationTrainingBloc
    extends Bloc<ConversationTrainingEvent, ConversationTrainingState> {
  ConversationTrainingBloc() : super(TrainingLoading()) {
    on<LoadTraining>((event, emit) async {
      try {
        await Future.delayed(const Duration(seconds: 1)); // Simulasi loading

        final trainings = [
          ConversationTraining(
            title: 'Profesional Conversation',
            subtitle: 'Simulate professional dialogue with real-time feedback',
            icon: const Icon(Icons.chat_bubble_outline, color: Colors.white, size: 50),
            route: '/conversation_instruction',
          ),
          ConversationTraining(
            title: 'Interview Practice',
            subtitle: 'Prepare for job interviews with realistic questions',
            icon: const Icon(Icons.business_center, color: Colors.white, size: 50),
            route: '/interview_instruction',
          ),
        ];

        emit(TrainingLoaded(trainings));
      } catch (e) {
        emit(TrainingError('Failed to load training data'));
      }
    });
  }
}
