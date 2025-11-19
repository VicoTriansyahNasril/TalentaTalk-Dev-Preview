class MateriUjian {
  final int id;
  final String kategori;

  MateriUjian({required this.id, required this.kategori});

  factory MateriUjian.fromJson(Map<String, dynamic> json) {
    return MateriUjian(
      id: json['idmateriujian'],
      kategori: json['kategori'],
    );
  }
}
