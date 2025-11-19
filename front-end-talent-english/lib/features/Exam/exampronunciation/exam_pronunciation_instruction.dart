import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../widgets/instruction_screen.dart';

class ExamPronunciationInstructionScreen extends StatelessWidget {
  final int examId;
  
  const ExamPronunciationInstructionScreen({
    super.key,
    required this.examId,
  });

  @override
  Widget build(BuildContext context) {
    return InstructionScreen(
      title: "Pronunciation Exam",
      subtitle: "Test your pronunciation skills with structured sentences",
      headerIcon: Icons.quiz,
      primaryColor: Colors.orange,
      estimatedTime: "10-15 minutes",
      startButtonText: "Start Exam",
      instructions: [
        InstructionItem(
          title: "Listen to Each Sentence",
          description: "Tap the speaker icon to hear the correct pronunciation of each sentence. You can listen multiple times.",
          icon: Icons.volume_up,
          isImportant: true,
        ),
        InstructionItem(
          title: "Record Your Pronunciation",
          description: "Tap the microphone button and speak the sentence clearly. Make sure you're in a quiet environment for best results.",
          icon: Icons.mic,
        ),
        InstructionItem(
          title: "Review Your Performance",
          description: "After recording, you'll see your pronunciation analysis with specific feedback on phonemes.",
          icon: Icons.analytics,
        ),
        InstructionItem(
          title: "Complete All Questions",
          description: "Work through all sentences in the exam. You can't go back to previous questions once you move forward.",
          icon: Icons.checklist,
          isImportant: true,
        ),
        InstructionItem(
          title: "Get Your Final Score",
          description: "After completing all questions, you'll receive a detailed score report with areas for improvement.",
          icon: Icons.score,
        ),
      ],
      onStartPressed: () {
        context.pushReplacementNamed(
          'pronunciation_exam',
          pathParameters: {
            'id': examId.toString(),
          },
        );
      },
    );
  }
}