import 'package:flutter/material.dart';

class HighlightSegment {
  final String text;
  final bool isError;

  HighlightSegment(this.text, this.isError);
}

class HighlightedText extends StatelessWidget {
  final List<HighlightSegment> segments;

  const HighlightedText({super.key, required this.segments});

  @override
  Widget build(BuildContext context) {
    return RichText(
      text: TextSpan(
        children: segments.map((segment) {
          return TextSpan(
            text: segment.text,
            style: TextStyle(
              color: segment.isError ? Colors.red : Colors.green,
              fontWeight: segment.isError ? FontWeight.bold : FontWeight.normal,
              fontSize: 16,
            ),
          );
        }).toList(),
      ),
    );
  }
}
