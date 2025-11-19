class MaterialModel {
  final int id;
  final String sentence;
  final String phoneme;
  final String category;
  final double accuracy;

  MaterialModel({
    required this.id,
    required this.sentence,
    required this.phoneme,
    required this.category,
    this.accuracy = 0.0,
  });

  factory MaterialModel.fromJson(Map<String, dynamic> json) {
    return MaterialModel(
      id: json['idContent'],
      sentence: json['content'],
      phoneme: json['phoneme'],
      category: json['phoneme_category'],
      accuracy: (json['accuracy'] ?? 0.0).toDouble(),
    );
  }
}
