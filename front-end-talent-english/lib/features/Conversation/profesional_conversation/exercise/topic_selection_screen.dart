import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../../../core/constants.dart';

class TopicSelectionScreen extends StatefulWidget {
  const TopicSelectionScreen({super.key});

  @override
  State<TopicSelectionScreen> createState() => _TopicSelectionScreenState();
}

class _TopicSelectionScreenState extends State<TopicSelectionScreen> {
  List<dynamic> topics = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchTopics();
  }

  Future<void> _fetchTopics() async {
    try {
      final res = await http.get(
        Uri.parse('${Env.baseUrl}/conversation/topics'),
      );
      if (res.statusCode == 200) {
        final body = jsonDecode(res.body);
        setState(() {
          topics = body['data']['topics'];
          isLoading = false;
        });
      } else {
        setState(() => isLoading = false);
      }
    } catch (e) {
      setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Select Conversation Topic")),
      body:
          isLoading
              ? const Center(child: CircularProgressIndicator())
              : topics.isEmpty
              ? const Center(child: Text("No topics available"))
              : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: topics.length,
                itemBuilder: (context, index) {
                  final topic = topics[index];
                  return Card(
                    elevation: 2,
                    margin: const EdgeInsets.only(bottom: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: ListTile(
                      contentPadding: const EdgeInsets.all(16),
                      leading: CircleAvatar(
                        backgroundColor: Colors.blue.shade100,
                        child: Text(
                          "${index + 1}",
                          style: TextStyle(color: Colors.blue.shade800),
                        ),
                      ),
                      title: Text(
                        topic['title'],
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      subtitle: Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: Text(topic['description']),
                      ),
                      trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                      onTap: () {
                        context.push('/conversation/${topic['id']}');
                      },
                    ),
                  );
                },
              ),
    );
  }
}
