import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'bloc/material_list_bloc.dart';
import 'bloc/material_list_event.dart';
import 'bloc/material_list_state.dart';
import 'widget/material_item_widget.dart';
import 'repository/material_repository.dart';
import 'service/material_service.dart';
import '../../../../core/constants.dart';

class ExamMaterialScreen extends StatelessWidget {
  final List<String> phonemes;
  
  const ExamMaterialScreen({super.key, required this.phonemes});

  @override
  Widget build(BuildContext context) {
    print('Phonemes: ${phonemes.join(', ')}');
    
    final service = MaterialService(baseUrl: Env.baseUrl);
    final repository = MaterialRepository(service);

    return BlocProvider(
      create: (_) => ExamMaterialBloc(repository)..add(LoadMultipleMaterials(phonemes)),
      child: Scaffold(
        appBar: AppBar(
          title: Text('List Materi - ${phonemes.map((p) => '/$p/').join(' vs ')}'),
        ),
        body: BlocBuilder<ExamMaterialBloc, ExamMaterialState>(
          builder: (context, state) {
            if (state is ExamMaterialLoading) {
              return const Center(child: CircularProgressIndicator());
            } else if (state is ExamMaterialLoaded) {
              return ListView.builder(
                itemCount: state.materials.length,
                itemBuilder: (context, index) {
                  return MaterialItemWidget(material: state.materials[index],examNumber: index + 1,);
                },
              );
            } else if (state is MaterialEmpty) {
              return const Center(child: Text('No materials found.'));
            } else if (state is ExamMaterialError) {
              return Center(child: Text(state.message));
            }
            return const SizedBox();
          },
        ),
      ),
    );
  }
}