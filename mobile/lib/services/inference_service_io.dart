import 'dart:io';
import 'dart:typed_data';
import 'package:image_picker/image_picker.dart';
import 'package:tflite_flutter/tflite_flutter.dart';
import 'package:image/image.dart' as img;
import '../models/inference_result.dart';

/// Offline inference using TensorFlow Lite (Windows, Android, iOS only — not web).
class InferenceService {
  Interpreter? _interpreter;
  static const String _modelPath = 'assets/bone_fracture.tflite';

  final List<String> bodyParts = [
    'elbow', 'finger', 'forearm', 'hand', 'humerus', 'shoulder', 'wrist',
  ];
  final List<String> fractureTypes = ['simple', 'comminuted', 'greenstick'];

  Future<void> loadModel() async {
    try {
      _interpreter = await Interpreter.fromAsset(_modelPath);
    } catch (e) {
      _interpreter = null;
      rethrow;
    }
  }

  Future<InferenceResult> runInference(String imagePath) async {
    if (_interpreter == null) await loadModel();
    if (_interpreter == null) return InferenceResult.placeholder;

    // Load bytes via XFile so content:// and cache paths work on Android
    Uint8List? imageBytes;
    try {
      final xFile = XFile(imagePath);
      imageBytes = await xFile.readAsBytes();
    } catch (_) {
      try {
        final file = File(imagePath);
        if (file.existsSync()) imageBytes = file.readAsBytesSync();
      } catch (_) {}
    }
    if (imageBytes == null || imageBytes.isEmpty) return InferenceResult.placeholder;

    final input = _decodeResizeNormalize(imageBytes);
    if (input == null) {
      return const InferenceResult(
        bodyPartName: 'Unknown',
        hasFracture: false,
        fractureConfidence: 0.0,
        fractureTypeName: '—',
        unsuitableReason:
            'Could not decode the image. Try JPEG or PNG from your gallery.',
      );
    }
    final inputBytes = Uint8List.view(
      input.buffer,
      input.offsetInBytes,
      input.lengthInBytes,
    );

    final bodyPartOut = List.generate(1, (_) => List.filled(bodyParts.length, 0.0));
    final fractureOut = List.generate(1, (_) => List.filled(1, 0.0));
    final fractureTypeOut = List.generate(1, (_) => List.filled(fractureTypes.length, 0.0));

    try {
      _interpreter!.runForMultipleInputs(
        [inputBytes],
        {0: bodyPartOut, 1: fractureOut, 2: fractureTypeOut},
      );
    } catch (e) {
      return InferenceResult.placeholder;
    }

    final bodyProbs = bodyPartOut[0].cast<num>().map((e) => e.toDouble()).toList();
    final bodyIdx = _argmax(bodyProbs);
    final bodyMaxProb = bodyProbs[bodyIdx];
    final fractureProb = (fractureOut[0][0] as num).toDouble();
    final typeIdx = _argmax(
      fractureTypeOut[0].cast<num>().map((e) => e.toDouble()).toList(),
    );

    // Require confident anatomy before trusting the fracture head. Unrelated
    // photos often get spurious fracture activations while body logits stay flat.
    const double anatomyMinProb = 0.50;
    const double anatomyMinMargin = 0.11;
    const double fracturePositiveThreshold = 0.58;

    final sorted = [...bodyProbs]..sort();
    final secondLargest =
        sorted.length >= 2 ? sorted[sorted.length - 2] : 0.0;
    final margin = bodyMaxProb - secondLargest;
    final anatomyEligible =
        bodyMaxProb >= anatomyMinProb && margin >= anatomyMinMargin;

    if (!anatomyEligible) {
      final modelHintedFracture = fractureProb >= 0.42;
      return InferenceResult(
        bodyPartName: 'Unknown',
        hasFracture: false,
        fractureConfidence: fractureProb,
        fractureTypeName: '—',
        unsuitableReason: modelHintedFracture
            ? 'The image does not match a confident limb X-ray, so no fracture is reported. Use a standard clinical extremity X-ray to reduce false alarms.'
            : 'Could not confidently match a supported region (elbow, finger, forearm, hand, humerus, shoulder, wrist). Use a clear extremity X-ray.',
      );
    }

    final bodyName = bodyParts[bodyIdx.clamp(0, bodyParts.length - 1)];

    return InferenceResult(
      bodyPartName: bodyName,
      hasFracture: fractureProb >= fracturePositiveThreshold,
      fractureConfidence: fractureProb,
      fractureTypeName: fractureTypes[typeIdx.clamp(0, fractureTypes.length - 1)],
    );
  }

  static const int _inputSize = 224;
  static const int _inputLen = 1 * _inputSize * _inputSize * 3;

  Float32List? _decodeResizeNormalize(Uint8List bytes) {
    try {
      final decoded = img.decodeImage(bytes);
      if (decoded == null) return null;
      final resized = img.copyResize(decoded, width: _inputSize, height: _inputSize);
      final out = Float32List(_inputLen);
      for (int y = 0; y < _inputSize; y++) {
        for (int x = 0; x < _inputSize; x++) {
          final p = resized.getPixel(x, y);
          final i = (y * _inputSize + x) * 3;
          out[i] = p.r / 255.0;
          out[i + 1] = p.g / 255.0;
          out[i + 2] = p.b / 255.0;
        }
      }
      return out;
    } catch (_) {
      return null;
    }
  }

  int _argmax(List list) {
    if (list.isEmpty) return 0;
    int idx = 0;
    double max = (list[0] as num).toDouble();
    for (int i = 1; i < list.length; i++) {
      final v = (list[i] as num).toDouble();
      if (v > max) {
        max = v;
        idx = i;
      }
    }
    return idx;
  }
}
