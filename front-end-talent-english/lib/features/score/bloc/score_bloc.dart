import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';
import '../widgets/highlighted_text.dart';
import '../models/score_result.dart';

part 'score_event.dart';
part 'score_state.dart';


class ScoreBloc extends Bloc<ScoreEvent, ScoreState> {
  ScoreBloc() : super(ScoreLoading()) {
    on<ScoreRequested>((event, emit) async {
    });

    on<ScoreRequestedFromResult>((event, emit) async {
      emit(ScoreLoading());

      try {
        final results = event.results;

        final averageScore = results.isNotEmpty
            ? results.map((r) => r.score).reduce((a, b) => a + b) / results.length
            : 0.0;

        final segments = results.map((r) => r.segments).toList();

        emit(ScoreLoaded(score: averageScore, segments: segments, results: results,));
      } catch (_) {
        emit(ScoreError("Gagal memuat skor"));
      }
    });
  }
}

