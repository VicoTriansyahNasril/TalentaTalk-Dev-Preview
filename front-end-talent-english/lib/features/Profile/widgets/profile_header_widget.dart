import 'package:flutter/material.dart'; 
import '../model/user_profile_model.dart'; 
 
class ProfileHeaderWidget extends StatelessWidget { 
  final UserProfileModel user; 
 
  const ProfileHeaderWidget({super.key, required this.user}); 
 
  @override 
  Widget build(BuildContext context) { 
    return Container( 
      margin: const EdgeInsets.all(16), 
      decoration: BoxDecoration( 
        gradient: const LinearGradient( 
          begin: Alignment.topLeft, 
          end: Alignment.bottomRight, 
          colors: [Color(0xFF1976D2), Color(0xFF1565C0)],
        ), 
        borderRadius: BorderRadius.circular(16), 
        boxShadow: [ 
          BoxShadow( 
            color: Colors.blue.withOpacity(0.3), 
            blurRadius: 10, 
            offset: const Offset(0, 4), 
          ), 
        ], 
      ), 
      child: Column( 
        children: [ 
          const SizedBox(height: 24), 
          Container( 
            width: 100, 
            height: 100, 
            decoration: BoxDecoration( 
              shape: BoxShape.circle, 
              color: Colors.white, 
              border: Border.all(color: Colors.white, width: 3), 
              boxShadow: [ 
                BoxShadow( 
                  color: Colors.black.withOpacity(0.1), 
                  blurRadius: 8, 
                  offset: const Offset(0, 2), 
                ), 
              ], 
            ), 
            child: Center( 
              child: Text( 
                user.name.isNotEmpty ? user.name[0].toUpperCase() : '?', 
                style: const TextStyle( 
                  fontSize: 40, 
                  fontWeight: FontWeight.bold, 
                  color: Color(0xFF1976D2),
                ), 
              ), 
            ), 
          ), 
          const SizedBox(height: 16), 
          Text( 
            user.name, 
            style: const TextStyle( 
              fontSize: 24, 
              fontWeight: FontWeight.bold, 
              color: Colors.white, 
            ), 
          ), 
          const SizedBox(height: 4), 
          Text( 
            user.jobTitle, 
            style: const TextStyle( 
              fontSize: 16, 
              color: Colors.white, 
              fontWeight: FontWeight.w400, 
            ), 
          ), 
          const SizedBox(height: 16), 
          Padding( 
            padding: const EdgeInsets.symmetric(horizontal: 24), 
            child: Container( 
              padding: const EdgeInsets.all(16), 
              decoration: BoxDecoration( 
                color: Colors.white.withOpacity(0.15), 
                borderRadius: BorderRadius.circular(12), 
              ), 
              child: Column( 
                children: [ 
                  Row( 
                    children: [ 
                      const Icon(Icons.email, color: Colors.white70), 
                      const SizedBox(width: 8), 
                      Expanded( 
                        child: Text( 
                          user.email, 
                          style: const TextStyle(color: Colors.white), 
                        ), 
                      ), 
                    ], 
                  ), 
                  const SizedBox(height: 10), 
                  Row( 
                    children: [ 
                      const Icon(Icons.assessment, color: Colors.white70), 
                      const SizedBox(width: 8), 
                      Text( 
                        "Hasil tes terakhir: ${user.lastTest}", 
                        style: const TextStyle(color: Colors.white), 
                      ), 
                    ], 
                  ), 
                ], 
              ), 
            ), 
          ), 
          const SizedBox(height: 24), 
           
        ], 
      ), 
    ); 
  } 
}