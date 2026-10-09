/// Result of offline inference: body part, fracture yes/no, fracture type.
/// Aligned with proposal expected outcomes.
class InferenceResult {
  final String bodyPartName;
  final bool hasFracture;
  final double fractureConfidence;
  final String fractureTypeName;

  /// When set, the image was not treated as a reliable limb X-ray for a
  /// fracture decision (reduces false positives on unrelated photos).
  final String? unsuitableReason;

  /// Confidence in the predicted body part (0–1), when anatomy checks pass.
  final double? bodyPartConfidence;

  /// Grad-CAM heatmap grid (7×7, values 0–1) when fracture is detected.
  final List<double>? heatmapGrid;

  const InferenceResult({
    required this.bodyPartName,
    required this.hasFracture,
    required this.fractureConfidence,
    required this.fractureTypeName,
    this.unsuitableReason,
    this.bodyPartConfidence,
    this.heatmapGrid,
  });

  static InferenceResult get placeholder => const InferenceResult(
        bodyPartName: 'Unknown',
        hasFracture: false,
        fractureConfidence: 0.0,
        fractureTypeName: '—',
      );
}
