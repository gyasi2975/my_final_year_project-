import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../services/heatmap_renderer.dart';

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

Widget resultHeatmapImage({
  required String imagePath,
  required List<double> heatmapGrid,
  double height = 280,
}) {
  return FutureBuilder<Uint8List?>(
    future: _loadOverlay(imagePath, heatmapGrid),
    builder: (context, snapshot) {
      if (snapshot.connectionState != ConnectionState.done) {
        return SizedBox(
          height: height,
          child: const Center(child: CircularProgressIndicator(strokeWidth: 2)),
        );
      }
      final bytes = snapshot.data;
      if (bytes == null) return resultImage(imagePath, height: height);
      return Image.memory(
        bytes,
        fit: BoxFit.contain,
        height: height,
        errorBuilder: (_, __, ___) => resultImage(imagePath, height: height),
      );
    },
  );
}

Future<Uint8List?> _loadOverlay(String path, List<double> heatmapGrid) async {
  try {
    final file = File(path);
    if (!file.existsSync()) return null;
    final bytes = await file.readAsBytes();
    return HeatmapRenderer.renderOverlayPng(
      imageBytes: bytes,
      heatmapGrid: heatmapGrid,
    );
  } catch (_) {
    return null;
  }
}
