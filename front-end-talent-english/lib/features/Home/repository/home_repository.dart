import '../models/home_summary.dart';
import '../service/home_service.dart';

class HomeRepository {
  final HomeService service;

  HomeRepository({required this.service});

  Future<HomeSummary> getSummary() => service.fetchHomeSummary();
}
