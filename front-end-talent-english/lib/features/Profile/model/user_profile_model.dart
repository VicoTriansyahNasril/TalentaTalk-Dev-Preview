class UserProfileModel {
  final String name;
  final String jobTitle;
  final String email;
  final int lastTest;
  final int pretestScore;
  final int highestExam;
  final int averagePronunciation;
  final int averageWPMConversation;
  final int averageWPMInterview;

  final int phonemeCompleted;
  final int phonemeTotal;
  final int conversationCompleted;
  final int interviewCompleted;

  UserProfileModel({
    required this.name,
    required this.jobTitle,
    required this.email,
    required this.lastTest,
    required this.pretestScore,
    required this.highestExam,
    required this.averagePronunciation,
    required this.averageWPMConversation,
    required this.averageWPMInterview,
    required this.phonemeCompleted,
    required this.phonemeTotal,
    required this.conversationCompleted,
    required this.interviewCompleted,
  });

  factory UserProfileModel.fromJson(Map<String, dynamic> json) {
    final activity = json['activity'] ?? {};

    int safeInt(dynamic value) {
      if (value == null) return 0;
      if (value is int) return value;
      if (value is double) return value.toInt();
      return int.tryParse(value.toString()) ?? 0;
    }

    return UserProfileModel(
      name: json['name'] ?? '',
      jobTitle: json['jobTitle'] ?? '',
      email: json['email'] ?? '',
      lastTest: safeInt(json['lastTest']),
      pretestScore: safeInt(json['pretestScore']),
      highestExam: safeInt(json['highestExam']),
      averagePronunciation: safeInt(json['averagePronunciation']),
      averageWPMConversation: safeInt(json['averageWPMConversation']),
      averageWPMInterview: safeInt(json['averageWPMInterview']),
      phonemeCompleted: safeInt(activity['phonemeCompleted']),
      phonemeTotal: safeInt(activity['phonemeTotal']),
      conversationCompleted: safeInt(activity['conversationCompleted']),
      interviewCompleted: safeInt(activity['interviewCompleted']),
    );
  }

}
