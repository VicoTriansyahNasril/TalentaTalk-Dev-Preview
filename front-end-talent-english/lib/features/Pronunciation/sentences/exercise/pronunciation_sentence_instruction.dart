import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../widgets/instruction_screen.dart';

class PronunciationSentencesInstructionScreen extends StatelessWidget {
  final int materialId;
  
  const PronunciationSentencesInstructionScreen({
    super.key,
    required this.materialId,
  });

  @override
  Widget build(BuildContext context) {
    return InstructionScreen(
      title: "Pronunciation Sentences",
      subtitle: "Practice speaking complete sentences with correct pronunciation",
      headerIcon: Icons.record_voice_over,
      primaryColor: Colors.blue,
      estimatedTime: "1 Minute",
      startButtonText: "Start Practice",
      instructions: const [
        InstructionItem(
          title: "Read the sentence carefully",
          description: "Take time to understand the sentence structure and pronunciation guide (IPA) provided.",
          icon: Icons.visibility,
        ),
        InstructionItem(
          title: "Listen to the audio",
          description: "Tap the speaker icon to hear the correct pronunciation of the sentence.",
          icon: Icons.volume_up,
        ),
        InstructionItem(
          title: "Practice silently first",
          description: "Mouth the words without speaking to get familiar with the pronunciation.",
          icon: Icons.hearing,
        ),
        InstructionItem(
          title: "Record your pronunciation",
          description: "Tap the microphone button and speak the sentence clearly at normal speed.",
          icon: Icons.mic,
          isImportant: true,
        ),
        InstructionItem(
          title: "Review your results",
          description: "Check your pronunciation accuracy and phoneme comparison to improve.",
          icon: Icons.analytics,
        ),
        InstructionItem(
          title: "Repeat if needed",
          description: "Practice multiple times until you achieve satisfactory pronunciation accuracy.",
          icon: Icons.refresh,
        ),
      ],
      onStartPressed: () {
        context.pushReplacementNamed(
          'pronunciation_sentence',
          pathParameters: {'id': materialId.toString()},
        );
      },
    );
  }
}