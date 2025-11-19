class InterviewHistory {
  final double wpm;
  final String grammar;
  final String feedback;
  final DateTime waktulatihan;

  InterviewHistory({
    required this.wpm,
    required this.grammar,
    required this.feedback,
    required this.waktulatihan,
  });

  factory InterviewHistory.fromJson(Map<String, dynamic> json) {
    return InterviewHistory(
      wpm: json['wpm'],
      grammar: json['grammar'],
      feedback: json['feedback'],
      waktulatihan: DateTime.parse(json['waktulatihan']),
    );
  }
}
