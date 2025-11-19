import 'package:flutter/material.dart';
import '../model/course_model.dart';
import '../../widgets/couse_card.dart';

class CourseCard extends StatelessWidget {
  final Course course;
  final VoidCallback onTap;

  const CourseCard({super.key, required this.course, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return UnifiedTrainingCard(
      title: course.title,
      subtitle: course.progress.isNotEmpty ? "Progress: ${course.progress}" : "Start your learning journey",
      icon: course.icon,
      color: course.color,
      onTap: onTap,
      progressText: course.progress.isNotEmpty ? course.progress : null,
    );
  }
}