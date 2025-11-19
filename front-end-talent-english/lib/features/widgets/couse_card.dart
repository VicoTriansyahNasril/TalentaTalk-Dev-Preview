import 'package:flutter/material.dart';
import 'package:percent_indicator/circular_percent_indicator.dart';

class UnifiedTrainingCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final Widget icon;
  final Color color;
  final VoidCallback onTap;
  final double? progress;
  final String? progressText;

  const UnifiedTrainingCard({
    super.key,
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.color,
    required this.onTap,
    this.progress,
    this.progressText,
  });

  double _getProgressPercentage() {
    if (progress != null) {
      return progress!;
    }
    
    if (progressText != null && progressText!.isNotEmpty) {
      final parts = progressText!.split('/');
      if (parts.length == 2) {
        try {
          final completed = double.parse(parts[0].trim());
          final total = double.parse(parts[1].trim());
          return completed / total;
        } catch (e) {
          return 0.0;
        }
      }
    }
    return 0.0;
  }

  @override
  Widget build(BuildContext context) {
    final progressPercentage = _getProgressPercentage();
    final hasProgress = progress != null || (progressText != null && progressText!.isNotEmpty);
    
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
      decoration: BoxDecoration(
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Card(
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        child: InkWell(
          borderRadius: BorderRadius.circular(20),
          onTap: onTap,
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  color,
                  color.withOpacity(0.8),
                ],
              ),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: IconTheme(
                          data: const IconThemeData(
                            color: Colors.white,
                            size: 28,
                          ),
                          child: icon,
                        ),
                      ),
                      if (hasProgress)
                        CircularPercentIndicator(
                          radius: 22.0,
                          lineWidth: 5.0,
                          percent: progressPercentage,
                          center: Text(
                            "${(progressPercentage * 100).toInt()}%",
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                          progressColor: Colors.white,
                          backgroundColor: Colors.white.withOpacity(0.2),
                        ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    subtitle,
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.9),
                      fontSize: 14,
                    ),
                  ),
                  if (hasProgress && progressText != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      "Progress: $progressText",
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.9),
                        fontSize: 14,
                      ),
                    ),
                  ],
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: onTap,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: color,
                      elevation: 0,
                      minimumSize: const Size(double.infinity, 45),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(15),
                      ),
                    ),
                    child: const Text(
                      "Start Learning",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}