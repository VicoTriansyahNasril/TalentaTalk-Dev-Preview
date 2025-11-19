// lib/features/Conversation/interview/interview_instruction_screen.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../widgets/instruction_screen.dart';

class InterviewInstructionScreen extends StatelessWidget {
  const InterviewInstructionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return InstructionScreen(
      title: "Job Interview Practice",
      subtitle: "Practice your interview skills with AI-powered conversation",
      estimatedTime: "10-15 minutes",
      primaryColor: Colors.blue,
      headerIcon: Icons.work_outline,
      startButtonText: "Start Interview",
      instructions: [
        InstructionItem(
          title: "Prepare Yourself",
          description: "Find a quiet space where you can speak clearly without interruptions. Make sure you have good internet connection.",
          icon: Icons.book
        ),
        InstructionItem(
          title: "Speak Clearly",
          description: "When recording your answers, speak clearly and at a normal pace. The AI will transcribe your speech automatically.",
          icon: Icons.record_voice_over,
          isImportant: true,
        ),
        InstructionItem(
          title: "Listen Carefully",
          description: "Pay attention to each question asked by the interviewer. Take a moment to think before responding.",
          icon: Icons.hearing,
        ),
        InstructionItem(
          title: "Answer Naturally",
          description: "Respond as you would in a real interview. Be honest, professional, and provide specific examples when possible.",
          icon: Icons.psychology,
        ),
        InstructionItem(
          title: "Use the Record Button",
          description: "Tap the microphone button to start recording your answer. Tap again to stop and send your response.",
          icon: Icons.mic,
          isImportant: true,
        ),
        InstructionItem(
          title: "Complete the Session",
          description: "Answer all questions to get a comprehensive evaluation. The interview will end automatically when complete.",
          icon: Icons.check_circle_outline,
        ),
        InstructionItem(
          title: "Review Your Performance",
          description: "After completing the interview, you'll receive detailed feedback on your performance, including strengths and areas for improvement.",
          icon: Icons.analytics_outlined,
        ),
      ],
      onStartPressed: () {
        context.push('/interview');
      },
    );
  }
}