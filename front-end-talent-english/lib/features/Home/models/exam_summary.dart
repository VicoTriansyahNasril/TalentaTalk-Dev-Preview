class ExamSummary {
  final double? latestExamScore;
  final int totalExams;
  final double? averageExamScore;
  final int? lastExamDaysAgo;

  ExamSummary({
    this.latestExamScore,
    required this.totalExams,
    this.averageExamScore,
    this.lastExamDaysAgo,
  });

  factory ExamSummary.fromJson(Map<String, dynamic> json) {
    return ExamSummary(
      latestExamScore: json['latest_exam_score']?.toDouble(),
      totalExams: json['total_exams'],
      averageExamScore: json['average_exam_score']?.toDouble(),
      lastExamDaysAgo: json['last_exam_days_ago'],
    );
  }
}
