import '../models/inference_result.dart';

/// Stub for web: TFLite (dart:ffi) is not available on web.
/// Run on Windows or Android for full offline inference.
class InferenceService {
  Future<void> loadModel() async {
    throw UnsupportedError(
      'ML inference is not available on web. Run the app on Windows or Android.',
    );
  }

  Future<InferenceResult> runInference(String imagePath) async {
    return InferenceResult.placeholder;
  }
}
