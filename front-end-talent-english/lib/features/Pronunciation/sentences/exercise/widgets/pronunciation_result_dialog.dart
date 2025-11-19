
import 'package:flutter/material.dart';

class PhonemeResult {
  final String target;
  final String user;
  final String status;

  PhonemeResult({
    required this.target,
    required this.user,
    required this.status,
  });

  factory PhonemeResult.fromJson(Map<String, dynamic> json) {
    return PhonemeResult(
      target: json['target'] as String,
      user: json['user'] as String,
      status: json['status'] as String,
    );
  }
}

class PronunciationResultDialog extends StatelessWidget {
  final double accuracyPercent;
  final List<PhonemeResult> phonemeComparison;
  final String targetPhrase;

  const PronunciationResultDialog({
    Key? key,
    required this.accuracyPercent,
    required this.phonemeComparison,
    required this.targetPhrase,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              "Pronunciation Result",
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildAccuracyMeter(accuracyPercent),
            const SizedBox(height: 12),
            _buildNativeUnderstandingIndicator(accuracyPercent),
            const SizedBox(height: 20),
            const Text(
              "Target Phrase:",
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 6),
            Text(
              targetPhrase,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 20),
            const Text(
              "Phoneme Comparison:",
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            _buildComparisonTable(),
            const SizedBox(height: 16),
            _buildLegend(),
            const SizedBox(height: 20),
            _buildActionButtons(context),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButtons(BuildContext context) {
    if (accuracyPercent >= 70) {
      return Row(
        children: [
          Expanded(
            child: ElevatedButton(
              onPressed: () => Navigator.of(context).pop(false),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: const Text(
                "Try Again",
                style: TextStyle(fontSize: 16, color: Colors.white),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: ElevatedButton(
              onPressed: () => Navigator.of(context).pop(true),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: const Text(
                "Exit",
                style: TextStyle(fontSize: 16, color: Colors.white),
              ),
            ),
          ),
        ],
      );
    } else {
      return SizedBox(
        width: double.infinity,
        child: ElevatedButton(
          onPressed: () => Navigator.of(context).pop(false),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blue,
            padding: const EdgeInsets.symmetric(vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          child: const Text(
            "Try Again",
            style: TextStyle(fontSize: 16, color: Colors.white),
          ),
        ),
      );
    }
  }

  Widget _buildAccuracyMeter(double percent) {
    final Color meterColor = percent >= 80
        ? Colors.green
        : percent >= 60
            ? Colors.orange
            : Colors.red;

    return Column(
      children: [
        Text(
          "${percent.toStringAsFixed(1)}%",
          style: TextStyle(
            fontSize: 36,
            fontWeight: FontWeight.bold,
            color: meterColor,
          ),
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: LinearProgressIndicator(
            value: percent / 100,
            backgroundColor: Colors.grey[200],
            color: meterColor,
            minHeight: 12,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          _getAccuracyMessage(percent),
          style: TextStyle(
            color: meterColor,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildNativeUnderstandingIndicator(double percent) {
    final bool isUnderstandable = percent >= 70;
    final Color indicatorColor = isUnderstandable ? Colors.green : Colors.red;
    final IconData icon = isUnderstandable ? Icons.check_circle : Icons.cancel;
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: indicatorColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: indicatorColor.withOpacity(0.3),
          width: 1.5,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            color: indicatorColor,
            size: 20,
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              isUnderstandable 
                  ? "Dapat dipahami oleh native speaker"
                  : "Kurang dapat dipahami oleh native speaker",
              style: TextStyle(
                color: indicatorColor,
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  String _getAccuracyMessage(double percent) {
    if (percent >= 90) return "Excellent!";
    if (percent >= 80) return "Very Good!";
    if (percent >= 70) return "Good";
    if (percent >= 60) return "Keep Practicing";
    return "Needs Improvement";
  }

  Widget _buildComparisonTable() {
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey.shade300),
        borderRadius: BorderRadius.circular(8),
      ),
      height: 150,
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Wrap(
            spacing: 2,
            runSpacing: 6,
            alignment: WrapAlignment.center,
            children: phonemeComparison.map((result) {
              return _buildPhonemeComparison(result);
            }).toList(),
          ),
        ),
      ),
    );
  }

  Widget _buildPhonemeComparison(PhonemeResult result) {
    Color backgroundColor;
    switch (result.status) {
      case 'correct':
        backgroundColor = Colors.green.shade100;
        break;
      case 'similar':
        backgroundColor = Colors.blue.shade100;
        break;
      case 'incorrect':
        backgroundColor = Colors.red.shade100;
        break;
      case 'missing':
        backgroundColor = Colors.grey.shade100;
        break;
      case 'extra':
        backgroundColor = Colors.orange.shade100;
        break;
      default:
        backgroundColor = Colors.grey.shade100;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(4),
        border: Border.all(
          color: backgroundColor.withOpacity(0.7),
          width: 1,
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            result.target,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 18,
              color: result.status == 'missing' ? Colors.grey : Colors.black87,
            ),
          ),
          if (result.user != result.target && result.user != "-")
            Text(
              "→ ${result.user}",
              style: TextStyle(
                fontSize: 14,
                color: result.status == 'correct' ? Colors.green : Colors.red,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildLegend() {
    return Wrap(
      spacing: 8,
      runSpacing: 4,
      alignment: WrapAlignment.center,
      children: [
        _buildLegendItem("Correct", Colors.green.shade100),
        _buildLegendItem("Similar", Colors.blue.shade100),
        _buildLegendItem("Incorrect", Colors.red.shade100),
        _buildLegendItem("Missing", Colors.grey.shade100),
        _buildLegendItem("Extra", Colors.orange.shade100),
      ],
    );
  }

  Widget _buildLegendItem(String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: 4),
        Text(label, style: TextStyle(fontSize: 12)),
      ],
    );
  }
}