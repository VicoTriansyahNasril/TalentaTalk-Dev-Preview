import '../model/user_profile_model.dart';
import '../service/profile_service.dart';

class ProfileRepository {
  final ProfileService _service = ProfileService();

  Future<UserProfileModel> getUserProfile() {
    return _service.fetchUserProfile();
  }
}