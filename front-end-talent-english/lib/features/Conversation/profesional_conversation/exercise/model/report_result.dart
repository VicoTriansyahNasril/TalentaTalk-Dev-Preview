class ReportResult {
  final String userInput;
  final double wpm;
  final int confidence;
  final List<GrammarIssue> grammarIssues;

  ReportResult({
    required this.userInput,
    required this.wpm,
    required this.confidence,
    required this.grammarIssues,
  });

  factory ReportResult.fromJson(Map<String, dynamic> json) {
    final wpmInfo = json['wpm_confidence_info'] as String;
    
    // Extract WPM from the string using regex
    final wpmRegex = RegExp(r'WPM: (\d+\.\d+)');
    final wpmMatch = wpmRegex.firstMatch(wpmInfo);
    final wpm = wpmMatch != null 
        ? double.parse(wpmMatch.group(1) ?? '0.0') 
        : 0.0;
    
    // Extract confidence score from the string using regex
    final confidenceRegex = RegExp(r'Confidence Score: (\d+)');
    final confidenceMatch = confidenceRegex.firstMatch(wpmInfo);
    final confidence = confidenceMatch != null 
        ? int.parse(confidenceMatch.group(1) ?? '0') 
        : 0;
    
    // Parse grammar issues
    final List<dynamic> grammarIssuesJson = json['grammar_issues'] ?? [];
    final List<GrammarIssue> grammarIssues = grammarIssuesJson
        .map((issue) => GrammarIssue.fromJson(issue))
        .toList();
    
    return ReportResult(
      userInput: json['user_input'] ?? '',
      wpm: wpm,
      confidence: confidence,
      grammarIssues: grammarIssues,
    );
  }
}

class GrammarIssue {
  final String message;
  final List<String> suggestions;
  final String sentence;

  GrammarIssue({
    required this.message,
    required this.suggestions,
    required this.sentence,
  });

  factory GrammarIssue.fromJson(Map<String, dynamic> json) {
    final suggestions = (json['suggestions'] as List?)?.cast<String>() ?? [];
    
    return GrammarIssue(
      message: json['message'] ?? '',
      suggestions: suggestions,
      sentence: json['sentence'] ?? '',
    );
  }
}