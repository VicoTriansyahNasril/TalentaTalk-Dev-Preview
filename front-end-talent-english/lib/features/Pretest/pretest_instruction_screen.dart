import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../widgets/instruction_screen.dart';
import 'pretest_pronunciation_screen.dart';


class PretestPronunciationInstructionScreen extends StatelessWidget {
  const PretestPronunciationInstructionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return InstructionScreen(
      title: "Pronunciation Pretest",
      subtitle: "Test your current pronunciation skills",
      headerIcon: Icons.record_voice_over,
      primaryColor: Colors.green,
      estimatedTime: "5-7 minutes",
      startButtonText: "Start Pretest",
      instructions: [
        const InstructionItem(
          title: "Listen to each sentence carefully",
          description: "Tap the speaker icon to hear the correct pronunciation of each sentence. You can replay it multiple times.",
          icon: Icons.volume_up,
        ),
        const InstructionItem(
          title: "Record your pronunciation",
          description: "Press the microphone button and speak the sentence clearly. Try to match the pronunciation you heard.",
          icon: Icons.mic,
        ),
        const InstructionItem(
          title: "Complete all sentences",
          description: "You'll need to pronounce 10 sentences. Take your time and do your best on each one.",
          icon: Icons.list_alt,
        ),
        const InstructionItem(
          title: "Find a quiet environment",
          description: "Make sure you're in a quiet place with minimal background noise for the best recording quality.",
          icon: Icons.volume_off,
          isImportant: true,
        ),
        const InstructionItem(
          title: "Speak clearly and naturally",
          description: "Don't rush. Speak at a normal pace and volume. The system will analyze your pronunciation accuracy.",
          icon: Icons.chat_bubble_outline,
          isImportant: true,
        ),
        const InstructionItem(
          title: "Review your results",
          description: "After completing all sentences, you'll see your overall score and detailed feedback.",
          icon: Icons.analytics,
        ),
      ],
      onStartPressed: () {
        context.go('/pretest'); 
      },
    );
  }
}