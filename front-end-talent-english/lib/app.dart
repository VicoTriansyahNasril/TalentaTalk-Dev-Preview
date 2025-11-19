import 'package:flutter/material.dart';
import 'route/app_router.dart';

class TalentaTalkApp extends StatelessWidget {
  const TalentaTalkApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      routerConfig: appRouter,
      debugShowCheckedModeBanner: false,
      theme: ThemeData(useMaterial3: true),
    );
  }
}
