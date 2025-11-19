import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'bloc/pretest_pronunciation_bloc.dart';
import 'bloc/pretest_pronunciation_event.dart';
import 'bloc/pretest_pronunciation_state.dart';
import '../../../../services/tts_service.dart';
import '../../../../core/constants.dart';
import 'pretest_summary_screen.dart';

class PracticePronunciationScreen extends StatefulWidget {
  const PracticePronunciationScreen({super.key});

  @override
  State<PracticePronunciationScreen> createState() => _PracticePronunciationScreenState();
}

class _PracticePronunciationScreenState extends State<PracticePronunciationScreen> {
  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => PracticePronunciationBloc(
        baseUrl: '${Env.baseUrl}',
        ttsService: TtsService(),
      )..add(FetchPracticeSentences()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text("Pronunciation Pretest"),
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: const BackButton(color: Colors.blue),
        ),
        body: Padding(
          padding: const EdgeInsets.all(16.0),
          child: BlocConsumer<PracticePronunciationBloc, PracticePronunciationState>(
            listener: (context, state) {
              if (state.errorMessage.isNotEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(state.errorMessage)),
                );
              }
              
              if (state.shouldNavigateToSummary) {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => PracticeSummaryScreen(
                      averageScore: state.averageScore,
                      completedSentences: state.completedSentences,
                    ),
                  ),
                ).then((_) {
                  context.read<PracticePronunciationBloc>().add(CloseFinalSummary());
                  context.go('/home');
                });
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
                        "Loading practice sentences...",
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
                        "No sentences found for practice",
                        style: TextStyle(fontSize: 18),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: () {
                          context.read<PracticePronunciationBloc>()
                              .add(FetchPracticeSentences());
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
                        "Sentence ${currentIndex + 1} of $totalSentences",
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
                          "${((currentIndex / totalSentences) * 100).toStringAsFixed(0)}% complete",
                          style: const TextStyle(
                            fontSize: 12,
                            color: Colors.blue,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  LinearProgressIndicator(
                    value: currentIndex / totalSentences,
                    backgroundColor: Colors.grey[300],
                    valueColor: const AlwaysStoppedAnimation<Color>(Colors.blue),
                  ),
                  const SizedBox(height: 24),

                  const Text(
                    "Pretest Sentence:",
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
                                    Color(0xFF4CAF50),
                                    Color(0xFF388E3C),
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
                                          context.read<PracticePronunciationBloc>().add(
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
                                "Pretest Tips",
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
                                          color: Colors.green[50],
                                          borderRadius: BorderRadius.circular(8),
                                        ),
                                        child: Icon(
                                          Icons.tips_and_updates,
                                          color: Colors.green[600],
                                          size: 16,
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      const Text(
                                        "Practice Mode",
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
                                    "• Take your time to practice\n• Listen carefully before speaking\n• Focus on clear pronunciation\n• You can retry if needed",
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
                                         state.isSubmitting ? Colors.orange :
                                         _hasRecorded(state) ? Colors.green : Colors.blue,
                                ),
                                const SizedBox(height: 12),
                                Text(
                                  state.isRecording 
                                    ? "Recording... Speak now!" 
                                    : state.isSubmitting
                                      ? "Processing your recording..."
                                      : _hasRecorded(state)
                                        ? "Ready for next sentence"
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

  bool _hasRecorded(PracticePronunciationState state) {
    return state.completedSentences.length > state.currentIndex;
  }

  Widget _buildActionButton(BuildContext context, PracticePronunciationState state) {
    if (state.isRecording) {
      return FloatingActionButton.large(
        backgroundColor: Colors.red,
        elevation: 4,
        child: const Icon(Icons.stop, size: 32, color: Colors.white),
        onPressed: () {
          context.read<PracticePronunciationBloc>().add(StopRecording());
        },
      );
    }
    
    if (state.isSubmitting) {
      return const CircularProgressIndicator();
    }
    
    if (state.completedSentences.length > state.currentIndex) {
      return ElevatedButton.icon(
        onPressed: () {
          context.read<PracticePronunciationBloc>().add(MoveToNextSentence());
        },
        icon: const Icon(Icons.arrow_forward),
        label: const Text("Next"),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.green,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      );
    }
    
    return FloatingActionButton.large(
      backgroundColor: Colors.green,
      elevation: 4,
      child: const Icon(Icons.mic, size: 32, color: Colors.white),
      onPressed: () {
        context.read<PracticePronunciationBloc>().add(StartRecording());
      },
    );
  }
}