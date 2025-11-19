// lib/features/Conversation/profesional_conversation/exercise/conversation_instruction_screen.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../widgets/instruction_screen.dart';

class ConversationInstructionScreen extends StatelessWidget {
  const ConversationInstructionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return InstructionScreen(
      title: "Professional Conversation",
      subtitle: "Practice your English conversation skills in a professional setting",
      headerIcon: Icons.record_voice_over,
      primaryColor: Colors.blue,
      estimatedTime: "10-15 min",
      startButtonText: "Start Conversation",
      instructions: const [
        InstructionItem(
          title: "Grant Microphone Permission",
          description: "Allow the app to access your microphone for recording your voice during the conversation.",
          icon: Icons.mic,
          isImportant: true,
        ),
        InstructionItem(
          title: "Tap to Record",
          description: "Press the microphone button to start recording your response. Speak clearly and at a normal pace.",
          icon: Icons.play_circle,
        ),
        InstructionItem(
          title: "Stop Recording",
          description: "Tap the microphone button again to stop recording. Your audio will be processed automatically.",
          icon: Icons.stop_circle,
        ),
        InstructionItem(
          title: "Wait for Processing",
          description: "The system will transcribe your audio and generate an appropriate response. Please wait for the processing to complete.",
          icon: Icons.hourglass_empty,
        ),
        InstructionItem(
          title: "Continue Conversation",
          description: "Read the AI response and continue the conversation by recording your next response when ready.",
          icon: Icons.chat_bubble,
        ),
        InstructionItem(
          title: "End Session",
          description: "When you're ready to finish, tap the 'End Conversation' button to generate your conversation report.",
          icon: Icons.assignment,
        ),
      ],
      onStartPressed: () {
        context.push('/conversation');
      },
    );
  }
}