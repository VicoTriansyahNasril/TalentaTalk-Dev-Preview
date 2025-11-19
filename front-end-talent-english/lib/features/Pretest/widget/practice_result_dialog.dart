import 'package:flutter/material.dart';
import '../bloc/pretest_pronunciation_state.dart';

class PracticeResultDialog extends StatelessWidget {
  final double accuracyPercent;
  final List<PhonemeResult> phonemeComparison;
  final String targetPhrase;
  final VoidCallback onNext;

  const PracticeResultDialog({
    super.key,
    required this.accuracyPercent,
    required this.phonemeComparison,
    required this.targetPhrase,
    required this.onNext,
  });

  @override
  Widget build(BuildContext context) {
    final String feedbackMessage = _getFeedbackMessage(accuracyPercent);
    final Color accuracyColor = _getAccuracyColor(accuracyPercent);

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 400),
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  Icon(
                    accuracyPercent >= 75 ? Icons.celebration : Icons.psychology,
                    color: accuracyColor,
                    size: 24,
                  ),
                  const SizedBox(width: 8),
                  const Expanded(
                    child: Text(
                      "Pronunciation Result",
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "Target Sentence:",
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      targetPhrase,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: accuracyColor.withOpacity(0.1),
                  border: Border.all(color: accuracyColor, width: 3),
                ),
                child: Center(
                  child: Text(
                    "${accuracyPercent.toStringAsFixed(1)}%",
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: accuracyColor,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),

              Text(
                feedbackMessage,
                style: TextStyle(
                  fontSize: 14,
                  color: accuracyColor,
                  fontWeight: FontWeight.w500,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),

              if (phonemeComparison.isNotEmpty) ...[
                const Divider(),
                const SizedBox(height: 12),
                Row(
                  children: [
                    const Icon(
                      Icons.record_voice_over,
                      size: 18,
                      color: Colors.grey,
                    ),
                    const SizedBox(width: 8),
                    const Text(
                      "Phoneme Analysis",
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      "${_getCorrectPhonemes()} / ${phonemeComparison.length}",
                      style: const TextStyle(
                        fontSize: 12,
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Container(
                  constraints: const BoxConstraints(maxHeight: 150),
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemCount: phonemeComparison.length,
                    itemBuilder: (context, index) {
                      final result = phonemeComparison[index];
                      return Container(
                        margin: const EdgeInsets.only(bottom: 8),
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: result.isCorrect
                              ? Colors.green.withOpacity(0.1)
                              : Colors.red.withOpacity(0.1),
                          border: Border.all(
                            color: result.isCorrect ? Colors.green : Colors.red,
                            width: 1,
                          ),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              result.isCorrect
                                  ? Icons.check_circle_outline
                                  : Icons.error_outline,
                              color: result.isCorrect ? Colors.green : Colors.red,
                              size: 16,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: RichText(
                                text: TextSpan(
                                  children: [
                                    TextSpan(
                                      text: "Expected: ",
                                      style: const TextStyle(
                                        fontSize: 12,
                                        color: Colors.grey,
                                      ),
                                    ),
                                    TextSpan(
                                      text: result.targetPhoneme,
                                      style: const TextStyle(
                                        fontSize: 12,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.black,
                                      ),
                                    ),
                                    TextSpan(
                                      text: " → Your: ",
                                      style: const TextStyle(
                                        fontSize: 12,
                                        color: Colors.grey,
                                      ),
                                    ),
                                    TextSpan(
                                      text: result.userPhoneme,
                                      style: TextStyle(
                                        fontSize: 12,
                                        fontWeight: FontWeight.bold,
                                        color: result.isCorrect ? Colors.green : Colors.red,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(height: 16),
              ],

              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  TextButton(
                    onPressed: () {
                      Navigator.of(context).pop();
                    },
                    child: const Text("Close"),
                  ),
                  ElevatedButton.icon(
                    onPressed: onNext,
                    icon: const Icon(Icons.arrow_forward),
                    label: const Text("Continue"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
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

  int _getCorrectPhonemes() {
    return phonemeComparison.where((result) => result.isCorrect).length;
  }

  String _getFeedbackMessage(double accuracy) {
    if (accuracy >= 90) {
      return "Excellent! Perfect pronunciation!";
    } else if (accuracy >= 80) {
      return "Very good! Minor improvements needed.";
    } else if (accuracy >= 70) {
      return "Good job! Keep practicing!";
    } else if (accuracy >= 60) {
      return "Not bad! You're getting there!";
    } else {
      return "Keep trying! Practice makes perfect!";
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