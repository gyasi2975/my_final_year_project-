import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Medical disclaimer (doc 3.10.2): educational/decision support only; matches app design system.
class DisclaimerBanner extends StatelessWidget {
  const DisclaimerBanner({super.key});

  static const String _text =
      'This app is for educational and decision support only. It is not a replacement '
      'for professional medical diagnosis. Always seek a qualified healthcare professional '
      'for final diagnosis and treatment. Do not rely on this app for self-diagnosis or '
      'treatment without clinical consultation.';

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: AppTheme.warning.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.warning.withOpacity(0.3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.info_outline_rounded, size: 22, color: AppTheme.warning),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              _text,
              style: TextStyle(
                fontSize: 12,
                color: AppTheme.textSecondary,
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
