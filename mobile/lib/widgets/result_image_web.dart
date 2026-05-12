import 'package:flutter/material.dart';

Widget resultImage(String path, {double height = 280}) {
  return Container(
    height: height,
    color: Colors.grey[300],
    child: Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.image, size: 48),
          const SizedBox(height: 8),
          Text('Image from picker', style: TextStyle(color: Colors.grey[600])),
        ],
      ),
    ),
  );
}
