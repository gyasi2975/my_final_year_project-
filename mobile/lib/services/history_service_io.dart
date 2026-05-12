import 'dart:convert';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import '../models/history_entry.dart';
import '../models/inference_result.dart';

/// File-based history on IO platforms (Android, iOS, Windows).
class HistoryService {
  static const String _dirName = 'bone_fracture_app';
  static const String _imagesDir = 'images';
  static const String _historyFile = 'history.json';

  Directory? _baseDir;
  File? _historyFileRef;

  Future<void> init() async {
    final appDir = await getApplicationDocumentsDirectory();
    _baseDir = Directory('${appDir.path}/$_dirName');
    await _baseDir!.create(recursive: true);
    final imagesDir = Directory('${_baseDir!.path}/$_imagesDir');
    await imagesDir.create(recursive: true);
    _historyFileRef = File('${_baseDir!.path}/$_historyFile');
  }

  Future<List<HistoryEntry>> getEntries() async {
    await init();
    if (_historyFileRef == null || !_historyFileRef!.existsSync()) return [];
    try {
      final content = await _historyFileRef!.readAsString();
      final list = jsonDecode(content) as List<dynamic>;
      return list.map((e) => HistoryEntry.fromJson(e as Map<String, dynamic>)).toList();
    } catch (_) {
      return [];
    }
  }

  Future<bool> saveEntry({
    required String sourceImagePath,
    required InferenceResult result,
  }) async {
    await init();
    if (_baseDir == null || _historyFileRef == null) return false;
    try {
      // Use XFile so content:// URIs and cache paths both work on Android
      final xFile = XFile(sourceImagePath);
      final bytes = await xFile.readAsBytes();
      if (bytes.isEmpty) return false;
      final id = '${DateTime.now().millisecondsSinceEpoch}';
      final ext = sourceImagePath.split('.').last.toLowerCase();
      final safeExt = (ext == 'jpg' || ext == 'jpeg' || ext == 'png') ? ext : 'jpg';
      final destPath = '${_baseDir!.path}/$_imagesDir/$id.$safeExt';
      await File(destPath).writeAsBytes(bytes);

      final entry = HistoryEntry(
        id: id,
        imagePath: destPath,
        bodyPartName: result.bodyPartName,
        hasFracture: result.hasFracture,
        fractureTypeName: result.fractureTypeName,
        fractureConfidence: result.fractureConfidence,
        date: DateTime.now(),
        unsuitableReason: result.unsuitableReason,
      );

      final entries = await getEntries();
      entries.insert(0, entry);
      await _writeEntries(entries);
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> deleteEntry(String id) async {
    await init();
    final entries = await getEntries();
    final found = entries.where((e) => e.id == id).toList();
    if (found.isEmpty) return false;
    final entry = found.first;
    try {
      final f = File(entry.imagePath);
      if (f.existsSync()) f.deleteSync();
    } catch (_) {}
    entries.removeWhere((e) => e.id == id);
    await _writeEntries(entries);
    return true;
  }

  Future<void> _writeEntries(List<HistoryEntry> entries) async {
    if (_historyFileRef == null) return;
    final list = entries.map((e) => e.toJson()).toList();
    await _historyFileRef!.writeAsString(jsonEncode(list));
  }
}
