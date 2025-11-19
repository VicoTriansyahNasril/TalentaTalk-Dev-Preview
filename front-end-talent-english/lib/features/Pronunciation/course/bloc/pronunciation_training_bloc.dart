import 'package:flutter_bloc/flutter_bloc.dart';
import 'pronunciation_training_event.dart';
import 'pronunciation_training_state.dart';
import '../model/ptraining_model.dart';
import 'package:flutter/material.dart';

class PronunciationTrainingBloc
    extends Bloc<PronunciationTrainingEvent, PronunciationTrainingState> {
  PronunciationTrainingBloc() : super(TrainingLoading()) {
    on<LoadTraining>((event, emit) async {
      try {
        await Future.delayed(const Duration(seconds: 1));

        final trainings = [
          PronunciationTraining(
            title: 'Basic Phoneme Training',
            subtitle: 'Learn individual sounds clearly',
            icon: const Icon(Icons.hearing, color: Colors.white, size: 32),
            route: '/phoneme-category',
            color: const Color.fromARGB(255, 0, 132, 255),
            
          ),
          PronunciationTraining(
            title: 'Contrastive Sentence Practice',
            subtitle: 'Practice sounds in context',
            icon: const Icon(Icons.record_voice_over, color: Colors.white, size: 32),
            route: '/contrastive-phoneme',
            color: const Color(0xFF40C057),
          
          ),
          PronunciationTraining(
            title: 'Pronunciation Exam Test',
            subtitle: 'Test your pronunciation skills',
            icon: const Icon(Icons.psychology, color: Colors.white, size: 32),
            route: '/exam-phoneme',
            color: const Color.fromARGB(255, 255, 166, 0),
           
          ),
        ];

        emit(TrainingLoaded(trainings));
      } catch (e) {
        emit(TrainingError('Failed to load training data'));
      }
    });
  }
}