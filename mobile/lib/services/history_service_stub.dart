import '../models/history_entry.dart';
import '../models/inference_result.dart';

/// Stub for platforms where file-based history is not available (e.g. web).
class HistoryService {
  Future<List<HistoryEntry>> getEntries() async => [];

  Future<bool> saveEntry({
    required String sourceImagePath,
    required InferenceResult result,
  }) async => false;

  Future<bool> deleteEntry(String id) async => false;

  Future<void> init() async {}
}
