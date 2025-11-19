class InterviewSummary {
  final Map<String, dynamic> summary;
  final Map<String, dynamic> statistics;
  final String message;

  InterviewSummary({
    required this.summary,
    required this.statistics,
    required this.message,
  });

  factory InterviewSummary.fromJson(Map<String, dynamic> json) {
    return InterviewSummary(
      summary: json['summary']?['summary'] ?? {},
      statistics: json['statistics'] ?? {},
      message: json['message'] ?? '',
    );
  }
}
