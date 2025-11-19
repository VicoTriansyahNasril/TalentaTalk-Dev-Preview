import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'bloc/exam_pronunciation_bloc.dart';
import 'bloc/exam_pronunciation_event.dart';
import 'bloc/exam_pronunciation_state.dart';
import '../../../../services/tts_service.dart';
import '../../../../core/constants.dart';
import 'widgets/result_dialog.dart';

class ExamPronunciationScreen extends StatefulWidget {
  final int examId;
  const ExamPronunciationScreen({super.key, required this.examId});

  @override
  State<ExamPronunciationScreen> createState() => _ExamPronunciationScreenState();
}

class _ExamPronunciationScreenState extends State<ExamPronunciationScreen> {
  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => PronunciationSentencesBloc(
        baseUrl: '${Env.baseUrl}',
        ttsService: TtsService(),
      )..add(FetchExamSentences(widget.examId)),
      child: Scaffold(
        appBar: AppBar(
          title: const Text("Pronunciation Exam"),
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: const BackButton(color: Colors.blue),
          actions: [
            BlocBuilder<PronunciationSentencesBloc, PronunciationSentencesState>(
              buildWhen: (previous, current) => 
                previous.isRestarting != current.isRestarting ||
                previous.sentences != current.sentences,
              builder: (context, state) {
                if (state.sentences.isEmpty && !state.isLoading) {
                  return const SizedBox.shrink();
                }
                
                return Padding(
                  padding: const EdgeInsets.only(right: 8.0),
                  child: state.isRestarting
                    ? const Padding(
                        padding: EdgeInsets.all(12.0),
                        child: SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
                          ),
                        ),
                      )
                    : IconButton(
                        icon: const Icon(
                          Icons.refresh,
                          color: Colors.blue,
                          size: 24,
                        ),
                        onPressed: () => _showRestartConfirmation(context, widget.examId),
                        tooltip: 'Restart Exam',
                      ),
                );
              },
            ),
          ],
        ),
        body: Padding(
          padding: const EdgeInsets.all(16.0),
          child: BlocConsumer<PronunciationSentencesBloc, PronunciationSentencesState>(
            listener: (context, state) {
              if (state.errorMessage.isNotEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(state.errorMessage),
                    backgroundColor: Colors.red,
                  ),
                );
              }
              
              if (state.showSessionSummary) {
                Future.delayed(Duration.zero, () {
                  context.go('/exam_score/${state.examId}');
                  context.read<PronunciationSentencesBloc>().add(CloseSessionSummary());
                });
              }

              if (state.justRestarted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('🔄 Exam restarted successfully!'),
                    backgroundColor: Colors.green,
                    duration: Duration(seconds: 2),
                  ),
                );
                context.read<PronunciationSentencesBloc>().add(ClearRestartSuccess());
              }
            },
            builder: (context, state) {
              if (state.isLoading) {
                return const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircularProgressIndicator(),
                      SizedBox(height: 16),
                      Text(
                        "Loading exam sentences...",
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                );
              }

              if (state.isRestarting) {
                return const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircularProgressIndicator(),
                      SizedBox(height: 16),
                      Text(
                        "Restarting exam...",
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                );
              }
              
              if (state.sentences.isEmpty) {
                return Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.assignment_outlined,
                        size: 64,
                        color: Colors.grey,
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        "No sentences found for this exam",
                        style: TextStyle(fontSize: 18),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: () {
                          context.read<PronunciationSentencesBloc>()
                              .add(FetchExamSentences(widget.examId));
                        },
                        icon: const Icon(Icons.refresh),
                        label: const Text("Retry"),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ],
                  ),
                );
              }
              
              final currentIndex = state.currentIndex;
              final totalSentences = state.sentences.length;
              final currentSentence = state.currentSentence;
              
              if (currentSentence == null) {
                return const Center(child: Text("No active sentence"));
              }
              
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        "Question ${currentIndex + 1} of $totalSentences",
                        style: const TextStyle(
                          fontSize: 16,
                          color: Colors.grey,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.blue.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          "${state.completedSentences.length}/$totalSentences completed",
                          style: const TextStyle(
                            fontSize: 12,
                            color: Colors.blue,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  const Text(
                    "Exam Sentence:",
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),

                  Expanded(
                    child: SingleChildScrollView(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Card(
                            elevation: 4,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Container(
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(16),
                                gradient: const LinearGradient(
                                  begin: Alignment.topLeft,
                                  end: Alignment.bottomRight,
                                  colors: [
                                    Color(0xFF2196F3),
                                    Color(0xFF1976D2),
                                  ],
                                ),
                              ),
                              child: Padding(
                                padding: const EdgeInsets.all(20.0),
                                child: Row(
                                  children: [
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            currentSentence.content,
                                            style: const TextStyle(
                                              color: Colors.white,
                                              fontSize: 24,
                                              fontWeight: FontWeight.bold,
                                              height: 1.3,
                                            ),
                                          ),
                                          if (currentSentence.phoneme.isNotEmpty) ...[
                                            const SizedBox(height: 12),
                                            Container(
                                              padding: const EdgeInsets.symmetric(
                                                horizontal: 12,
                                                vertical: 6,
                                              ),
                                              decoration: BoxDecoration(
                                                color: Colors.white.withOpacity(0.2),
                                                borderRadius: BorderRadius.circular(20),
                                              ),
                                              child: Text(
                                                currentSentence.phoneme,
                                                style: const TextStyle(
                                                  color: Colors.white,
                                                  fontSize: 16,
                                                  fontFamily: 'monospace',
                                                ),
                                              ),
                                            ),
                                          ],
                                        ],
                                      ),
                                    ),
                                    Container(
                                      decoration: BoxDecoration(
                                        color: Colors.white.withOpacity(0.2),
                                        borderRadius: BorderRadius.circular(50),
                                      ),
                                      child: IconButton(
                                        icon: const Icon(
                                          Icons.volume_up,
                                          color: Colors.white,
                                          size: 28,
                                        ),
                                        onPressed: state.isRecording || state.isSubmitting ? null : () {
                                          context.read<PronunciationSentencesBloc>().add(
                                            PlayTts(currentSentence.content)
                                          );
                                        },
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),

                          const SizedBox(height: 24),

                          Row(
                            children: [
                              Icon(
                                Icons.lightbulb_outline,
                                color: Colors.amber[700],
                                size: 20,
                              ),
                              const SizedBox(width: 8),
                              const Text(
                                "Exam Instructions",
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.grey,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),

                          Card(
                            elevation: 2,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Container(
                                        padding: const EdgeInsets.all(6),
                                        decoration: BoxDecoration(
                                          color: Colors.orange[50],
                                          borderRadius: BorderRadius.circular(8),
                                        ),
                                        child: Icon(
                                          Icons.assignment,
                                          color: Colors.orange[600],
                                          size: 16,
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      const Text(
                                        "Exam Mode",
                                        style: TextStyle(
                                          fontSize: 14,
                                          fontWeight: FontWeight.bold,
                                          color: Colors.grey,
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  const Text(
                                    "• Listen carefully to the sentence\n• Speak clearly and confidently\n• One attempt per question\n• You cannot go back once submitted",
                                    style: TextStyle(
                                      fontSize: 14,
                                      color: Colors.black87,
                                      height: 1.4,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),

                          const SizedBox(height: 24),

                          Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(20),
                            decoration: BoxDecoration(
                              color: Colors.grey[50],
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(
                                color: Colors.grey[200]!,
                                width: 1,
                              ),
                            ),
                            child: Column(
                              children: [
                                Icon(
                                  state.isRecording ? Icons.mic : Icons.mic_outlined,
                                  size: 32,
                                  color: state.isRecording ? Colors.red : 
                                         state.isSubmitting ? Colors.orange : Colors.blue,
                                ),
                                const SizedBox(height: 12),
                                Text(
                                  state.isRecording 
                                    ? "Recording... Speak now!" 
                                    : state.isSubmitting
                                      ? "Processing your recording..."
                                      : "Tap the microphone to start recording",
                                  style: TextStyle(
                                    fontSize: 16,
                                    color: Colors.grey[700],
                                    fontWeight: FontWeight.w500,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                                const SizedBox(height: 16),
                                _buildActionButton(context, state),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }

  void _showRestartConfirmation(BuildContext context, int examId) {
    showDialog(
      context: context,
      builder: (BuildContext dialogContext) {
        return AlertDialog(
          title: const Row(
            children: [
              Icon(Icons.refresh, color: Colors.orange),
              SizedBox(width: 8),
              Text('Restart Exam'),
            ],
          ),
          content: const Text(
            'Are you sure you want to restart this exam?\n\n'
            'This will:\n'
            '• Delete all your current progress\n'
            '• Reset all answered questions\n'
            '• Start the exam from the beginning',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(dialogContext).pop();
                context.read<PronunciationSentencesBloc>().add(RestartExam(examId));
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.orange,
                foregroundColor: Colors.white,
              ),
              child: const Text('Restart'),
            ),
          ],
        );
      },
    );
  }

  Widget _buildActionButton(BuildContext context, PronunciationSentencesState state) {
    if (state.isRecording) {
      return FloatingActionButton.large(
        backgroundColor: Colors.red,
        elevation: 4,
        child: const Icon(Icons.stop, size: 32, color: Colors.white),
        onPressed: () {
          context.read<PronunciationSentencesBloc>().add(StopRecording());
        },
      );
    }
    
    if (state.isSubmitting) {
      return const CircularProgressIndicator();
    }
    
    if (state.phonemeResults.isNotEmpty) {
      return ElevatedButton.icon(
        icon: const Icon(Icons.arrow_forward),
        label: const Text("Next"),
        onPressed: () {
          context.read<PronunciationSentencesBloc>().add(MoveToNextSentence());
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.blue,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      );
    }
    
    return FloatingActionButton.large(
      backgroundColor: Colors.blue,
      elevation: 4,
      child: const Icon(Icons.mic, size: 32, color: Colors.white),
      onPressed: () {
        context.read<PronunciationSentencesBloc>().add(StartRecording());
      },
    );
  }
}