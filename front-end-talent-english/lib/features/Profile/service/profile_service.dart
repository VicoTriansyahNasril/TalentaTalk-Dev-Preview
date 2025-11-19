import 'dart:convert';
import 'package:http/http.dart' as http;
import '../model/user_profile_model.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../core/constants.dart';

class ProfileService {
  final baseUrl = Env.baseUrl;

  Future<UserProfileModel> fetchUserProfile() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString("token");

    final response = await http.get(
      Uri.parse('$baseUrl/profile/summary'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return UserProfileModel.fromJson(data);
    } else {
      throw Exception('Failed to load profile: ${response.statusCode}');
    }
  }
}
