import 'package:flutter_bloc/flutter_bloc.dart';
import 'course_event.dart';
import 'course_state.dart';
import '../model/course_model.dart';
import 'package:flutter/material.dart';
class CourseBloc extends Bloc<CourseEvent, CourseState> {
  CourseBloc() : super(CourseInitial()) {
    on<LoadCourses>((event, emit) async {
      emit(CourseLoading());
      try {
        await Future.delayed(const Duration(seconds: 1));
        final courses = [
          Course(
            title: 'Conversation',
            progress: '',
            color: Colors.green,
            icon: const Icon(Icons.chat, color: Colors.white, size: 50),
            route: '/conversation-training',
          ),
          Course(
            title: 'Pronunciation',
            progress: '',
            color: Colors.blue,
            icon: const Icon(Icons.record_voice_over, color: Colors.white, size: 50),
            route: '/pronunciation-training',
          ),
        ];


        emit(CourseLoaded(courses));
      } catch (e) {
        emit(CourseError("Failed to load courses"));
      }
    });
  }
}
