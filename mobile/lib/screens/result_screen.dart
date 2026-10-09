import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/inference_result.dart';
import '../theme/app_theme.dart';
import '../theme/app_ui.dart';
import '../widgets/disclaimer_banner.dart';
import '../widgets/result_image_web.dart' if (dart.library.io) '../widgets/result_image_io.dart';
import '../services/history_service_stub.dart' if (dart.library.io) '../services/history_service_io.dart';

/// Result screen: gradient header, image card, result cards, Save/Share/Delete in design system style.
class ResultScreen extends StatelessWidget {
  final String imagePath;
  final InferenceResult result;
  final bool fromHistory;
  final String? entryId;
  final VoidCallback? onDeleted;

  const ResultScreen({
    super.key,
    required this.imagePath,
    required this.result,
    this.fromHistory = false,
    this.entryId,
    this.onDeleted,
  });

  Future<void> _saveToHistory(BuildContext context) async {
    final service = HistoryService();
    await service.init();
    final ok = await service.saveEntry(sourceImagePath: imagePath, result: result);
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(ok ? 'Saved to history' : 'Could not save. Try choosing from gallery instead of camera.'),
        backgroundColor: ok ? AppTheme.success : null,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  Future<void> _share(BuildContext context) async {
    final String analysisLine = result.unsuitableReason != null
        ? 'Bone fracture analysis: ${result.bodyPartName}. Fracture not reported — ${result.unsuitableReason}'
        : 'Bone fracture analysis: ${result.bodyPartName}, '
            '${result.hasFracture ? "Fracture detected (${result.fractureTypeName})" : "No fracture"}.';
    final text =
        '$analysisLine Educational/decision support only. Seek a qualified healthcare professional for diagnosis.';
    try {
      await Clipboard.setData(ClipboardData(text: text));
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Result copied to clipboard. Paste to share.'),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Copy failed: $e'), behavior: SnackBarBehavior.floating),
        );
      }
    }
  }

  Future<void> _deleteFromHistory(BuildContext context) async {
    if (entryId == null) return;
    final service = HistoryService();
    await service.init();
    await service.deleteEntry(entryId!);
    if (context.mounted) {
      onDeleted?.call();
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surface,
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 120,
            pinned: true,
            elevation: 0,
            backgroundColor: AppTheme.primaryStart,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
                  ),
                ),
              ),
              title: const Text(
                'Analysis result',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 18,
                  color: Colors.white,
                ),
              ),
              centerTitle: true,
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(AppUI.horizontalPadding),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 16),
                  const DisclaimerBanner(),
                  if (result.unsuitableReason != null) ...[
                    const SizedBox(height: 14),
                    _EligibilityCallout(message: result.unsuitableReason!),
                  ],
                  const SizedBox(height: 20),
                  AppUI.contentCard(
                    child: _FractureImagePanel(
                      imagePath: imagePath,
                      result: result,
                    ),
                  ),
                  const SizedBox(height: 20),
                  _ResultCard(
                    title: 'Body part',
                    value: result.bodyPartName,
                    subtitle: result.bodyPartConfidence != null
                        ? 'Confidence: ${(result.bodyPartConfidence! * 100).toStringAsFixed(0)}%'
                        : null,
                    icon: Icons.accessibility_new_rounded,
                  ),
                  const SizedBox(height: 12),
                  _ResultCard(
                    title: result.unsuitableReason != null
                        ? 'Fracture assessment'
                        : 'Fracture detected',
                    value: result.unsuitableReason != null
                        ? 'Not assessed'
                        : (result.hasFracture ? 'Yes' : 'No'),
                    subtitle: result.unsuitableReason != null
                        ? 'Shown only for confident limb X-rays'
                        : (result.hasFracture
                            ? 'Confidence: ${(result.fractureConfidence * 100).toStringAsFixed(0)}%'
                            : null),
                    icon: result.unsuitableReason != null
                        ? Icons.info_outline_rounded
                        : (result.hasFracture
                            ? Icons.warning_amber_rounded
                            : Icons.check_circle_rounded),
                    valueColor: result.unsuitableReason != null
                        ? AppTheme.primaryStart
                        : (result.hasFracture ? AppTheme.warning : AppTheme.success),
                  ),
                  if (result.hasFracture) ...[
                    const SizedBox(height: 12),
                    _ResultCard(
                      title: 'Fracture type',
                      value: result.fractureTypeName,
                      icon: Icons.medical_information_rounded,
                    ),
                  ],
                  const SizedBox(height: 16),
                  Text(
                    result.hasFracture && result.heatmapGrid != null
                        ? 'Grad-CAM heat map highlights regions that influenced the fracture prediction. Toggle to compare with the original X-ray.'
                        : result.hasFracture
                            ? 'Fracture detected. Heat map unavailable for this scan.'
                            : 'Heat map is shown when a fracture is detected.',
                    style: TextStyle(
                      fontSize: 12,
                      fontStyle: FontStyle.italic,
                      color: AppTheme.textSecondary,
                    ),
                  ),
                  const SizedBox(height: 28),
                  Row(
                    children: [
                      if (!fromHistory)
                        Expanded(
                          child: _GradientButton(
                            label: 'Save to history',
                            icon: Icons.save_rounded,
                            onPressed: () => _saveToHistory(context),
                          ),
                        ),
                      if (!fromHistory) const SizedBox(width: 12),
                      Expanded(
                        child: _OutlinedActionButton(
                          label: 'Share',
                          icon: Icons.share_rounded,
                          onPressed: () => _share(context),
                        ),
                      ),
                      if (fromHistory) ...[
                        const SizedBox(width: 12),
                        Expanded(
                          child: _OutlinedActionButton(
                            label: 'Delete',
                            icon: Icons.delete_outline_rounded,
                            onPressed: () => _deleteFromHistory(context),
                            isDestructive: true,
                          ),
                        ),
                      ],
                    ],
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: () => Navigator.of(context).pop(),
                      icon: const Icon(Icons.add_a_photo_rounded, size: 20),
                      label: const Text('New analysis'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        foregroundColor: AppTheme.primaryStart,
                        side: BorderSide(color: AppTheme.primaryStart),
                      ),
                    ),
                  ),
                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _FractureImagePanel extends StatefulWidget {
  final String imagePath;
  final InferenceResult result;

  const _FractureImagePanel({
    required this.imagePath,
    required this.result,
  });

  @override
  State<_FractureImagePanel> createState() => _FractureImagePanelState();
}

