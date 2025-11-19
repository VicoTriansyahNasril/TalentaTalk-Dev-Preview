import 'package:flutter/material.dart';

class OverallPerformanceCard extends StatelessWidget {
  final Map<String, dynamic> overallPerformance;

  const OverallPerformanceCard({
    super.key,
    required this.overallPerformance,
  });

  @override
  Widget build(BuildContext context) {
    if (overallPerformance.isEmpty) return const SizedBox.shrink();

    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.purple.shade50, Colors.indigo.shade50],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.purple.shade100),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.purple.shade100,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(Icons.assessment_outlined, color: Colors.purple.shade700, size: 24),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Text(
                  "Overall Performance",
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (overallPerformance['technical_knowledge'] != null)
            _buildEnhancedPerformanceRow("Technical Knowledge", 
              overallPerformance['technical_knowledge'], Icons.code),
          if (overallPerformance['communication_speed'] != null)
            _buildEnhancedPerformanceRow("Communication Speed", 
              overallPerformance['communication_speed'], Icons.speed),
          if (overallPerformance['grammar_usage'] != null)
            _buildEnhancedPerformanceRow("Grammar Usage", 
              overallPerformance['grammar_usage'], Icons.spellcheck),
          if (overallPerformance['recommendation'] != null) ...[
            const SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.lightbulb, color: Colors.blue.shade700),
                      const SizedBox(width: 8),
                      const Expanded(
                        child: Text(
                          "Recommendation",
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                            color: Colors.black87,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    overallPerformance['recommendation'],
                    style: const TextStyle(
                      height: 1.5,
                      fontSize: 15,
                      color: Colors.black87,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildEnhancedPerformanceRow(String label, String value, IconData icon) {
    Color valueColor = Colors.black87;
    Color bgColor = Colors.grey.shade100;
    
    if (value.toLowerCase().contains('poor')) {
      valueColor = Colors.red.shade700;
      bgColor = Colors.red.shade50;
    } else if (value.toLowerCase().contains('good') || value.toLowerCase().contains('excellent')) {
      valueColor = Colors.green.shade700;
      bgColor = Colors.green.shade50;
    } else if (value.toLowerCase().contains('average') || value.toLowerCase().contains('medium')) {
      valueColor = Colors.orange.shade700;
      bgColor = Colors.orange.shade50;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(icon, size: 20, color: Colors.purple.shade600),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  label,
                  style: const TextStyle(
                    fontWeight: FontWeight.w500,
                    fontSize: 15,
                    color: Colors.black87,
                  ),
                  overflow: TextOverflow.visible,
                  softWrap: true,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Align(
            alignment: Alignment.centerRight,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: bgColor,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                value,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: valueColor,
                  fontSize: 14,
                ),
                overflow: TextOverflow.visible,
                softWrap: true,
                textAlign: TextAlign.center,
              ),
            ),
          ),
        ],
      ),
    );
  }
}