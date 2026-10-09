import 'dart:io';
import 'dart:typed_data';
import 'package:image_picker/image_picker.dart';
import 'package:tflite_flutter/tflite_flutter.dart';
import 'package:image/image.dart' as img;
import '../models/inference_result.dart';
import 'heatmap_renderer.dart';

/// Offline inference using TensorFlow Lite (Windows, Android, iOS only — not web).
class InferenceService {
  Interpreter? _interpreter;
  Interpreter? _validityInterpreter;
  Interpreter? _heatmapInterpreter;

  static const String _modelPath = 'assets/bone_fracture.tflite';
  static const String _validityPath = 'assets/xray_validity.tflite';
  static const String _heatmapPath = 'assets/fracture_heatmap.tflite';
  static const String modelVersion = '2026-08-heatmap';

  /// Minimum probability that image is a supported extremity X-ray.
  /// Retrained validity model outputs unrelated images below ~0.03.
  static const double relatedMinProb = 0.30;

  int? _bodyPartOutputIndex;
  int? _fractureOutputIndex;
  int? _fractureTypeOutputIndex;

  final List<String> bodyParts = [
    'elbow', 'finger', 'forearm', 'hand', 'humerus', 'shoulder', 'wrist',
  ];
  final List<String> fractureTypes = ['simple', 'comminuted', 'greenstick'];

  Future<void> loadModel() async {
    try {
      _interpreter = await Interpreter.fromAsset(_modelPath);
      _resolveOutputIndices();
      try {
        _validityInterpreter = await Interpreter.fromAsset(_validityPath);
      } catch (_) {
        _validityInterpreter = null;
      }
      try {
        _heatmapInterpreter = await Interpreter.fromAsset(_heatmapPath);
      } catch (_) {
        _heatmapInterpreter = null;
      }
    } catch (e) {
      _interpreter = null;
      _validityInterpreter = null;
      _heatmapInterpreter = null;
      rethrow;
    }
  }

  void _resolveOutputIndices() {
    final interpreter = _interpreter;
    if (interpreter == null) return;

    _bodyPartOutputIndex = null;
    _fractureOutputIndex = null;
    _fractureTypeOutputIndex = null;

    for (var i = 0; i < interpreter.getOutputTensors().length; i++) {
      final shape = interpreter.getOutputTensor(i).shape;
      if (shape.length == 2 && shape[1] == bodyParts.length) {
        _bodyPartOutputIndex = i;
      } else if (shape.length == 2 && shape[1] == 1) {
        _fractureOutputIndex = i;
      } else if (shape.length == 2 && shape[1] == fractureTypes.length) {
        _fractureTypeOutputIndex = i;
      }
    }

    if (_bodyPartOutputIndex == null ||
        _fractureOutputIndex == null ||
        _fractureTypeOutputIndex == null) {
      throw StateError('Unexpected TFLite output layout for $_modelPath');
    }
  }

  Future<InferenceResult> runInference(String imagePath) async {
    if (_interpreter == null) await loadModel();
    if (_interpreter == null) return InferenceResult.placeholder;

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

    final relatedProb = _predictRelated(inputBytes);
    if (relatedProb != null && relatedProb < relatedMinProb) {
      return InferenceResult(
        bodyPartName: 'Unrelated',
        hasFracture: false,
        fractureConfidence: 0.0,
        fractureTypeName: '—',
        unsuitableReason:
            'This image was detected as unrelated to supported upper-extremity X-rays '
            '(chest, photos, or other non-limb images). Use a clear elbow, wrist, hand, '
            'finger, forearm, humerus, or shoulder X-ray.',
        bodyPartConfidence: relatedProb,
      );
    }

    final bodyPartOut = List.generate(1, (_) => List.filled(bodyParts.length, 0.0));
    final fractureOut = List.generate(1, (_) => List.filled(1, 0.0));
    final fractureTypeOut = List.generate(1, (_) => List.filled(fractureTypes.length, 0.0));

    try {
      _interpreter!.runForMultipleInputs(
        [inputBytes],
        {
          _bodyPartOutputIndex!: bodyPartOut,
          _fractureOutputIndex!: fractureOut,
          _fractureTypeOutputIndex!: fractureTypeOut,
        },
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

    final sorted = [...bodyProbs]..sort();
    final secondLargest =
        sorted.length >= 2 ? sorted[sorted.length - 2] : 0.0;
    final margin = bodyMaxProb - secondLargest;

    const double anatomyMinProb = 0.55;
    const double anatomyMinMargin = 0.18;
    const double fractureThreshold = 0.60;
    const double highFractureProb = 0.75;
    const double highFractureMinBodyProb = 0.72;
    const double highFractureMinMargin = 0.25;

    final anatomyEligible =
        bodyMaxProb >= anatomyMinProb && margin >= anatomyMinMargin;
    final fractureAnatomyMismatch = fractureProb >= 0.65 &&
        (bodyMaxProb < 0.50 || margin < 0.12);
    final highFractureWithoutEvidence = fractureProb >= highFractureProb &&
        (bodyMaxProb < highFractureMinBodyProb ||
            margin < highFractureMinMargin);

    if (!anatomyEligible ||
        fractureAnatomyMismatch ||
        highFractureWithoutEvidence) {
      return InferenceResult(
        bodyPartName: 'Unknown',
        hasFracture: false,
        fractureConfidence: fractureProb,
        fractureTypeName: '—',
        unsuitableReason:
            'This image is not a supported upper-extremity X-ray view. '
            'Chest, spine, pelvis, and full-torso radiographs are not supported.',
      );
    }

    final bodyName = bodyParts[bodyIdx.clamp(0, bodyParts.length - 1)];
    final hasFracture = fractureProb >= fractureThreshold;
    List<double>? heatmapGrid;
    if (hasFracture) {
      heatmapGrid = _predictHeatmap(inputBytes);
    }

    return InferenceResult(
      bodyPartName: bodyName,
      hasFracture: hasFracture,
      fractureConfidence: fractureProb,
      fractureTypeName: fractureTypes[typeIdx.clamp(0, fractureTypes.length - 1)],
      bodyPartConfidence: bodyMaxProb,
      heatmapGrid: heatmapGrid,
    );
  }

  List<double>? _predictHeatmap(Uint8List inputBytes) {
    final heatmap = _heatmapInterpreter;
    if (heatmap == null) return null;
    final out = List.generate(
      1,
      (_) => List.generate(
        HeatmapRenderer.gridSize,
        (_) => List.generate(
          HeatmapRenderer.gridSize,
          (_) => List.filled(1, 0.0),
        ),
      ),
    );
    try {
      heatmap.run(inputBytes, out);
      return HeatmapRenderer.flattenHeatmapOutput(out);
    } catch (_) {
      return null;
    }
  }

  double? _predictRelated(Uint8List inputBytes) {
    final validity = _validityInterpreter;
    if (validity == null) return null;
    final out = List.generate(1, (_) => List.filled(1, 0.0));
    try {
      validity.run(inputBytes, out);
      return (out[0][0] as num).toDouble();
    } catch (_) {
      return null;
    }
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
