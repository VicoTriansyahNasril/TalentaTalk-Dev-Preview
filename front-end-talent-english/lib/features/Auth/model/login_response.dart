class LoginResponse {
  final String token;
  final String userId;
  final bool success;
  final String message;

  LoginResponse({
    required this.token,
    required this.userId,
    required this.success,
    required this.message,
  });

  factory LoginResponse.fromJson(Map<String, dynamic> json) {
    return LoginResponse(
      token: json['access_token'] ?? '',
      userId: json['user_id'] ?? '',
      success: json['success'] ?? false,
      message: json['message'] ?? '',
    );
  }
}