class ExamScoreDetail {
  final int idSoal;
  final String kalimat;
  final double nilai;

  ExamScoreDetail({
    required this.idSoal,
    required this.kalimat,
    required this.nilai,
  });

  factory ExamScoreDetail.fromJson(Map<String, dynamic> json) {
    return ExamScoreDetail(
      idSoal: json['idsoal'],
      kalimat: json['kalimat'],
      nilai: (json['nilai'] as num).toDouble(),
    );
  }
}

class ExamScoreResult {
  final int idUjian;
  final String kategori;
  final int jumlahSoal;
  final double nilaiRataRata;
  final List<ExamScoreDetail> detail;

  ExamScoreResult({
    required this.idUjian,
    required this.kategori,
    required this.jumlahSoal,
    required this.nilaiRataRata,
    required this.detail,
  });

  factory ExamScoreResult.fromJson(Map<String, dynamic> json) {
    return ExamScoreResult(
      idUjian: json['id_ujian'],
      kategori: json['kategori'],
      jumlahSoal: json['jumlah_soal'],
      nilaiRataRata: (json['nilai_rata_rata'] as num).toDouble(),
      detail: (json['detail'] as List)
          .map((item) => ExamScoreDetail.fromJson(item))
          .toList(),
    );
  }
}
