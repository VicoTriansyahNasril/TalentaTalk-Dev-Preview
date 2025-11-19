abstract class AuthState {}

class AuthInitial extends AuthState {}

class AuthLoading extends AuthState {}

class AuthAuthenticated extends AuthState {
  final String token;

  AuthAuthenticated({required this.token});
}

class AuthUnauthenticated extends AuthState {}

class AuthError extends AuthState {
  final String message;

  AuthError({required this.message});
}

class AuthOnboardingRequired extends AuthState {
  final String token;

  AuthOnboardingRequired({
    required this.token,
  });
}

class AuthTokenExpired extends AuthState {}