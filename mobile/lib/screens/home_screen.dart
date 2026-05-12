import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../theme/app_theme.dart';
import '../theme/app_ui.dart';
import '../services/inference_service_stub.dart' if (dart.library.io) '../services/inference_service_io.dart';
import '../widgets/disclaimer_banner.dart';
import 'result_screen.dart';

/// Home screen: gradient hero "Smarter Health Better You", stat cards, quick actions (Capture / Gallery).
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final InferenceService _inference = InferenceService();
  bool _modelLoaded = false;
  String? _loadError;

  @override
  void initState() {
    super.initState();
    _loadModel();
  }

  Future<void> _loadModel() async {
    setState(() {
      _modelLoaded = false;
      _loadError = null;
    });
    try {
      await _inference.loadModel();
      if (mounted) {
        setState(() => _modelLoaded = true);
      }
    } catch (e) {
      if (mounted) {
        setState(() => _loadError = e.toString());
      }
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(
      source: source,
      maxWidth: 1600,
      maxHeight: 1600,
      imageQuality: 92,
    );
    if (picked == null || !mounted) return;
    final imagePath = picked.path;
    if (!_modelLoaded) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Add bone_fracture.tflite to mobile/assets/ and run again.'),
            duration: Duration(seconds: 4),
          ),
        );
      }
      return;
    }
    final result = await _inference.runInference(imagePath);
    if (!mounted) return;
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => ResultScreen(
          imagePath: imagePath,
          result: result,
        ),
      ),
    );
  }

  String get _greeting {
    final h = DateTime.now().hour;
    if (h < 12) return 'Good morning';
    if (h < 17) return 'Good afternoon';
    return 'Good evening';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surface,
      body: Column(
        children: [
          AppUI.heroSection(
            title: 'Smarter Health\nBetter You',
            subtitle: 'AI-powered bone fracture detection from X-ray images',
            trailing: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  _greeting,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: Colors.white.withOpacity(0.9),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.medical_services_rounded, size: 18, color: Colors.white),
                      const SizedBox(width: 6),
                      Text(
                        'Health',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: AppUI.horizontalPadding),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      Expanded(
                        child: AppUI.statCard(
                          label: 'Model status',
                          value: _modelLoaded ? 'Ready' : (_loadError != null ? 'Error' : 'Loading…'),
                          icon: _modelLoaded ? Icons.check_circle_rounded : Icons.hourglass_empty_rounded,
                          iconColor: _modelLoaded ? AppTheme.success : AppTheme.textSecondary,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: AppUI.statCard(
                          label: 'Offline',
                          value: 'Yes',
                          icon: Icons.wifi_off_rounded,
                          iconColor: AppTheme.primaryStart,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 28),
                  AppUI.sectionHeader('Quick actions'),
                  const SizedBox(height: 8),
                  AppUI.primaryActionCard(
                    title: 'Capture X-ray',
                    subtitle: 'Take a new photo for analysis',
                    icon: Icons.camera_alt_rounded,
                    onTap: () => _pickImage(ImageSource.camera),
                    enabled: _modelLoaded,
                  ),
                  const SizedBox(height: 12),
                  AppUI.secondaryActionCard(
                    title: 'Choose from gallery',
                    subtitle: 'Select an existing X-ray image',
                    icon: Icons.photo_library_rounded,
                    onTap: () => _pickImage(ImageSource.gallery),
                    enabled: _modelLoaded,
                  ),
                  if (_loadError != null) ...[
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: AppTheme.error.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(AppUI.radiusSmall),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.error_outline_rounded, color: AppTheme.error, size: 24),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              _loadError!,
                              style: TextStyle(
                                fontSize: 13,
                                color: AppTheme.error,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                  const SizedBox(height: 24),
                  const DisclaimerBanner(),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
