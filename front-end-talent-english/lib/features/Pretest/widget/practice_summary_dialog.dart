import 'package:flutter/material.dart';
import '../bloc/pretest_pronunciation_state.dart';

class PracticeSummaryDialog extends StatelessWidget {
  final double averageScore;
  final List<CompletedSentenceResult> completedSentences;
  final VoidCallback onClose;

  const PracticeSummaryDialog({
    super.key,
    required this.averageScore,
    required this.completedSentences,
    required this.onClose,
  });

  @override
  Widget build(BuildContext context) {
    final averagePercent = averageScore * 100;
    final String overallFeedback = _getOverallFeedback(averagePercent);
    final Color scoreColor = _getScoreColor(averagePercent);

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        constraints: const BoxConstraints(maxHeight: 600, maxWidth: 400),
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.emoji_events,
                    color: scoreColor,
                    size: 28,
                  ),
                  const SizedBox(width: 8),
                  const Expanded(
                    child: Text(
                      "Practice Complete!",
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),

              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: scoreColor.withOpacity(0.1),
                  border: Border.all(color: scoreColor, width: 4),
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        "${averagePercent.toStringAsFixed(1)}%",
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: scoreColor,
                        ),
                      ),
                      const Text(
                        "Average",
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              Text(
                overallFeedback,
                style: TextStyle(
                  fontSize: 16,
                  color: scoreColor,
                  fontWeight: FontWeight.w500,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),

              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildStatItem(
                      "Total Sentences",
                      completedSentences.length.toString(),
                      Icons.format_list_numbered,
                    ),
                    _buildStatItem(
                      "Best Score",
                      "${_getBestScore().toStringAsFixed(1)}%",
                      Icons.star,
                    ),
                    _buildStatItem(
                      "Lowest Score",
                      "${_getLowestScore().toStringAsFixed(1)}%",
                      Icons.trending_down,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              const Text(
                "Detailed Results",
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              
              Flexible(
                child: Container(
                  constraints: const BoxConstraints(maxHeight: 200),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey[300]!),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemCount: completedSentences.length,
                    itemBuilder: (context, index) {
                      final result = completedSentences[index];
                      final scorePercent = result.score * 100;
                      return Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          border: index < completedSentences.length - 1
                              ? Border(bottom: BorderSide(color: Colors.grey[200]!))
                              : null,
                        ),
                        child: Row(
                          children: [
                            Container(
                              width: 30,
                              height: 30,
                              decoration: BoxDecoration(
                                color: _getScoreColor(scorePercent).withOpacity(0.1),
                                border: Border.all(color: _getScoreColor(scorePercent)),
                                borderRadius: BorderRadius.circular(15),
                              ),
                              child: Center(
                                child: Text(
                                  "${index + 1}",
                                  style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.bold,
                                    color: _getScoreColor(scorePercent),
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    result.sentence.content,
                                    style: const TextStyle(
                                      fontSize: 14,
                                      fontWeight: FontWeight.w500,
                                    ),
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  if (result.sentence.category.isNotEmpty)
                                    Text(
                                      "Category: ${result.sentence.category}",
                                      style: const TextStyle(
                                        fontSize: 12,
                                        color: Colors.grey,
                                      ),
                                    ),
                                ],
                              ),
                            ),
                            
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 8,
                                vertical: 4,
                              ),
                              decoration: BoxDecoration(
                                color: _getScoreColor(scorePercent).withOpacity(0.1),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                "${scorePercent.toStringAsFixed(1)}%",
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  color: _getScoreColor(scorePercent),
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
              ),
              const SizedBox(height: 20),

              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  TextButton.icon(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text("Share feature coming soon!")),
                      );
                    },
                    icon: const Icon(Icons.share),
                    label: const Text("Share"),
                    style: TextButton.styleFrom(
                      foregroundColor: Colors.blue,
                    ),
                  ),
                  ElevatedButton.icon(
                    onPressed: onClose,
                    icon: const Icon(Icons.check),
                    label: const Text("Finish"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 24,
                        vertical: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(
          icon,
          color: Colors.blue,
          size: 20,
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontSize: 10,
            color: Colors.grey,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  double _getBestScore() {
    if (completedSentences.isEmpty) return 0.0;
    return completedSentences
        .map((e) => e.score * 100)
        .reduce((a, b) => a > b ? a : b);
  }

  double _getLowestScore() {
    if (completedSentences.isEmpty) return 0.0;
    return completedSentences
        .map((e) => e.score * 100)
        .reduce((a, b) => a < b ? a : b);
  }

  String _getOverallFeedback(double averagePercent) {
    if (averagePercent >= 90) {
      return "Outstanding! You've mastered pronunciation practice!";
    } else if (averagePercent >= 80) {
      return "Excellent work! Your pronunciation skills are strong!";
    } else if (averagePercent >= 70) {
      return "Great job! You're making good progress!";
    } else if (averagePercent >= 60) {
      return "Good effort! Keep practicing to improve further!";
    } else {
      return "Keep practicing! Every session makes you better!";
    }
  }

  Color _getScoreColor(double scorePercent) {
    if (scorePercent >= 90) {
      return Colors.green;
    } else if (scorePercent >= 75) {
      return Colors.lightGreen;
    } else if (scorePercent >= 60) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }
}