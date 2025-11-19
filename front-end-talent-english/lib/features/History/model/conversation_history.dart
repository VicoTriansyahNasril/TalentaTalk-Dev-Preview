class ConversationHistory {
  final String topic;
  final double wpm;
  final String grammar;
  final DateTime waktulatihan;

  ConversationHistory({
    required this.topic,
    required this.wpm,
    required this.grammar,
    required this.waktulatihan,
  });

  factory ConversationHistory.fromJson(Map<String, dynamic> json) {
    return ConversationHistory(
      topic: json['topic'],
      wpm: json['wpm'],
      grammar: json['grammar'],
      waktulatihan: DateTime.parse(json['waktulatihan']),
    );
  }
}