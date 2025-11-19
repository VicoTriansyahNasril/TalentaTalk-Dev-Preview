import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:front_end_talent/features/Conversation/interview/service/interview_service.dart';
import 'package:front_end_talent/features/Conversation/profesional_conversation/exercise/service/conversation_service.dart';
import '../features/Conversation/interview/bloc/interview_bloc.dart';
import '../features/Conversation/interview/bloc/interview_event.dart';
import '../features/Conversation/interview/interview_instruction.dart';
import '../features/Conversation/interview/repository/interview_repository.dart';
import '../features/Conversation/profesional_conversation/exercise/conversation_instruction.dart';
import '../features/Exam/exammaterial/exam_material_screen.dart';
import '../features/Exam/exampronunciation/exam_pronunciation_instruction.dart';
import '../features/Exam/exampronunciation/exam_pronunciation_screen.dart';
import 'package:go_router/go_router.dart';
import '../features/Auth/bloc/auth_event.dart';
import '../features/Exam/examscore/exam_score_screen.dart';
import '../features/History/bloc/history_bloc.dart';
import '../features/History/history_screen.dart';
import '../features/History/repository/history_repository.dart';
import '../features/History/service/history_service.dart';
import '../features/Onboarding/onboarding_screen.dart';
import '../features/Pretest/pretest_instruction_screen.dart';
import '../features/Pronunciation/phoneme/phoneme_category_screen.dart';
import '../features/Pronunciation/sentences/exercise/pronunciation_sentence_instruction.dart';
import '../features/Pronunciation/similiarphoneme/similiar_phoneme.dart';
import '../features/Pronunciation/words/exercise/pronunciation_words_instruction.dart';
import '../features/home/home_screen.dart';
import '../features/Course/course_screen.dart';
import '../features/splash/splash_screen.dart';
import '../features/navigation/nav_wrapper.dart';
import '../features/Pronunciation/course/pronunciation_course_screen.dart';
import '../features/Pretest/pretest_pronunciation_screen.dart';
import '../features/Conversation/interview/interview_screen.dart';
import '../features/Pronunciation/sentences/exercise/pronunciation_sentences_screen.dart';
import '../features/Conversation/profesional_conversation/exercise/conversation_screen.dart';
import '../features/Conversation/profesional_conversation/exercise/bloc/conversation_bloc.dart';
import '../features/Conversation/profesional_conversation/exercise/bloc/conversation_event.dart';
import '../features/Conversation/profesional_conversation/exercise/repository/conversation_repository.dart';
import '../features/Conversation/course/conversation_course_screen.dart';
import '../features/Pronunciation/words/exercise/pronunciation_words_screen.dart';
import '../features/Auth/login_screen.dart';
import '../features/Auth/bloc/auth_bloc.dart';
import '../features/Auth/repository/auth_repository.dart';
import '../features/Pronunciation/sentences/material/material_list_screen.dart';
import '../features/Pronunciation/words/material/material_list_screen.dart';
import '../features/Profile/profile_screen.dart';
import '../features/Exam/examphoneme/exam_phoneme.dart';
import '../features/Exam/exampronunciation/exam_pronunciation_screen.dart';

