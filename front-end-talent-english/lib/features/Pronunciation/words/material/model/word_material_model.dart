class WordMaterialModel {
  final int idWord;
  final String word;
  final String phoneme;

  WordMaterialModel({
    required this.idWord,
    required this.word,
    required this.phoneme,
  });

  factory WordMaterialModel.fromJson(Map<String, dynamic> json) {
    return WordMaterialModel(
      idWord: json['idContent'],
      word: json['content'],
      phoneme: json['phoneme'],
    );
  }
}
