import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:io';

import 'bloc/conversation_bloc.dart';
import 'bloc/conversation_event.dart';
import 'bloc/conversation_state.dart';
import 'model/chat_message.dart';
import 'widget/conversation_report.dart';
import '../../interview/service/transcribe_service.dart';

class ConversationScreen extends StatefulWidget {
  const ConversationScreen({Key? key}) : super(key: key);

  @override
  State<ConversationScreen> createState() => _ConversationScreenState();
}

class _ConversationScreenState extends State<ConversationScreen> {
  final AudioRecorder _audioRecorder = AudioRecorder();
  final TranscriptionService _transcriptionService = TranscriptionService();
  bool _isRecording = false;
  String _recordingPath = '';
  late DateTime _conversationStartTime;
  DateTime? _recordingStartTime;
  bool _isProcessing = false;
  
  String _permanentRecordingPath = '';

  @override
  void initState() {
    super.initState();
    _conversationStartTime = DateTime.now();
    context.read<ConversationBloc>().add(StartConversationEvent());
    _requestPermissions();
    _initializePermanentPath();
  }

  @override
  void dispose() {
    _audioRecorder.dispose();
    super.dispose();
  }

  Future<void> _initializePermanentPath() async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      _permanentRecordingPath = '${directory.path}/transcribe.m4a';
      print('Permanent recording path initialized: $_permanentRecordingPath');
    } catch (e) {
      print('Error initializing permanent path: $e');
      final directory = await getTemporaryDirectory();
      _permanentRecordingPath = '${directory.path}/transcribe.m4a';
    }
  }

  Future<void> _requestPermissions() async {
    final status = await Permission.microphone.request();
    if (status != PermissionStatus.granted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Microphone permission is required for recording'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    final hours = twoDigits(duration.inHours);
    final minutes = twoDigits(duration.inMinutes.remainder(60));
    final seconds = twoDigits(duration.inSeconds.remainder(60));
    
    if (duration.inHours > 0) {
      return '$hours:$minutes:$seconds';
    } else {
      return '$minutes:$seconds';
    }
  }

  Future<void> _startRecording() async {
    try {
      final hasPermission = await _audioRecorder.hasPermission();
      if (!hasPermission) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Microphone permission denied'),
            backgroundColor: Colors.red,
          ),
        );
        return;
      }

      if (_permanentRecordingPath.isEmpty) {
        await _initializePermanentPath();
      }

      final existingFile = File(_permanentRecordingPath);
      if (existingFile.existsSync()) {
        await existingFile.delete();
        print('Previous recording file deleted for overwrite');
      }

      _recordingPath = _permanentRecordingPath;

      const config = RecordConfig(
        encoder: AudioEncoder.aacLc,
        bitRate: 128000,
        sampleRate: 44100,
      );

      await _audioRecorder.start(config, path: _recordingPath);

      setState(() {
        _isRecording = true;
        _recordingStartTime = DateTime.now();
      });

      print('Recording started: $_recordingPath');
      print('Recording start time: $_recordingStartTime');
    } catch (e) {
      print('Error starting recording: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to start recording: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _stopRecording() async {
    try {
      final path = await _audioRecorder.stop();
      final recordingEndTime = DateTime.now();
      
      setState(() {
        _isRecording = false;
        _isProcessing = true;
      });

      print('Recording stopped. Path from stop(): $path');
      print('Recording path variable: $_recordingPath');
      print('Recording end time: $recordingEndTime');

      final finalPath = path ?? _recordingPath;
      
      if (finalPath.isNotEmpty && _recordingStartTime != null) {
        final file = File(finalPath);
        print('File exists: ${file.existsSync()}');
        print('File path: ${file.path}');
        
        if (file.existsSync()) {
          await Future.delayed(const Duration(milliseconds: 100));
          
          final recordingDuration = recordingEndTime.difference(_recordingStartTime!);
          final formattedDuration = _formatDuration(recordingDuration);
          
          print('Actual recording duration: $formattedDuration');
          print('Recording file will be kept at: ${file.path}');
          
          await _transcribeAndSend(finalPath, formattedDuration);
        } else {
          throw Exception('Recording file not found at: $finalPath');
        }
      } else {
        throw Exception('Recording path is empty or start time not recorded');
      }
    } catch (e) {
      print('Error stopping recording: $e');
      setState(() {
        _isRecording = false;
        _isProcessing = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to stop recording: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _transcribeAndSend(String audioPath, String recordingDuration) async {
    try {
      print('Transcribing audio from: $audioPath');
      print('Recording duration: $recordingDuration');
      
      final file = File(audioPath);
      if (!file.existsSync()) {
        throw Exception('Audio file not found at: $audioPath');
      }

      final fileSize = await file.length();
      print('Audio file size: $fileSize bytes');

      if (fileSize == 0) {
        throw Exception('Audio file is empty');
      }

      final transcribedText = await _transcriptionService.transcribeAudio(audioPath);
      
      if (transcribedText != null && transcribedText.trim().isNotEmpty) {
        print('Transcribed text: $transcribedText');
        print('Recording file saved permanently at: $audioPath');
        
        context.read<ConversationBloc>().add(
          SendAudioMessageEvent(audioPath, recordingDuration),
        );
      } else {
        print('No transcription received or empty transcription');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('No speech detected in the recording'),
            backgroundColor: Colors.orange,
            duration: Duration(seconds: 2),
          ),
        );
      }

      
      setState(() {
        _isProcessing = false;
        _recordingStartTime = null;
      });
      
    } catch (e) {
      print('Error in transcribeAndSend: $e');
      setState(() {
        _isProcessing = false;
        _recordingStartTime = null;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to process audio: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _clearRecordingFile() async {
    try {
      final file = File(_permanentRecordingPath);
      if (file.existsSync()) {
        await file.delete();
        print('Recording file cleared: $_permanentRecordingPath');
      }
    } catch (e) {
      print('Error clearing recording file: $e');
    }
  }

  bool _hasRecordingFile() {
    if (_permanentRecordingPath.isEmpty) return false;
    return File(_permanentRecordingPath).existsSync();
  }

  void _handleFinish() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: Row(
          children: [
            Icon(Icons.help_outline, color: Colors.orange.shade600),
            const SizedBox(width: 8),
            const Text('End Conversation?'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Are you sure you want to end the conversation and generate the report?',
              style: TextStyle(fontSize: 15),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Cancel',
              style: TextStyle(color: Colors.grey.shade600),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<ConversationBloc>().add(FinishConversationEvent());
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue.shade600,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
            child: const Text('Yes, End'),
          ),
        ],
      ),
    );
  }

  void _handleRestart() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: Row(
          children: [
            Icon(Icons.refresh, color: Colors.green.shade600),
            const SizedBox(width: 8),
            const Text('Start New Conversation?'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'This will start a new conversation session. Your current report will be cleared.',
              style: TextStyle(fontSize: 15),
            ),
            if (_hasRecordingFile()) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.orange.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.warning_outlined, 
                         color: Colors.orange.shade600, size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Your previous recording will be overwritten on next record',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.orange.shade700,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Cancel',
              style: TextStyle(color: Colors.grey.shade600),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _conversationStartTime = DateTime.now();
              context.read<ConversationBloc>().add(StartConversationEvent());
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green.shade600,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
            child: const Text('Start New'),
          ),
        ],
      ),
    );
  }

  Widget _buildChatBubble(ChatMessage message) {
    return Align(
      alignment: message.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.8,
        ),
        decoration: BoxDecoration(
          color: message.isUser 
              ? Colors.blue.shade600 
              : Colors.grey.shade100,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: message.isUser 
                ? const Radius.circular(16) 
                : const Radius.circular(4),
            bottomRight: message.isUser 
                ? const Radius.circular(4) 
                : const Radius.circular(16),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Text(
          message.message,
          style: TextStyle(
            color: message.isUser ? Colors.white : Colors.black87,
            fontSize: 15,
            height: 1.4,
          ),
        ),
      ),
    );
  }

  Widget _buildRecordingIndicator() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: const BoxDecoration(
              color: Colors.red,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Recording...',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.red.shade700,
                  ),
                ),
                Text(
                  'Tap the microphone to stop recording',
                  style: TextStyle(
                    color: Colors.red.shade600,
                    fontSize: 12,
                  ),
                ),
                if (_recordingStartTime != null)
                  StreamBuilder(
                    stream: Stream.periodic(const Duration(seconds: 1)),
                    builder: (context, snapshot) {
                      final duration = DateTime.now().difference(_recordingStartTime!);
                      return Text(
                        'Duration: ${_formatDuration(duration)}',
                        style: TextStyle(
                          color: Colors.red.shade600,
                          fontSize: 11,
                          fontWeight: FontWeight.w500,
                        ),
                      );
                    },
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProcessingIndicator() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.orange.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.orange.shade200),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(Colors.orange.shade600),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'Processing audio...',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.orange.shade700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMicrophoneButton() {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            _isRecording 
                ? "Recording... (tap to stop)" 
                : _isProcessing
                    ? "Processing audio..."
                    : "Tap the microphone to record",
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey.shade600,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          GestureDetector(
            onTap: _isProcessing 
                ? null 
                : _isRecording 
                    ? _stopRecording 
                    : _startRecording,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: _isProcessing
                    ? Colors.orange.shade600
                    : _isRecording 
                        ? Colors.red.shade600 
                        : Colors.blue.shade600,
                boxShadow: [
                  BoxShadow(
                    color: (_isProcessing 
                        ? Colors.orange
                        : _isRecording 
                            ? Colors.red 
                            : Colors.blue).withOpacity(0.3),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: _isProcessing
                  ? const Padding(
                      padding: EdgeInsets.all(20),
                      child: CircularProgressIndicator(
                        color: Colors.white,
                        strokeWidth: 3,
                      ),
                    )
                  : Icon(
                      _isRecording ? Icons.stop : Icons.mic,
                      color: Colors.white,
                      size: 32,
                    ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        title: const Text(
          'Professional Conversation',
          style: TextStyle(color: Colors.black87),
        ),
        actions: [
          BlocBuilder<ConversationBloc, ConversationState>(
            builder: (context, state) {
              if (state is ConversationFinished) {
                return IconButton(
                  icon: const Icon(Icons.refresh, color: Colors.green),
                  onPressed: _handleRestart,
                  tooltip: 'Start New Conversation',
                );
              } else if (state is ConversationInProgress) {
                return IconButton(
                  icon: const Icon(Icons.check_circle, color: Colors.blue),
                  onPressed: _handleFinish,
                  tooltip: 'End Conversation',
                );
              }
              return const SizedBox.shrink();
            },
          ),
        ],
      ),
      body: BlocBuilder<ConversationBloc, ConversationState>(
        builder: (context, state) {
          if (state is ConversationLoading) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.blue.shade600),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Processing conversation...',
                    style: TextStyle(
                      color: Colors.grey.shade600,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            );
          } else if (state is ConversationError) {
            return Center(
              child: Container(
                margin: const EdgeInsets.all(24),
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.red.shade200),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.error_outline,
                      color: Colors.red.shade600,
                      size: 48,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Something went wrong',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.red.shade700,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      state.message,
                      style: TextStyle(
                        color: Colors.red.shade600,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            );
          } else if (state is ConversationFinished) {
            return ConversationReportWidget(
              report: state.report,
              saveStatus: state.saveStatus,
            );
          } else if (state is ConversationInProgress) {
            return Column(
              children: [
                Expanded(
                  child: state.messages.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.chat_bubble_outline,
                                size: 64,
                                color: Colors.grey.shade400,
                              ),
                              const SizedBox(height: 16),
                              Text(
                                'Start your conversation',
                                style: TextStyle(
                                  fontSize: 18,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Tap the microphone below to begin recording',
                                style: TextStyle(
                                  color: Colors.grey.shade500,
                                ),
                              ),
                            ],
                          ),
                        )
                      : ListView.builder(
                          itemCount: state.messages.length,
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          itemBuilder: (context, index) {
                            return _buildChatBubble(state.messages[index]);
                          },
                        ),
                ),
                if (_isRecording) _buildRecordingIndicator(),
                if (_isProcessing) _buildProcessingIndicator(),
                _buildMicrophoneButton(),
              ],
            );
          }

          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.chat,
                  size: 64,
                  color: Colors.grey.shade400,
                ),
                const SizedBox(height: 16),
                Text(
                  'Ready to start conversation',
                  style: TextStyle(
                    fontSize: 18,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}