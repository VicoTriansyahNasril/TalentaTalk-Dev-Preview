class SimilarPhonemePair {
  final List<String> phonemes;
  final List<String> examples;
  
  const SimilarPhonemePair({
    required this.phonemes,
    required this.examples,
  });

  // Backward compatibility getters
  String get phoneme1 => phonemes.isNotEmpty ? phonemes[0] : '';
  String get example1 => examples.isNotEmpty ? examples[0] : '';
  String get phoneme2 => phonemes.length > 1 ? phonemes[1] : '';
  String get example2 => examples.length > 1 ? examples[1] : '';
}