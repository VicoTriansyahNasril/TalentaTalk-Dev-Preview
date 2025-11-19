class Phoneme {
  final String phoneme;
  final String example;
  final String type;

  Phoneme({
    required this.phoneme,
    required this.example,
    required this.type,
  });

  factory Phoneme.fromJson(Map<String, dynamic> json) {
    return Phoneme(
      phoneme: json['phoneme'],
      example: json['example'],
      type: json['type'],
    );
  }
}
