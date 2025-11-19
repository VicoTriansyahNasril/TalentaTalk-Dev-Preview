import '../model/similar_phoneme_pair.dart';

final List<SimilarPhonemePair> vowelPairs = [
  SimilarPhonemePair(phonemes: ['i', 'ɪ'], examples: ['beet', 'bit']),
  SimilarPhonemePair(phonemes: ['æ', 'ɛ'], examples: ['bat', 'bet']),
  SimilarPhonemePair(phonemes: ['u', 'ʊ'], examples: ['boot', 'book']),
  SimilarPhonemePair(phonemes: ['ə', 'ʌ', 'ɚ'], examples: ['sofa', 'cup', 'teacher']),
  SimilarPhonemePair(phonemes: ['ɑ', 'ɔ', 'ʌ'], examples: ['father', 'bought', 'cup']),
  SimilarPhonemePair(phonemes: ['ɑ', 'ɔ', 'oʊ'], examples: ['father', 'bought', 'go']),
  SimilarPhonemePair(phonemes: ['oʊ', 'ɔ', 'ʊ'], examples: ['go', 'bought', 'book']),
  SimilarPhonemePair(phonemes: ['oʊ', 'u', 'ʊ'], examples: ['go', 'boot', 'book']),
  SimilarPhonemePair(phonemes: ['ɛ', 'i', 'ɪ'], examples: ['bet', 'beet', 'bit']),
  SimilarPhonemePair(phonemes: ['æ', 'ɛ', 'ɪ'], examples: ['bat', 'bet', 'bit']),
  SimilarPhonemePair(phonemes: ['eɪ', 'ɛ', 'ɪ'], examples: ['day', 'bet', 'bit']),
  SimilarPhonemePair(phonemes: ['aɪ', 'ɑ', 'ɪ'], examples: ['my', 'father', 'bit']),
  SimilarPhonemePair(phonemes: ['ɔ', 'ɔɪ', 'ɪ'], examples: ['bought', 'boy', 'bit']),
  SimilarPhonemePair(phonemes: ['aʊ', 'ɑ', 'ʊ'], examples: ['now', 'father', 'book']),
];

final List<SimilarPhonemePair> consonantPairs = [
  SimilarPhonemePair(phonemes: ['b', 'p'], examples: ['bat', 'pat']),
  SimilarPhonemePair(phonemes: ['d', 't'], examples: ['dog', 'top']),
  SimilarPhonemePair(phonemes: ['g', 'k'], examples: ['go', 'cat']),
  SimilarPhonemePair(phonemes: ['f', 'v'], examples: ['fan', 'van']),
  SimilarPhonemePair(phonemes: ['ð', 'θ'], examples: ['the', 'think']),
  SimilarPhonemePair(phonemes: ['s', 'z'], examples: ['sun', 'zoo']),
  SimilarPhonemePair(phonemes: ['ʒ', 'ʃ'], examples: ['measure', 'shoe']),
  SimilarPhonemePair(phonemes: ['dʒ', 'tʃ'], examples: ['judge', 'church']),
  SimilarPhonemePair(phonemes: ['m', 'n'], examples: ['mom', 'nun']),
  SimilarPhonemePair(phonemes: ['n', 'ŋ'], examples: ['nun', 'sing']),
  SimilarPhonemePair(phonemes: ['l', 'r'], examples: ['light', 'right']),
  SimilarPhonemePair(phonemes: ['i', 'j'], examples: ['eat', 'yes']),
  SimilarPhonemePair(phonemes: ['u', 'w'], examples: ['boot', 'water']),
  SimilarPhonemePair(phonemes: ['m', 'n', 'ŋ'], examples: ['mom', 'nun', 'sing']),
];