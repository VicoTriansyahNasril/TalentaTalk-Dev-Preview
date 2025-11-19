import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../widgets/instruction_screen.dart';


class PronunciationWordsInstructionScreen extends StatelessWidget {
  final int materialId;

  const PronunciationWordsInstructionScreen({
    super.key,
    required this.materialId,
  });

  @override
  Widget build(BuildContext context) {
    return InstructionScreen(
      title: "Word Pronunciation Practice",
      subtitle: "Learn to pronounce words correctly with phoneme focus",
      headerIcon: Icons.record_voice_over,
      primaryColor: Colors.green,
      estimatedTime: "10-15 minutes",
      startButtonText: "Start Word Practice",
      instructions: [
        InstructionItem(
          title: "Listen to the Reference Audio",
          description: "Each word will be played with correct pronunciation. Listen carefully to understand the phoneme sounds.",
          icon: Icons.headphones,
          isImportant: true,
        ),
        InstructionItem(
          title: "Record Your Pronunciation",
          description: "Tap the record button and pronounce the word clearly. Speak at normal speed and volume.",
          icon: Icons.mic,
        ),
        InstructionItem(
          title: "Review Your Performance",
          description: "Listen to your recording and compare it with the reference audio. Notice the differences in pronunciation.",
          icon: Icons.compare_arrows,
        ),
        InstructionItem(
          title: "Focus on Phoneme Accuracy",
          description: "Pay special attention to the target phoneme in each word. This will help improve your overall pronunciation.",
          icon: Icons.tablet,
          isImportant: true,
        ),
        InstructionItem(
          title: "Practice Multiple Times",
          description: "You can re-record as many times as needed. Repetition helps build muscle memory for correct pronunciation.",
          icon: Icons.repeat,
        ),
      ],
      onStartPressed: () {
        context.pushReplacementNamed(
          'pronunciation_words',
          pathParameters: {
            'id': materialId.toString(),
          },
        );
      },
    );
  }
}