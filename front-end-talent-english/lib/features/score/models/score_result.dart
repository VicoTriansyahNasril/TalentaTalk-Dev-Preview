import 'package:flutter/material.dart';
import '../widgets/highlighted_text.dart';
class ScoreResult {
  final String userPhoneme;
  final String targetPhoneme;
  final double score;
  final List<HighlightSegment> segments;

  ScoreResult({
    required this.userPhoneme,
    required this.targetPhoneme,
    required this.score,
    required this.segments,
  });
}
