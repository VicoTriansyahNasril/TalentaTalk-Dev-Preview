import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:go_router/go_router.dart';
import 'home_event.dart';
import 'home_state.dart';
import '../models/user_activity.dart';
import '../repository/home_repository.dart';
import '../service/home_service.dart';

class HomeBloc extends Bloc<HomeEvent, HomeState> {
  final HomeRepository repository;

  HomeBloc() : repository = HomeRepository(service: HomeService()), super(HomeInitial()) {
    on<LoadHomeData>((event, emit) async {
      emit(HomeLoading());
      try {
        final summary = await repository.getSummary();
        emit(HomeLoaded(
          activities: summary.activities,
          lastScore: summary.lastScore,
          totalTests: summary.totalTests,
          accuracy: summary.accuracy,
          lastTestDaysAgo: summary.lastTestDaysAgo,
          userName: summary.userName,
          learningStreak: summary.learningStreak,
          quickStats: summary.quickStats,
          examSummary: summary.examSummary,
        ));
      } catch (e) {
        print('HomeBloc Error: $e');
        
        if (_isTokenExpiredError(e.toString())) {
          await _handleTokenExpiry();
          emit(HomeTokenExpired());
        } else {
          emit(HomeError(message: e.toString()));
        }
      }
    });
  }

  bool _isTokenExpiredError(String errorMessage) {
    return errorMessage.contains('403') || 
           errorMessage.contains('Signature has expired') ||
           errorMessage.contains('Could not validate token') ||
           errorMessage.contains('token') && errorMessage.contains('expired');
  }

  Future<void> _handleTokenExpiry() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('token');
      await prefs.remove('userId');
      print('Token and userId cleared due to expiry');
    } catch (e) {
      print('Error clearing expired token: $e');
    }
  }
}