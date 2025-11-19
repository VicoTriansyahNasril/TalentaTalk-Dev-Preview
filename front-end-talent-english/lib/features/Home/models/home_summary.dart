import 'user_activity.dart';
import 'learning_streak.dart';
import 'quick_stats.dart';
import 'exam_summary.dart';

class HomeSummary {
  final List<UserActivity> activities;
  final double lastScore;
  final int totalTests;
  final double accuracy;
  final int lastTestDaysAgo;
  final String userName;
  final LearningStreak? learningStreak;
  final QuickStats? quickStats;
  final ExamSummary? examSummary;

  HomeSummary({
    required this.activities,
    required this.lastScore,
    required this.totalTests,
    required this.accuracy,
    required this.lastTestDaysAgo,
    required this.userName,
    this.learningStreak,
    this.quickStats,
    this.examSummary,
  });

  factory HomeSummary.fromJson(Map<String, dynamic> json) {
    final recent = json['recent_activities']['data'] as List;
    final exam = json['exam_summary'];
    final user = json['user'];

    return HomeSummary(
      activities: recent.map((e) => UserActivity.fromJson(e)).toList(),
      lastScore: (exam['latest_exam_score'] ?? 0).toDouble(),
      totalTests: exam['total_exams'] ?? 0,
      accuracy: (exam['average_exam_score'] ?? 0).toDouble(),
      lastTestDaysAgo: exam['last_exam_days_ago'] ?? 0,
      userName: user['name'] ?? 'User',
      learningStreak: json['learning_streak'] != null 
          ? LearningStreak.fromJson(json['learning_streak']) 
          : null,
      quickStats: json['quick_stats'] != null 
          ? QuickStats.fromJson(json['quick_stats']) 
          : null,
      examSummary: json['exam_summary'] != null 
          ? ExamSummary.fromJson(json['exam_summary']) 
          : null,
    );
  }
}