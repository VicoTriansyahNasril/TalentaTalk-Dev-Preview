class LearningStreak {
  final int currentStreak;
  final int thisWeekActivities;

  LearningStreak({
    required this.currentStreak,
    required this.thisWeekActivities,
  });

  factory LearningStreak.fromJson(Map<String, dynamic> json) {
    return LearningStreak(
      currentStreak: json['current_streak'],
      thisWeekActivities: json['this_week_activities'],
    );
  }
}


