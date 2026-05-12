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

  const InferenceResult({
    required this.bodyPartName,
    required this.hasFracture,
    required this.fractureConfidence,
    required this.fractureTypeName,
    this.unsuitableReason,
  });

  static InferenceResult get placeholder => const InferenceResult(
        bodyPartName: 'Unknown',
        hasFracture: false,
        fractureConfidence: 0.0,
        fractureTypeName: '—',
      );
}
