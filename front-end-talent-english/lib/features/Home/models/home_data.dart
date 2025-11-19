import 'exam_summary.dart';
import 'learning_streak.dart';
import 'quick_stats.dart';
import 'user_activity.dart';

class HomeData {
  final UserInfo user;
  final LearningStreak learningStreak;
  final QuickStats quickStats;
  final RecentActivities recentActivities;
  final ExamSummary examSummary;

  HomeData({
    required this.user,
    required this.learningStreak,
    required this.quickStats,
    required this.recentActivities,
    required this.examSummary,
  });

  factory HomeData.fromJson(Map<String, dynamic> json) {
    return HomeData(
      user: UserInfo.fromJson(json['user']),
      learningStreak: LearningStreak.fromJson(json['learning_streak']),
      quickStats: QuickStats.fromJson(json['quick_stats']),
      recentActivities: RecentActivities.fromJson(json['recent_activities']),
      examSummary: ExamSummary.fromJson(json['exam_summary']),
    );
  }
}

class UserInfo {
  final int id;
  final String name;

  UserInfo({
    required this.id,
    required this.name,
  });

  factory UserInfo.fromJson(Map<String, dynamic> json) {
    return UserInfo(
      id: json['id'],
      name: json['name'],
    );
  }
}

class RecentActivities {
  final int total;
  final List<UserActivity> data;

  RecentActivities({
    required this.total,
    required this.data,
  });

  factory RecentActivities.fromJson(Map<String, dynamic> json) {
    return RecentActivities(
      total: json['total'],
      data: (json['data'] as List)
          .map((item) => UserActivity.fromJson(item))
          .toList(),
    );
  }
}