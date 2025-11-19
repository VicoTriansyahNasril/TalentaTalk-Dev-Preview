import 'package:flutter_bloc/flutter_bloc.dart';
import '../repository/profile_repository.dart';
import 'profile_event.dart';
import 'profile_state.dart';



class ProfileBloc extends Bloc<ProfileEvent, ProfileState> {
  final ProfileRepository repository;

  ProfileBloc(this.repository) : super(ProfileInitial()) {
    on<LoadUserProfile>((event, emit) async {
      emit(ProfileLoading());
      try {
        final user = await repository.getUserProfile();
        emit(ProfileLoaded(user));
      } catch (e) {
        emit(ProfileError("Failed to load profile"));
      }
    });
  }
}
