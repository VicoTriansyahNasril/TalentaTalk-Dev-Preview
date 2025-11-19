class OnboardingCheckResponse {
  final bool showOnboarding;
  
  OnboardingCheckResponse({
    required this.showOnboarding,
  });
  
  factory OnboardingCheckResponse.fromJson(Map<String, dynamic> json) {
    return OnboardingCheckResponse(
      showOnboarding: json['show_onboarding'] ?? false,
    );
  }
}