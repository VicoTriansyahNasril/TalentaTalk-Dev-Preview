abstract class TrainingHistoryEvent {}

class LoadTrainingHistory extends TrainingHistoryEvent {}

class RefreshTrainingHistory extends TrainingHistoryEvent {}

class FilterByDateRange extends TrainingHistoryEvent {
  final DateTime startDate;
  final DateTime endDate;

  FilterByDateRange({required this.startDate, required this.endDate});
}