class _FractureImagePanelState extends State<_FractureImagePanel> {
  bool _showHeatmap = true;

  @override
  Widget build(BuildContext context) {
    final hasHeatmap =
        widget.result.hasFracture && widget.result.heatmapGrid != null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (hasHeatmap)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: SegmentedButton<bool>(
              segments: const [
                ButtonSegment(
                  value: true,
                  label: Text('Heat map'),
                  icon: Icon(Icons.local_fire_department_rounded, size: 18),
                ),
                ButtonSegment(
                  value: false,
                  label: Text('Original'),
                  icon: Icon(Icons.image_rounded, size: 18),
                ),
              ],
              selected: {_showHeatmap},
              onSelectionChanged: (values) {
                setState(() => _showHeatmap = values.first);
              },
            ),
          ),
        ClipRRect(
          borderRadius: BorderRadius.circular(AppUI.radiusSmall),
          child: _showHeatmap && hasHeatmap
              ? resultHeatmapImage(
                  imagePath: widget.imagePath,
                  heatmapGrid: widget.result.heatmapGrid!,
                )
              : resultImage(widget.imagePath),
        ),
      ],
    );
  }
}

class _EligibilityCallout extends StatelessWidget {
  final String message;

  const _EligibilityCallout({required this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.primaryStart.withOpacity(0.08),
        borderRadius: BorderRadius.circular(AppUI.radiusCard),
        border: Border.all(color: AppTheme.primaryStart.withOpacity(0.22)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.photo_filter_rounded, color: AppTheme.primaryStart, size: 22),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              message,
              style: TextStyle(
                fontSize: 13,
                height: 1.38,
                fontWeight: FontWeight.w500,
                color: AppTheme.textPrimary,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ResultCard extends StatelessWidget {
  final String title;
  final String value;
  final String? subtitle;
  final IconData icon;
  final Color? valueColor;

  const _ResultCard({
    required this.title,
    required this.value,
    this.subtitle,
    required this.icon,
    this.valueColor,
  });

  @override
  Widget build(BuildContext context) {
    return AppUI.contentCard(
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              gradient: AppTheme.softGradient,
              borderRadius: BorderRadius.circular(AppUI.radiusSmall),
            ),
            child: Icon(icon, size: 28, color: valueColor ?? AppTheme.primaryStart),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                    color: AppTheme.textSecondary,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w700,
                    color: valueColor ?? AppTheme.textPrimary,
                  ),
                ),
                if (subtitle != null)
                  Text(
                    subtitle!,
                    style: TextStyle(
                      fontSize: 13,
                      color: AppTheme.textSecondary,
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _GradientButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final VoidCallback onPressed;

  const _GradientButton({required this.label, required this.icon, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(AppUI.radiusButton),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            gradient: AppTheme.primaryGradient,
            borderRadius: BorderRadius.circular(AppUI.radiusButton),
            boxShadow: [
              BoxShadow(
                color: AppTheme.primaryStart.withOpacity(0.4),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 22, color: Colors.white),
              const SizedBox(width: 8),
              Text(
                label,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: Colors.white,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _OutlinedActionButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final VoidCallback onPressed;
  final bool isDestructive;

  const _OutlinedActionButton({
    required this.label,
    required this.icon,
    required this.onPressed,
    this.isDestructive = false,
  });

  @override
  Widget build(BuildContext context) {
    final color = isDestructive ? AppTheme.error : AppTheme.primaryStart;
    return OutlinedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: 20, color: color),
      label: Text(
        label,
        style: TextStyle(
          fontWeight: FontWeight.w600,
          color: color,
        ),
      ),
      style: OutlinedButton.styleFrom(
        padding: const EdgeInsets.symmetric(vertical: 16),
        side: BorderSide(color: color),
      ),
    );
  }
}
