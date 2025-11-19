import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../Auth/bloc/auth_bloc.dart';
import '../Auth/bloc/auth_event.dart';
import '../Auth/bloc/auth_state.dart';
import '../Auth/repository/auth_repository.dart';

class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => AuthBloc(AuthRepository())..add(CheckAuthStatusEvent()),
      child: const SplashView(),
    );
  }
}

class SplashView extends StatefulWidget {
  const SplashView({super.key});

  @override
  State<SplashView> createState() => _SplashViewState();
}

class _SplashViewState extends State<SplashView> {
  @override
  void initState() {
    super.initState();
    _initializeApp();
  }

  Future<void> _initializeApp() async {
    await Future.delayed(const Duration(seconds: 2));
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<AuthBloc, AuthState>(
      listener: (context, state) {
        // Navigate based on auth state
        if (state is AuthAuthenticated) {
          context.go('/home');
        } else if (state is AuthOnboardingRequired) {
          context.go('/onboarding');
        } else if (state is AuthUnauthenticated) {
          context.go('/login');
        } else if (state is AuthTokenExpired) {
          context.go('/login');
          
          Future.delayed(Duration.zero, () {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Your session has expired. Please login again.'),
                backgroundColor: Colors.orange,
              ),
            );
          });
        } else if (state is AuthError) {
          // On error, go to login
          context.go('/login');
        }
      },
      child: Scaffold(
        backgroundColor: Colors.white,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                height: 100,
                width: 100,
                decoration: BoxDecoration(
                  color: Colors.blue.shade100,
                  shape: BoxShape.circle,
                ),
                child: Center(
                  child: Icon(
                    Icons.chat_bubble_outline,
                    size: 50,
                    color: Colors.blue.shade700,
                  ),
                ),
              ),
              const SizedBox(height: 24),
              const Text(
                "TalentaTalk",
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 32),
              SizedBox(
                width: 40,
                height: 40,
                child: CircularProgressIndicator(
                  color: Colors.blue.shade400,
                  strokeWidth: 2,
                ),
              ),
              const SizedBox(height: 16),
              BlocBuilder<AuthBloc, AuthState>(
                builder: (context, state) {
                  if (state is AuthLoading) {
                    return const Text(
                      "Checking authentication...",
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey,
                      ),
                    );
                  } else if (state is AuthTokenExpired) {
                    return const Text(
                      "Session expired, redirecting to login...",
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.orange,
                      ),
                    );
                  } else if (state is AuthError) {
                    return Text(
                      "Error: ${state.message}",
                      style: const TextStyle(
                        fontSize: 14,
                        color: Colors.red,
                      ),
                    );
                  }
                  return const SizedBox.shrink();
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}