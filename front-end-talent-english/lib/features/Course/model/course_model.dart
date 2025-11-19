import 'package:flutter/material.dart';

class Course {
  final String title;
  final String progress;
  final Color color;
  final Icon icon;
  final String route;
  final String? description;
  final int totalDuration;

  Course({
    required this.title,
    required this.progress,
    required this.color,
    required this.icon,
    required this.route,
    this.description,
    this.totalDuration = 0,
  });
}