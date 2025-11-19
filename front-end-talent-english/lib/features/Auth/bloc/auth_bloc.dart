import 'package:flutter_bloc/flutter_bloc.dart';
import '../repository/auth_repository.dart';
import 'auth_event.dart';
import 'auth_state.dart';
import 'package:shared_preferences/shared_preferences.dart';


class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository authRepository;

  AuthBloc(this.authRepository) : super(AuthInitial()) {
    on<LoginEvent>(_onLoginEvent);
    on<LogoutEvent>(_onLogoutEvent);
    on<CheckAuthStatusEvent>(_onCheckAuthStatusEvent);
  }

    Future<void> _onLoginEvent(
      LoginEvent event,
      Emitter<AuthState> emit,
    ) async {
      emit(AuthLoading());
      try {
        final loginResponse = await authRepository.login(
          email: event.email,
          password: event.password,
        );
        
        print('Login success: token=${loginResponse.token}, userId=${loginResponse.userId}');
        
        if (loginResponse.token.isNotEmpty) {
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('token', loginResponse.token);
          await prefs.setString('userId', loginResponse.userId);
          
          final savedToken = prefs.getString('token');
          final savedUserId = prefs.getString('userId');
          print('Saved token: $savedToken');
          print('Saved userId: $savedUserId');

          try {
            final onboardingResponse = await authRepository.checkOnboarding(
              token: loginResponse.token,
            );
            
            if (onboardingResponse.showOnboarding) {
              emit(AuthOnboardingRequired(
                token: loginResponse.token,
                
              ));
            } else {
              emit(AuthAuthenticated(
                token: loginResponse.token,
                
              ));
            }
          } catch (onboardingError) {
            print('Onboarding check error: $onboardingError');
            emit(AuthAuthenticated(
              token: loginResponse.token,
              
            ));
          }
        } else {
          emit(AuthError(message: 'Authentication failed'));
        }
      } catch (e) {
        emit(AuthError(message: e.toString()));
      }
    }

  Future<void> _onLogoutEvent(
    LogoutEvent event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('token');
      await prefs.remove('userId');

      emit(AuthUnauthenticated());
    } catch (e) {
      emit(AuthError(message: e.toString()));
    }
  }

  Future<void> _onCheckAuthStatusEvent(
    CheckAuthStatusEvent event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token');

      if (token != null && token.isNotEmpty) {
        try {
          final onboardingResponse = await authRepository.checkOnboarding(
            token: token,
          );
          
          if (onboardingResponse.showOnboarding) {
            emit(AuthOnboardingRequired(token: token));
          } else {
            emit(AuthAuthenticated(token: token));
          }
        } catch (onboardingError) {
          print('Onboarding check error on auth status: $onboardingError');
          
          if (_isTokenExpiredError(onboardingError.toString())) {
            print('Token expired, clearing credentials and redirecting to login');
            await prefs.remove('token');
            await prefs.remove('userId');
            emit(AuthTokenExpired());
          } else {
            emit(AuthAuthenticated(token: token));
          }
        }
      } else {
        emit(AuthUnauthenticated());
      }
    } catch (e) {
      emit(AuthError(message: e.toString()));
    }
  }

  bool _isTokenExpiredError(String errorMessage) {
    return errorMessage.contains('Could not validate token: Signature has expired') ||
           errorMessage.contains('403') ||
           errorMessage.contains('Signature has expired');
  }
}
