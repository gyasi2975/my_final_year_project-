import 'dart:typed_data';
import 'package:image/image.dart' as img;

/// Renders a low-res Grad-CAM grid as a JET-colormap overlay on an X-ray image.
class HeatmapRenderer {
  static const int gridSize = 7;
  static const double overlayAlpha = 0.42;

  /// Blend heatmap grid (7×7, values 0–1) onto [imageBytes]. Returns PNG bytes.
  static Uint8List? renderOverlayPng({
    required Uint8List imageBytes,
    required List<double> heatmapGrid,
    double alpha = overlayAlpha,
  }) {
    if (heatmapGrid.length != gridSize * gridSize) return null;

    final decoded = img.decodeImage(imageBytes);
    if (decoded == null) return null;

    final width = decoded.width;
    final height = decoded.height;
    final out = img.Image.from(decoded);

    for (int y = 0; y < height; y++) {
      for (int x = 0; x < width; x++) {
        final gx = x / width * gridSize;
        final gy = y / height * gridSize;
        final value = _bilinearSample(heatmapGrid, gx, gy);
        if (value <= 0.08) continue;

        final jet = _jetColor(value);
        final base = decoded.getPixel(x, y);
        final r = _blendChannel(base.r, jet[0], alpha * value);
        final g = _blendChannel(base.g, jet[1], alpha * value);
        final b = _blendChannel(base.b, jet[2], alpha * value);
        out.setPixelRgb(x, y, r, g, b);
      }
    }

    return Uint8List.fromList(img.encodePng(out));
  }

  static int _blendChannel num base, num overlay, double alpha) {
    return (base * (1 - alpha) + overlay * alpha).round().clamp(0, 255);
  }

  static double _bilinearSample(List<double> grid, double x, double y) {
    final x0 = x.floor().clamp(0, gridSize - 1);
    final y0 = y.floor().clamp(0, gridSize - 1);
    final x1 = (x0 + 1).clamp(0, gridSize - 1);
    final y1 = (y0 + 1).clamp(0, gridSize - 1);
    final tx = x - x0;
    final ty = y - y0;

    final v00 = grid[y0 * gridSize + x0];
    final v10 = grid[y0 * gridSize + x1];
    final v01 = grid[y1 * gridSize + x0];
    final v11 = grid[y1 * gridSize + x1];

    final top = v00 * (1 - tx) + v10 * tx;
    final bottom = v01 * (1 - tx) + v11 * tx;
    return top * (1 - ty) + bottom * ty;
  }

  /// OpenCV JET colormap approximation.
  static List<int> _jetColor(double t) {
    t = t.clamp(0.0, 1.0);
    final r = (1.5 - (4 * (t - 0.75).abs())).clamp(0.0, 1.0);
    final g = (1.5 - (4 * (t - 0.5).abs())).clamp(0.0, 1.0);
    final b = (1.5 - (4 * (t - 0.25).abs())).clamp(0.0, 1.0);
    return [(r * 255).round(), (g * 255).round(), (b * 255).round()];
  }

  static List<double> flattenHeatmapOutput(dynamic output) {
    final grid = List<double>.filled(gridSize * gridSize, 0);
    try {
      final batch = output[0] as List;
      for (int y = 0; y < gridSize; y++) {
        for (int x = 0; x < gridSize; x++) {
          final cell = batch[y][x];
          final value = cell is List ? cell[0] : cell;
          grid[y * gridSize + x] = (value as num).toDouble().clamp(0.0, 1.0);
        }
      }
    } catch (_) {}
    return grid;
  }
}
