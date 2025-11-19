import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'bloc/word_material_bloc.dart';
import 'bloc/word_material_event.dart';
import 'bloc/word_material_state.dart';
import 'widget/word_material_item_widget.dart';
import 'repository/word_material_repository.dart';
import 'service/word_material_service.dart';

class WordMaterialScreen extends StatelessWidget {
  final String phoneme;
  const WordMaterialScreen({super.key, required this.phoneme});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => WordMaterialBloc(
        WordMaterialRepository(service: WordMaterialService()),
      )..add(LoadWordMaterials(phoneme)),
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: Colors.white,
          title: const Text('Word Materials'),
        ),
        backgroundColor: Colors.white,
        body: BlocBuilder<WordMaterialBloc, WordMaterialState>(
          builder: (context, state) {
            if (state is WordMaterialLoading) {
              return const Center(child: CircularProgressIndicator());
            } else if (state is WordMaterialLoaded) {
              return ListView.builder(
                itemCount: state.words.length,
                itemBuilder: (context, index) {
                  return WordMaterialItemWidget(data: state.words[index]);
                },
              );
            }else if (state is WordMaterialEmpty) {
              return const Center(child: Text('No word materials found.'));
            } else if (state is WordMaterialError) {
              return Center(child: Text(state.message));
            }
            return const SizedBox();
          },
        ),
      ),
    );
  }
}
