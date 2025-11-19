import 'package:flutter/material.dart';
import 'animated_list_item.dart';

class StrengthsCard extends StatelessWidget {
  final List<String> strengths;

  const StrengthsCard({
    super.key,
    required this.strengths,
  });

  @override
  Widget build(BuildContext context) {
    if (strengths.isEmpty) return const SizedBox.shrink();

    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.green.shade50, Colors.teal.shade50],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.green.shade100),
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
                  color: Colors.green.shade100,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(Icons.check_circle, color: Colors.green.shade700, size: 24),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Text(
                  "Your Strengths",
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
          ...strengths.asMap().entries.map((entry) => 
            AnimatedListItem(
              text: entry.value,
              color: Colors.green,
              delay: entry.key * 100,
            )
          ),
        ],
      ),
    );
  }
}