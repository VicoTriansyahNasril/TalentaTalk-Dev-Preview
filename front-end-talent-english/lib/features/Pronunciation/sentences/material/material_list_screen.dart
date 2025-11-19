import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'bloc/material_list_bloc.dart';
import 'bloc/material_list_event.dart';
import 'bloc/material_list_state.dart';
import 'widget/material_item_widget.dart';
import 'repository/material_repository.dart';
import 'service/material_service.dart';
import '../../../../core/constants.dart';

class MaterialListScreen extends StatelessWidget {
  final List<String> phonemes;
  
  const MaterialListScreen({
    super.key, 
    required this.phonemes,
  });

  @override
  Widget build(BuildContext context) {
    print('Phonemes: ${phonemes.join(', ')}');
    final service = MaterialService(baseUrl: Env.baseUrl);
    final repository = MaterialRepository(service);

    return BlocProvider(
      create: (_) => MaterialListBloc(repository)..add(LoadMaterialsForPhonemes(phonemes)),
      child: Scaffold(
        appBar: AppBar(
          title: Text('Materi: ${phonemes.map((p) => '/$p/').join(' vs ')}'),
        ),
        body: BlocBuilder<MaterialListBloc, MaterialListState>(
          builder: (context, state) {
            if (state is MaterialListLoading) {
              return const Center(child: CircularProgressIndicator());
            } else if (state is MaterialListLoaded) {
              if (state.materials.isEmpty) {
                return const Center(child: Text('No materials found.'));
              }
              return ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: state.materials.length,
                itemBuilder: (context, index) {
                  return MaterialItemWidget(material: state.materials[index]);
                },
              );
            } else if (state is MaterialListError) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.error, size: 48, color: Colors.red),
                    const SizedBox(height: 16),
                    Text(
                      state.message,
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 16),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () {
                        context.read<MaterialListBloc>().add(LoadMaterialsForPhonemes(phonemes));
                      },
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              );
            }
            return const SizedBox();
          },
        ),
      ),
    );
  }
}
