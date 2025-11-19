class PronunciationHistory {
  final String soal;
  final double nilai;
  final DateTime waktulatihan;
  final String typelatihan;
  final List<PhonemeComparison>? phonemeComparison;
  final int idsoal;

  PronunciationHistory({
    required this.soal,
    required this.nilai,
    required this.waktulatihan,
    required this.typelatihan,
    this.phonemeComparison,
    required this.idsoal,
  });

  factory PronunciationHistory.fromJson(Map<String, dynamic> json) {
    List<PhonemeComparison>? phonemeComp;
    
    if (json['phoneme_comparison'] != null) {
      phonemeComp = (json['phoneme_comparison'] as List)
          .map((item) => PhonemeComparison.fromJson(item))
          .toList();
    }

    return PronunciationHistory(
      soal: json['soal'] ?? '',
      nilai: (json['nilai'] ?? 0.0).toDouble(),
      waktulatihan: DateTime.parse(json['waktulatihan']),
      typelatihan: json['typelatihan'] ?? '',
      phonemeComparison: phonemeComp,
      idsoal: json['idsoal'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'soal': soal,
      'nilai': nilai,
      'waktulatihan': waktulatihan.toIso8601String(),
      'typelatihan': typelatihan,
      'phoneme_comparison': phonemeComparison?.map((e) => e.toJson()).toList(),
      'idsoal': idsoal,
    };
  }
}

class PhonemeComparison {
  final String target;
  final String user;
  final String status;

  PhonemeComparison({
    required this.target,
    required this.user,
    required this.status,
  });

  factory PhonemeComparison.fromJson(Map<String, dynamic> json) {
    return PhonemeComparison(
      target: json['target'] ?? '',
      user: json['user'] ?? '',
      status: json['status'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'target': target,
      'user': user,
      'status': status,
    };
  }
}