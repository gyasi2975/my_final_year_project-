import 'package:flutter/material.dart';
import '../models/history_entry.dart';
import '../models/inference_result.dart';
import '../theme/app_theme.dart';
import '../theme/app_ui.dart';
import '../services/history_service_stub.dart' if (dart.library.io) '../services/history_service_io.dart';
import '../widgets/disclaimer_banner.dart';
import '../widgets/result_image_web.dart' if (dart.library.io) '../widgets/result_image_io.dart';
import 'result_screen.dart';

/// History tab: "Recent analyses" list with cards matching the design system.
class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<HistoryEntry> _entries = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final service = HistoryService();
      await service.init();
      final list = await service.getEntries();
      list.sort((a, b) => b.date.compareTo(a.date));
      if (mounted) {
        setState(() {
          _entries = list;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surface,
      body: Column(
        children: [
          _buildHeader(context),
          Expanded(child: _buildBody(context)),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(AppUI.horizontalPadding, 48, AppUI.horizontalPadding, 32),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
        ),
        borderRadius: BorderRadius.only(
          bottomLeft: Radius.circular(32),
          bottomRight: Radius.circular(32),
        ),
      ),
      child: SafeArea(
        bottom: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Recent analyses',
              style: const TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.w700,
                color: Colors.white,
                letterSpacing: -0.5,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Tap to view full result',
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w400,
                color: Colors.white.withOpacity(0.9),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBody(BuildContext context) {
    if (_loading) {
      return Center(
        child: CircularProgressIndicator(
          color: AppTheme.primaryStart,
        ),
      );
    }
    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline_rounded, size: 56, color: AppTheme.error),
              const SizedBox(height: 16),
              Text(
                _error!,
                textAlign: TextAlign.center,
                style: TextStyle(color: AppTheme.error, fontSize: 14),
              ),
            ],
          ),
        ),
      );
    }
    if (_entries.isEmpty) {
      return SingleChildScrollView(
        padding: const EdgeInsets.all(AppUI.horizontalPadding),
        child: Column(
          children: [
            const SizedBox(height: 48),
            Container(
              padding: const EdgeInsets.all(32),
              decoration: BoxDecoration(
                color: AppTheme.cardBg,
                borderRadius: BorderRadius.circular(AppUI.radiusCard),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.06),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                children: [
                  Icon(Icons.history_rounded, size: 64, color: AppTheme.textSecondary),
                  const SizedBox(height: 20),
                  Text(
                    'No saved analyses yet',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w700,
                          color: AppTheme.textPrimary,
                        ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Run an analysis from Home and tap "Save to history" to see it here.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 14,
                      color: AppTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            const DisclaimerBanner(),
          ],
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: _load,
      color: AppTheme.primaryStart,
      child: ListView.builder(
        padding: const EdgeInsets.fromLTRB(AppUI.horizontalPadding, 24, AppUI.horizontalPadding, 100),
        itemCount: _entries.length,
        itemBuilder: (context, index) {
          final e = _entries[index];
          return _HistoryTile(
            entry: e,
            onTap: () => _openResult(context, e),
            onDelete: () => _deleteAndRefresh(e.id),
          );
        },
      ),
    );
  }

  void _openResult(BuildContext context, HistoryEntry e) {
    final result = InferenceResult(
      bodyPartName: e.bodyPartName,
      hasFracture: e.hasFracture,
      fractureConfidence: e.fractureConfidence,
      fractureTypeName: e.fractureTypeName,
      unsuitableReason: e.unsuitableReason,
    );
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => ResultScreen(
          imagePath: e.imagePath,
          result: result,
          fromHistory: true,
          entryId: e.id,
          onDeleted: _load,
        ),
      ),
    );
  }

  Future<void> _deleteAndRefresh(String id) async {
    final service = HistoryService();
    await service.init();
    await service.deleteEntry(id);
    if (mounted) _load();
  }
}

class _HistoryTile extends StatelessWidget {
  final HistoryEntry entry;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  const _HistoryTile({required this.entry, required this.onTap, required this.onDelete});

  @override
  Widget build(BuildContext context) {
    final dateStr = '${entry.date.day}/${entry.date.month}/${entry.date.year} · ${entry.date.hour}:${entry.date.minute.toString().padLeft(2, '0')}';
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: AppTheme.cardBg,
        borderRadius: BorderRadius.circular(AppUI.radiusCard),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.06),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(AppUI.radiusCard),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(AppUI.radiusSmall),
                  child: SizedBox(
                    width: 72,
                    height: 72,
                    child: resultImage(entry.imagePath, height: 72),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        entry.bodyPartName,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: AppTheme.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        entry.hasFracture ? 'Fracture: ${entry.fractureTypeName}' : 'No fracture',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w500,
                          color: entry.hasFracture ? AppTheme.warning : AppTheme.success,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        dateStr,
                        style: TextStyle(
                          fontSize: 12,
                          color: AppTheme.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  onPressed: onDelete,
                  icon: const Icon(Icons.delete_outline_rounded),
                  color: AppTheme.textSecondary,
                  tooltip: 'Delete',
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
