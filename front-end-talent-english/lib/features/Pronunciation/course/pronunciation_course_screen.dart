import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'bloc/pronunciation_training_bloc.dart';
import 'bloc/pronunciation_training_event.dart';
import 'bloc/pronunciation_training_state.dart';
import '../../widgets/couse_card.dart';

class PronunciationCourseScreen extends StatelessWidget {
  const PronunciationCourseScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => PronunciationTrainingBloc()..add(LoadTraining()),
      child: Scaffold(
        body: Padding(
          padding: const EdgeInsets.all(16.0),
          child: BlocBuilder<PronunciationTrainingBloc, PronunciationTrainingState>(
            builder: (context, state) {
              if (state is TrainingLoading) {
                return const Center(child: CircularProgressIndicator());
              } else if (state is TrainingLoaded) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Improve Your Pronunciation",
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      "Select a training module to begin",
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey[600],
                      ),
                    ),
                    const SizedBox(height: 24),
                    Expanded(
                      child: ListView.builder(
                        itemCount: state.trainings.length,
                        itemBuilder: (context, index) {
                          final training = state.trainings[index];
                          return UnifiedTrainingCard(
                            title: training.title,
                            subtitle: training.subtitle,
                            icon: training.icon,
                            color: training.color,
                            onTap: () {
                              context.push(training.route);
                            },
                          );
                        },
                      ),
                    ),
                  ],
                );
              } else if (state is TrainingError) {
                return Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.error_outline, size: 48, color: Colors.red),
                      const SizedBox(height: 16),
                      Text(state.message),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () {
                          context.read<PronunciationTrainingBloc>().add(LoadTraining());
                        },
                        child: const Text('Try Again'),
                      ),
                    ],
                  ),
                );
              } else {
                return const SizedBox();
              }
            },
          ),
        ),
      ),
    );
  }
}