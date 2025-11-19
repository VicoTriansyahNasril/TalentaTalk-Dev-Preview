import 'package:flutter/material.dart';
import 'animated_list_item.dart';

class WeaknessesCard extends StatelessWidget {
  final List<String> weaknesses;

  const WeaknessesCard({
    super.key,
    required this.weaknesses,
  });

  @override
  Widget build(BuildContext context) {
    if (weaknesses.isEmpty) return const SizedBox.shrink();

    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.orange.shade50, Colors.amber.shade50],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.orange.shade100),
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
                  color: Colors.orange.shade100,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(Icons.trending_up, color: Colors.orange.shade700, size: 24),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Text(
                  "Areas for Improvement",
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
          ...weaknesses.asMap().entries.map((entry) => 
            AnimatedListItem(
              text: entry.value,
              color: Colors.orange,
              delay: entry.key * 100,
            )
          ),
        ],
      ),
    );
  }
}