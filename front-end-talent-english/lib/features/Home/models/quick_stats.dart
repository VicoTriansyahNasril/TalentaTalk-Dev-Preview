class QuickStats {
  final int totalTrainingSessions;
  final double? avgPhonemeScore;
  final double? avgSpeakingWpm;
  final int phonemeSessions;
  final int speakingSessions;

  QuickStats({
    required this.totalTrainingSessions,
    this.avgPhonemeScore,
    this.avgSpeakingWpm,
    required this.phonemeSessions,
    required this.speakingSessions,
  });

  factory QuickStats.fromJson(Map<String, dynamic> json) {
    return QuickStats(
      totalTrainingSessions: json['total_training_sessions'],
      avgPhonemeScore: json['avg_phoneme_score']?.toDouble(),
      avgSpeakingWpm: json['avg_speaking_wpm']?.toDouble(),
      phonemeSessions: json['phoneme_sessions'],
      speakingSessions: json['speaking_sessions'],
    );
  }
}