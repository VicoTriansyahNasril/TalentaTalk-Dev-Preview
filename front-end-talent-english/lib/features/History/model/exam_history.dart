class ExamHistory {
  final int idujian;
  final String kategori;
  final double nilaiTotal;
  final DateTime waktuujian;
  final DateTime? updatedAt;
  final List<ExamDetail> details;

  ExamHistory({
    required this.idujian,
    required this.kategori,
    required this.nilaiTotal,
    required this.waktuujian,
    this.updatedAt,
    required this.details,
  });

  factory ExamHistory.fromJson(Map<String, dynamic> json) {
    return ExamHistory(
      idujian: json['idujian'] ?? 0,
      kategori: json['kategori'] ?? '',
      nilaiTotal: (json['nilai_total'] ?? 0.0).toDouble(),
      waktuujian: DateTime.parse(json['waktuujian']),
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      details: (json['details'] as List? ?? [])
          .map((item) => ExamDetail.fromJson(item))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'idujian': idujian,
      'kategori': kategori,
      'nilai_total': nilaiTotal,
      'waktuujian': waktuujian.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'details': details.map((e) => e.toJson()).toList(),
    };
  }
}

class ExamDetail {
  final int idsoal;
  final String kalimat;
  final double nilai;
  final DateTime? updatedAt;

  ExamDetail({
    required this.idsoal,
    required this.kalimat,
    required this.nilai,
    this.updatedAt,
  });

  factory ExamDetail.fromJson(Map<String, dynamic> json) {
    return ExamDetail(
      idsoal: json['idsoal'] ?? 0,
      kalimat: json['kalimat'] ?? '',
      nilai: (json['nilai'] ?? 0.0).toDouble(),
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'idsoal': idsoal,
      'kalimat': kalimat,
      'nilai': nilai,
      'updated_at': updatedAt?.toIso8601String(),
    };
  }
}