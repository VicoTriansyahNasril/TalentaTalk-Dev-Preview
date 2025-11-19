import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'bloc/history_bloc.dart';
import 'bloc/history_event.dart';
import 'bloc/history_state.dart';
import 'pronunciation_tab.dart';
import 'conversation_tab.dart';
import 'interview_tab.dart';
import 'exam_tab.dart';

class TrainingHistoryScreen extends StatefulWidget {
  @override
  _TrainingHistoryScreenState createState() => _TrainingHistoryScreenState();
}

class _TrainingHistoryScreenState extends State<TrainingHistoryScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    context.read<TrainingHistoryBloc>().add(LoadTrainingHistory());
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Exercise History'),
        backgroundColor: Colors.blue.shade600,
        foregroundColor: Colors.white,
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          indicatorColor: Colors.white,
          isScrollable: true,
          tabs: [
            Tab(text: 'Pronunciation'),
            Tab(text: 'Conversation'),
            Tab(text: 'Interview'),
            Tab(text: 'Exam'),
          ],
        ),
      ),
      body: BlocBuilder<TrainingHistoryBloc, TrainingHistoryState>(
        builder: (context, state) {
          if (state is TrainingHistoryLoading) {
            return Center(child: CircularProgressIndicator());
          } else if (state is TrainingHistoryError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.error_outline, size: 64, color: Colors.red),
                  SizedBox(height: 16),
                  Text('Error: ${state.message}'),
                  SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      context.read<TrainingHistoryBloc>().add(LoadTrainingHistory());
                    },
                    child: Text('Retry'),
                  ),
                ],
              ),
            );
          } else if (state is TrainingHistoryLoaded) {
            return RefreshIndicator(
              onRefresh: () async {
                context.read<TrainingHistoryBloc>().add(RefreshTrainingHistory());
              },
              child: TabBarView(
                controller: _tabController,
                children: [
                  PronunciationTab(history: state.pronunciationHistory),
                  ConversationTab(history: state.conversationHistory),
                  InterviewTab(history: state.interviewHistory),
                  ExamTab(history: state.examHistory),
                ],
              ),
            );
          }
          return Center(child: Text('Tidak ada data'));
        },
      ),
    );
  }
}