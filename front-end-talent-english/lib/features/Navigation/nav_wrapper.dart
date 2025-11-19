import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../../widgets/bottom_nav_bar.dart';
import '../../widgets/app_bar.dart';
import '../../widgets/side_bar.dart';
import '../Auth/bloc/auth_bloc.dart';
import '../Auth/repository/auth_repository.dart';


class NavWrapper extends StatelessWidget {
  final Widget child;
  final int currentIndex;

  const NavWrapper({
    super.key,
    required this.child,
    required this.currentIndex,
  });

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => AuthBloc(AuthRepository()),
      child: Scaffold(
        appBar: const GlobalAppBar(),
        drawer: const AppSidebar(),
        body: child,
        bottomNavigationBar: BottomNavBar(currentIndex: currentIndex),
      ),
    );
  }
}