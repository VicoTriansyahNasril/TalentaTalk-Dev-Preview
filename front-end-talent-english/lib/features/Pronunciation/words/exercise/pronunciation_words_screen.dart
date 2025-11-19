import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../sentences/exercise/widgets/pronunciation_result_dialog.dart';
import 'bloc/pronunciation_words_bloc.dart';
import 'bloc/pronunciation_words_event.dart';
import 'bloc/pronunciation_words_state.dart';
import '../../../../services/tts_service.dart';
import '../../../../core/constants.dart';

class PronunciationWordsScreen extends StatefulWidget {
  final int idMaterial;
  const PronunciationWordsScreen({super.key, required this.idMaterial});

  @override
  State<PronunciationWordsScreen> createState() => _PronunciationWordsScreenState();
}

class _PronunciationWordsScreenState extends State<PronunciationWordsScreen> {
  bool _resultDialogShown = false;

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => PronunciationWordsBloc(
        baseUrl: '${Env.baseUrl}',
        ttsService: TtsService(),
      )..add(FetchWordById(widget.idMaterial)),
      child: Scaffold(
        appBar: AppBar(
          title: const Text("Pronunciation Practice"),
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: const BackButton(color: Colors.blue),
        ),
        body: Padding(
          padding: const EdgeInsets.all(16.0),
          child: BlocConsumer<PronunciationWordsBloc, PronunciationWordsState>(
            listener: (context, state) {
              if (state.errorMessage.isNotEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(state.errorMessage)),
                );
              }

              if (state.recordingCompleted && !_resultDialogShown) {
                _resultDialogShown = true;

                Future.delayed(Duration.zero, () {
                  showDialog(
                    context: context,
                    builder: (context) => PronunciationResultDialog(
                      accuracyPercent: state.score * 100,
                      phonemeComparison: state.phonemeComparison,
                      targetPhrase: state.phrase,
                    ),
                    barrierDismissible: false,
                  ).then((_) {
                    _resultDialogShown = false;
                    
                    context.read<PronunciationWordsBloc>().add(ResetRecordingCompleted());
                  });
                });
              }
            },
            builder: (context, state) {
              final phrase = state.phrase;
              final ipa = state.ipa;
              final meaning = state.meaning;
              final definition = state.definition;
              final error = state.errorMessage;

              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Practice Word:",
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),

                  if (error.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 20),
                      child: Center(
                        child: Text(
                          error,
                          style: const TextStyle(color: Colors.red, fontSize: 16),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    )

                  else if (phrase.isNotEmpty)
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
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        children: [
                                          Expanded(
                                            child: Column(
                                              crossAxisAlignment: CrossAxisAlignment.start,
                                              children: [
                                                Text(
                                                  phrase,
                                                  style: const TextStyle(
                                                    color: Colors.white,
                                                    fontSize: 28,
                                                    fontWeight: FontWeight.bold,
                                                  ),
                                                ),
                                                const SizedBox(height: 8),
                                                Container(
                                                  padding: const EdgeInsets.symmetric(
                                                    horizontal: 12,
                                                    vertical: 4,
                                                  ),
                                                  decoration: BoxDecoration(
                                                    color: Colors.white.withOpacity(0.2),
                                                    borderRadius: BorderRadius.circular(20),
                                                  ),
                                                  child: Text(
                                                    ipa,
                                                    style: const TextStyle(
                                                      color: Colors.white,
                                                      fontSize: 16,
                                                      fontFamily: 'monospace',
                                                    ),
                                                  ),
                                                ),
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
                                              onPressed: () {
                                                context
                                                    .read<PronunciationWordsBloc>()
                                                    .add(PlayTts(phrase));
                                              },
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),

                            const SizedBox(height: 16),

                            if (meaning.isNotEmpty || definition.isNotEmpty) ...[
                              Row(
                                children: [
                                  Icon(
                                    Icons.lightbulb_outline,
                                    color: Colors.amber[700],
                                    size: 20,
                                  ),
                                  const SizedBox(width: 8),
                                  const Text(
                                    "Word Information",
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.grey,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),

                              if (meaning.isNotEmpty)
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
                                                Icons.translate,
                                                color: Colors.green[600],
                                                size: 16,
                                              ),
                                            ),
                                            const SizedBox(width: 8),
                                            const Text(
                                              "Meaning",
                                              style: TextStyle(
                                                fontSize: 14,
                                                fontWeight: FontWeight.bold,
                                                color: Colors.grey,
                                              ),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 8),
                                        Text(
                                          meaning,
                                          style: const TextStyle(
                                            fontSize: 16,
                                            color: Colors.black87,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),

                              if (definition.isNotEmpty)
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
                                                color: Colors.purple[50],
                                                borderRadius: BorderRadius.circular(8),
                                              ),
                                              child: Icon(
                                                Icons.description_outlined,
                                                color: Colors.purple[600],
                                                size: 16,
                                              ),
                                            ),
                                            const SizedBox(width: 8),
                                            const Text(
                                              "Definition",
                                              style: TextStyle(
                                                fontSize: 14,
                                                fontWeight: FontWeight.bold,
                                                color: Colors.grey,
                                              ),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 8),
                                        Text(
                                          definition,
                                          style: const TextStyle(
                                            fontSize: 16,
                                            color: Colors.black87,
                                            height: 1.4,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),

                              const SizedBox(height: 24),
                            ],

                            if (phrase.isNotEmpty && error.isEmpty)
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
                                      color: state.isRecording ? Colors.red : Colors.blue,
                                    ),
                                    const SizedBox(height: 12),
                                    Text(
                                      state.isRecording
                                          ? "Recording... Speak now!"
                                          : "Tap the microphone to start recording",
                                      style: TextStyle(
                                        fontSize: 16,
                                        color: Colors.grey[700],
                                        fontWeight: FontWeight.w500,
                                      ),
                                      textAlign: TextAlign.center,
                                    ),
                                    const SizedBox(height: 16),
                                    FloatingActionButton.large(
                                      backgroundColor: state.isRecording ? Colors.red : Colors.blue,
                                      elevation: 4,
                                      child: Icon(
                                        state.isRecording ? Icons.stop : Icons.mic,
                                        size: 32,
                                        color: Colors.white,
                                      ),
                                      onPressed: () {
                                        final bloc = context.read<PronunciationWordsBloc>();
                                        bloc.add(state.isRecording
                                            ? StopRecording()
                                            : StartRecording());
                                      },
                                    ),
                                  ],
                                ),
                              ),
                          ],
                        ),
                      ),
                    )

                  else
                    const Expanded(
                      child: Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            CircularProgressIndicator(),
                            SizedBox(height: 16),
                            Text(
                              "Loading word...",
                              style: TextStyle(
                                fontSize: 16,
                                color: Colors.grey,
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
}