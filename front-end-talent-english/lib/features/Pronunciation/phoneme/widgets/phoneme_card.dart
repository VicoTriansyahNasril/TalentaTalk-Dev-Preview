import 'package:flutter/material.dart';

class PhonemeCard extends StatelessWidget {
  final String phoneme;
  final double progress;
  final VoidCallback onTap;

  const PhonemeCard({
    super.key,
    required this.phoneme,
    required this.progress,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Card(
        color: Colors.blue,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(phoneme, style: TextStyle(fontSize: 24, color: Colors.white)),
            Text("${(progress * 100).toInt()}%", style: TextStyle(color: Colors.white)),
          ],
        ),
      ),
    );
  }
}
