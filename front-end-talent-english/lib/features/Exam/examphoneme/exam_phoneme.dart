import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'data/similar_phoneme_pairs.dart';
import 'model/similar_phoneme_pair.dart';

class ExamPhonemeScreen extends StatelessWidget {
  const ExamPhonemeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        backgroundColor: const Color(0xFFF5F7FE),
        appBar: AppBar(
          title: const Text(
            'Exam Phoneme Categories',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w600,
              color: Colors.black87,
            ),
          ),
          backgroundColor: Colors.white,
          elevation: 0,
          iconTheme: const IconThemeData(color: Colors.black87),
          bottom: TabBar(
            tabs: const [
              Tab(text: 'Vowels'),
              Tab(text: 'Consonants'),
            ],
            labelColor: Colors.blue[700],
            unselectedLabelColor: Colors.grey[600],
            indicatorColor: Colors.blue[700],
            labelStyle: const TextStyle(fontWeight: FontWeight.w600),
          ),
        ),
        body: TabBarView(
          children: [
            _buildPhonemeList(vowelPairs, context),
            _buildPhonemeList(consonantPairs, context),
          ],
        ),
      ),
    );
  }

  Widget _buildPhonemeList(List<SimilarPhonemePair> pairs, BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: pairs.length,
      itemBuilder: (context, index) {
        final pair = pairs[index];

        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          child: Material(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            elevation: 2,
            shadowColor: Colors.black.withOpacity(0.1),
            child: InkWell(
              onTap: () {
                print('Navigating to exam with phonemes: ${pair.phonemes.join(', ')}');
                context.pushNamed(
                  'exam_material',
                  queryParameters: {
                    'phonemes': pair.phonemes.join(','),
                  },
                );
              },
              borderRadius: BorderRadius.circular(16),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          "Phoneme Pair",
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                            color: Colors.grey[600],
                          ),
                        ),
                        const Spacer(),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [Colors.orange[100]!, Colors.orange[50]!],
                            ),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                Icons.quiz_outlined,
                                size: 16,
                                color: Colors.orange[700],
                              ),
                              const SizedBox(width: 6),
                              Text(
                                'EXAM',
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.orange[700],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    _buildPhonemeRow(pair),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildPhonemeRow(SimilarPhonemePair pair) {
    List<Widget> phonemeBoxes = [];
    
    for (int i = 0; i < pair.phonemes.length; i++) {
      phonemeBoxes.add(_phonemeBox(pair.phonemes[i], pair.examples[i]));
      
      if (i < pair.phonemes.length - 1) {
        phonemeBoxes.add(const SizedBox(width: 12));
        phonemeBoxes.add(
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.blue[50],
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.compare_arrows,
              size: 20,
              color: Colors.blue[600],
            ),
          ),
        );
        phonemeBoxes.add(const SizedBox(width: 12));
      }
    }

    return Row(
      children: phonemeBoxes,
    );
  }

  Widget _phonemeBox(String phoneme, String example) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
        decoration: BoxDecoration(
          color: Colors.blue[50],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.blue[100]!, width: 1),
        ),
        child: Column(
          children: [
            Text(
              "/$phoneme/",
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.blue[700],
              ),
            ),
            const SizedBox(height: 6),
            Text(
              example,
              style: const TextStyle(
                fontSize: 16,
                color: Colors.black87,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
