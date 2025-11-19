import 'package:flutter/material.dart';
import '../model/user_profile_model.dart';

class ProgressStatsWidget extends StatelessWidget {
  final UserProfileModel user;

  const ProgressStatsWidget({super.key, required this.user});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Text(
              "",
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Color(0xFF333333),
              ),
            ),
          ),
          const SizedBox(height: 8),
          _buildProgressCards(),
        ],
      ),
    );
  }

  Widget _buildProgressCards() {
    return Column(
      children: [
        _buildCard(
          title: "Learning Score",
          icon: Icons.school,
          color: const Color(0xFF4CAF50),
          items: [
            _buildProgressItem(
              label: "Pretest score",
              value: user.pretestScore,
              color: const Color(0xFF4CAF50),
            ),
            _buildProgressItem(
              label: "Highest score",
              value: user.highestExam,
              color: const Color(0xFF4CAF50),
            ),
          ],
        ),

        const SizedBox(height: 16),

        _buildCard(
          title: "Pronunciation",
          icon: Icons.record_voice_over,
          color: const Color(0xFF2196F3),
          items: [
            _buildProgressItem(
              label: "Average Pronunciation score",
              value: user.averagePronunciation,
              color: const Color(0xFF2196F3),
            ),
          ],
        ),

        const SizedBox(height: 16),

        _buildCard(
          title: "Conversation",
          icon: Icons.forum,
          color: const Color(0xFFFF9800),
          items: [
            _buildProgressItem(
              label: "Average WPM",
              value: user.averageWPMConversation,
              color: const Color(0xFFFF9800),
              isWPM: true,
            ),
          ],
        ),

        const SizedBox(height: 16),

        _buildCard(
          title: "Interview",
          icon: Icons.mic,
          color: const Color(0xFF9C27B0),
          items: [
            _buildProgressItem(
              label: "Average WPM",
              value: user.averageWPMInterview,
              color: const Color(0xFF9C27B0),
              isWPM: true,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildCard({
    required String title,
    required IconData icon,
    required Color color,
    required List<Widget> items,
  }) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    icon,
                    color: color,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  title,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                    color: color,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...items,
          ],
        ),
      ),
    );
  }

  Widget _buildProgressItem({
    required String label,
    required int value,
    required Color color,
    bool isWPM = false,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: const TextStyle(
                fontSize: 14,
                color: Color(0xFF666666),
              ),
            ),
            Text(
              isWPM ? "$value WPM" : "$value%",
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: Color(0xFF333333),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: value / 100,
            backgroundColor: color.withOpacity(0.1),
            minHeight: 8,
            valueColor: AlwaysStoppedAnimation<Color>(color),
          ),
        ),
        const SizedBox(height: 8),
      ],
    );
  }
}