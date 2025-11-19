import 'package:flutter/material.dart';
import '../bloc/exam_pronunciation_state.dart';

class PronunciationResultDialog extends StatelessWidget {
  final double accuracyPercent;
  final List<PhonemeResult> phonemeComparison;
  final String targetPhrase;
  final VoidCallback? onNext;

  const PronunciationResultDialog({
    super.key,
    required this.accuracyPercent,
    required this.phonemeComparison,
    required this.targetPhrase,
    this.onNext,
  });

  @override
  Widget build(BuildContext context) {
    final String feedbackMessage = _getFeedbackMessage(accuracyPercent);
    final Color accuracyColor = _getAccuracyColor(accuracyPercent);

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              "Pronunciation Results",
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              targetPhrase,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: accuracyColor.withOpacity(0.2),
                border: Border.all(color: accuracyColor, width: 4),
              ),
              child: Center(
                child: Text(
                  "${accuracyPercent.toStringAsFixed(1)}%",
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: accuracyColor,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              feedbackMessage,
              style: TextStyle(
                fontSize: 16,
                color: accuracyColor,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 8),
            const Text(
              "Phoneme Breakdown",
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 8),
            Flexible(
              child: Container(
                constraints: const BoxConstraints(maxHeight: 200),
                child: ListView.builder(
                  shrinkWrap: true,
                  itemCount: phonemeComparison.length,
                  itemBuilder: (context, index) {
                    final result = phonemeComparison[index];
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4.0),
                      child: Row(
                        children: [
                          Icon(
                            result.isCorrect
                                ? Icons.check_circle
                                : Icons.error,
                            color: result.isCorrect
                                ? Colors.green
                                : Colors.red,
                            size: 16,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            "Target: ${result.targetPhoneme}",
                            style: const TextStyle(
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text("Your: ${result.userPhoneme}"),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                  },
                  child: const Text("Close"),
                ),
                if (onNext != null)
                  ElevatedButton(
                    onPressed: onNext,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                    ),
                    child: const Text(
                      "Next Sentence",
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _getFeedbackMessage(double accuracy) {
    if (accuracy >= 90) {
      return "Excellent! Your pronunciation is perfect!";
    } else if (accuracy >= 75) {
      return "Very good! Just a few minor improvements needed.";
    } else if (accuracy >= 60) {
      return "Good effort! Keep practicing to improve.";
    } else {
      return "Keep practicing! You'll get better with time.";
    }
  }

  Color _getAccuracyColor(double accuracy) {
    if (accuracy >= 90) {
      return Colors.green;
    } else if (accuracy >= 75) {
      return Colors.lightGreen;
    } else if (accuracy >= 60) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }
}