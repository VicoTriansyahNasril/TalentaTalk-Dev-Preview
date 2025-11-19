import 'package:flutter_bloc/flutter_bloc.dart';
import 'interview_event.dart';
import 'interview_state.dart';
import '../model/chat_message.dart';
import '../model/interview_summary.dart';
import '../repository/interview_repository.dart';

class InterviewBloc extends Bloc<InterviewEvent, InterviewState> {
  final InterviewRepository repository;

  InterviewBloc({required this.repository})
      : super(InterviewState(messages: [])) {
    on<StartInterview>(_onStart);
    on<SendMessage>(_onSend);
    on<FetchSummary>(_onFetchSummary);
  }

  Future<void> _onStart(StartInterview event, Emitter<InterviewState> emit) async {
    emit(state.copyWith(isLoading: true));

    final question = await repository.startInterview();
    if (question != null) {
      emit(state.copyWith(messages: [question], isLoading: false));
    } else {
      emit(state.copyWith(isLoading: false));
    }
  }

  Future<void> _onSend(SendMessage event, Emitter<InterviewState> emit) async {
    final updated = List<ChatMessage>.from(state.messages)
      ..add(ChatMessage(message: event.message, isUser: true));

    emit(state.copyWith(messages: updated, isLoading: true));

    final duration = event.duration ?? '0:10';
    print('📤 Using duration: $duration for message: ${event.message}');

    final (result, isCompleted) = await repository.sendAnswer(event.message, duration);

    final newMessages = [...updated, ...result];

    emit(state.copyWith(
      messages: newMessages,
      isLoading: false,
      interviewCompleted: isCompleted,
    ));
  }

  Future<void> _onFetchSummary(FetchSummary event, Emitter<InterviewState> emit) async {
    emit(state.copyWith(isLoading: true));
    final summary = await repository.fetchSummary();
    if (summary != null) {
      emit(state.copyWith(summary: summary, isLoading: false));
    } else {
      emit(state.copyWith(isLoading: false));
    }
  }
  
}