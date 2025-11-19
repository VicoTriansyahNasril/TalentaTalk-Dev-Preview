class UserActivity {
  final int id;
  final String title;
  final String type;
  final String? category;
  final double score;
  final String date;
  final String? time;
  final DateTime waktulatihan;

  UserActivity({
    required this.id,
    required this.title,
    required this.type,
    this.category,
    required this.score,
    required this.date,
    this.time,
    required this.waktulatihan,
  });

  factory UserActivity.fromJson(Map<String, dynamic> json) {
    return UserActivity(
      id: json['id'],
      title: json['title'],
      type: json['type'],
      category: json['category'],
      score: (json['score'] as num).toDouble(),
      date: json['date'],
      time: json['time'],
      waktulatihan: DateTime.parse(json['waktulatihan']),
    );
  }
}


