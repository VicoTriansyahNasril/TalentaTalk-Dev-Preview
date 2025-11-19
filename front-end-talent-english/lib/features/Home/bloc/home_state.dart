import 'package:equatable/equatable.dart';
import '../models/user_activity.dart';
import '../models/learning_streak.dart';
import '../models/quick_stats.dart';
import '../models/exam_summary.dart';

abstract class HomeState extends Equatable {
  const HomeState();

  @override
  List<Object?> get props => [];
}

class HomeInitial extends HomeState {}

class HomeLoading extends HomeState {}

class HomeLoaded extends HomeState {
  final String userName;
  final List<UserActivity> activities;
  final LearningStreak? learningStreak;
  final QuickStats? quickStats;
  final ExamSummary? examSummary;
  final double accuracy;
  final int totalTests;
  final int? lastTestDaysAgo;
  final double? lastScore;

  const HomeLoaded({
    required this.userName,
    required this.activities,
    this.learningStreak,
    this.quickStats,
    this.examSummary,
    required this.accuracy,
    required this.totalTests,
    this.lastTestDaysAgo,
    this.lastScore,
  });

  @override
  List<Object?> get props => [
        userName,
        activities,
        learningStreak,
        quickStats,
        examSummary,
        accuracy,
        totalTests,
        lastTestDaysAgo,
        lastScore,
      ];
}

class HomeError extends HomeState {
  final String message;

  const HomeError({required this.message});

  @override
  List<Object> get props => [message];
}

class HomeTokenExpired extends HomeState {}