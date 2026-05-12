import 'dart:io';
import 'package:flutter/material.dart';

Widget resultImage(String path, {double height = 280}) {
  return Image.file(
    File(path),
    fit: BoxFit.contain,
    height: height,
    errorBuilder: (_, __, ___) => Container(
      height: height,
      color: Colors.grey[300],
      child: const Center(child: Icon(Icons.broken_image, size: 48)),
    ),
  );
}