final GoRouter appRouter = GoRouter(
  initialLocation: '/',
  routes: [
     GoRoute(
      path: '/',
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: '/conversation',
      builder: (context, state) => BlocProvider(
        create: (_) => ConversationBloc(
          ConversationRepository(service: ConversationService()),
        )..add(StartConversationEvent()),
        child: const ConversationScreen(),
      ),
    ),
    
    GoRoute(
      path: '/interview',
      builder: (context, state) {
        return BlocProvider(
          create: (context) => InterviewBloc(
            repository: InterviewRepository(service:InterviewService()),
          )..add(StartInterview()),
          child: const InterviewScreen(),
        );
      },
    ),
    GoRoute(
      path: '/pretest',
      name: 'pretest',
      builder: (context, state) => const PracticePronunciationScreen(),
    ),
    GoRoute(
      path: '/pretest_instruction',
      name: 'pretest_instruction',
      builder: (context, state) => const PretestPronunciationInstructionScreen(),
    ),
    GoRoute(
      path: '/pronunciation_exam_instruction/:id',
      name: 'pronunciation_exam_instruction',
      builder: (context, state) {
        final examId = int.parse(state.pathParameters['id']!);
        return ExamPronunciationInstructionScreen(examId: examId);
      },
    ),
    GoRoute(
      path: '/pronunciation_sentence_instruction/:id',
      name: 'pronunciation_sentence_instruction',
      builder: (context, state) {
        final idString = state.pathParameters['id']!;
        final id = int.parse(idString);
        return PronunciationSentencesInstructionScreen(materialId: id);
      },
    ),
    GoRoute(
      path: '/pronunciation_words_instruction/:id',
      name: 'pronunciation_words_instruction',
      builder: (context, state) {
        final idString = state.pathParameters['id']!;
        final id = int.parse(idString);
        return PronunciationWordsInstructionScreen(materialId: id);
      },
    ),
    GoRoute(
      path: '/interview_instruction',
      name: 'interview_instruction',
      builder: (context, state) => const InterviewInstructionScreen(),
    ),
    GoRoute(
      path: '/conversation_instruction',
      name: 'conversation_instruction',
      builder: (context, state) => const ConversationInstructionScreen(),
    ),
    
    GoRoute(
      path: '/login',
      builder: (context, state) => BlocProvider(
        create: (_) => AuthBloc(AuthRepository())..add(CheckAuthStatusEvent()),
        child: const LoginScreen(),
      ),
    ),
    GoRoute(
      path: '/onboarding',
      builder: (context, state) => const OnboardingScreen(),
    ),
    GoRoute(
      path: '/pronunciation_sentence/:id',
      name: 'pronunciation_sentence',
      builder: (context, state) {
        final idString = state.pathParameters['id']!;
        final id = int.parse(idString);
        return PronunciationSentencesScreen(idMaterial: id);
      },
    ),
    GoRoute(
      path: '/pronunciation_word/:id',
      name: 'pronunciation_words',
      builder: (context, state) {
        final idString = state.pathParameters['id']!;
        final id = int.parse(idString);
        return PronunciationWordsScreen(idMaterial: id);
      },
    ),
    GoRoute(
      path: '/pronunciation_exam/:id',
      name: 'pronunciation_exam',
      builder: (context, state) {
        final examid = state.pathParameters['id']!;
        final id = int.parse(examid);
        return ExamPronunciationScreen(examId: id);
      },
    ),

    GoRoute(
      path: '/training-history',
      name: 'training_history',
      builder: (context, state) => BlocProvider(
        create: (context) => TrainingHistoryBloc(
          repository: TrainingHistoryRepository(
            service: TrainingHistoryService(),
          ),
        ),
        child: TrainingHistoryScreen(),
      ),
    ),
    GoRoute(
      path: '/exam_score/:id',
      name: 'exam_score',
      builder: (context, state) {
        final id = int.parse(state.pathParameters['id']!);
        return ExamScoreScreen(examId: id);
      },
    ),

    
    ShellRoute(
      builder: (context, state, child) {
        
        int index = 0;
        final currentLocation = state.matchedLocation;
        
        final coursePaths = [
          '/course',
          '/pronunciation-training',
          '/conversation-training',
          '/contrastive-phoneme',
          '/phoneme-category',
          '/exam-phoneme',
          '/materials',
          '/material_words',
          '/exam_material'
        ];
        
        if (currentLocation == '/home') {
          index = 0;
        } else if (coursePaths.contains(currentLocation)) {
          index = 1;
        } else if (currentLocation == '/profile') {
          index = 2;
        }
        
        return NavWrapper(child: child, currentIndex: index);
      },
      routes: [
        GoRoute(
          path: '/home',
          builder: (context, state) => const HomeScreen(),
        ),
        GoRoute(
          path: '/course',
          builder: (context, state) => const CourseScreen(),
        ),
        GoRoute(
          path: '/profile',
          builder: (context, state) => const ProfileScreen(),
        ),
        GoRoute(
          path: '/pronunciation-training',
          builder: (context, state) => const PronunciationCourseScreen(),
        ),
        GoRoute(
          path: '/conversation-training',
          builder: (context, state) => const ConversationCourseScreen(),
        ),
        GoRoute(
          path: '/contrastive-phoneme',
          builder: (context, state) => const SimilarPhonemePairScreen(),
        ),
        GoRoute(
          path: '/phoneme-category',
          builder: (context, state) => const PhonemeCategoryScreen(),
        ),
        GoRoute(
          path: '/exam-phoneme',
          builder: (context, state) => const ExamPhonemeScreen(),
        ),
        GoRoute(
          path: '/materials',
          name: 'material_list',
          builder: (context, state) {
            final phonemes = state.uri.queryParameters['phonemes'];
            final phoneme1 = state.uri.queryParameters['phoneme1'];
            final phoneme2 = state.uri.queryParameters['phoneme2'];
            
            List<String> phonemeList = [];
            
            if (phonemes != null && phonemes.isNotEmpty) {
              phonemeList = phonemes.split(',').map((p) => p.trim()).toList();
            } else if (phoneme1 != null && phoneme2 != null) {
              phonemeList = [phoneme1, phoneme2];
            }
            
            if (phonemeList.isEmpty) {
              return const Scaffold(
                body: Center(child: Text('No phonemes specified')),
              );
            }
            
            return MaterialListScreen(phonemes: phonemeList);
          },
        ),
        GoRoute(
          path: '/material_words/:phoneme',
          name: 'material_words',
          builder: (context, state) {
            final phoneme = state.pathParameters['phoneme']!;
            return WordMaterialScreen(phoneme: phoneme);
          },
        ),
        GoRoute(
          path: '/exam_materials',
          name: 'exam_material',
          builder: (context, state) {
            final phonemes = state.uri.queryParameters['phonemes'];
            final phoneme1 = state.uri.queryParameters['phoneme1'];
            final phoneme2 = state.uri.queryParameters['phoneme2'];
            
            List<String> phonemeList = [];
            
            if (phonemes != null && phonemes.isNotEmpty) {
              phonemeList = phonemes.split(',').map((p) => p.trim()).toList();
            } else if (phoneme1 != null && phoneme2 != null) {
              phonemeList = [phoneme1, phoneme2];
            }
            
            if (phonemeList.isEmpty) {
              return const Scaffold(
                body: Center(child: Text('No phonemes specified for exam')),
              );
            }
            
            return ExamMaterialScreen(phonemes: phonemeList);
          },
        ),

      ],
    ),
  ],
);
