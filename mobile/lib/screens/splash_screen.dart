import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_shell.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

/// Aspect ratio of the abstract “imaging viewport” mark (no launcher bitmap).
const double _kMarkWidth = 112.0;
const double _kMarkHeight = 148.0;

class _SplashScreenState extends State<SplashScreen>
    with TickerProviderStateMixin {
  late final AnimationController _mainCtrl;
  late final AnimationController _floatCtrl;

  late final Animation<double> _markScale;
  late final Animation<double> _markOpacity;
  late final Animation<double> _markFramePulse;
  late final Animation<double> _scanPhase;

  late final Animation<Offset> _titleSlide;
  late final Animation<double> _titleOpacity;
  late final Animation<double> _taglineOpacity;

  late final Animation<double> _orb1Opacity;
  late final Animation<double> _orb2Opacity;

  late final Animation<double> _progressWidth;

  @override
  void initState() {
    super.initState();

    SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: Color(0xFF0B1020),
      systemNavigationBarIconBrightness: Brightness.light,
    ));

    _mainCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2800),
    );

    _floatCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 3800),
    )..repeat(reverse: true);

    _markScale = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween(begin: 0.88, end: 1.0)
            .chain(CurveTween(curve: Curves.easeOutCubic)),
        weight: 42,
      ),
      TweenSequenceItem(tween: ConstantTween(1.0), weight: 58),
    ]).animate(_mainCtrl);

    _markOpacity = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _mainCtrl,
        curve: const Interval(0.0, 0.24, curve: Curves.easeOut),
      ),
    );

    _markFramePulse = Tween<double>(begin: 0.35, end: 1.0).animate(
      CurvedAnimation(
        parent: _mainCtrl,
        curve: const Interval(0.0, 0.55, curve: Curves.easeOutCubic),
      ),
    );

    _scanPhase = CurvedAnimation(
      parent: _mainCtrl,
      curve: const Interval(0.12, 0.92, curve: Curves.easeInOutCubic),
    );

    _titleSlide = Tween<Offset>(
      begin: const Offset(0, 0.22),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _mainCtrl,
      curve: const Interval(0.30, 0.62, curve: Curves.easeOutCubic),
    ));

    _titleOpacity = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _mainCtrl,
        curve: const Interval(0.30, 0.58, curve: Curves.easeOut),
      ),
    );

    _taglineOpacity = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _mainCtrl,
        curve: const Interval(0.54, 0.78, curve: Curves.easeOut),
      ),
    );

    _orb1Opacity = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _mainCtrl,
        curve: const Interval(0.0, 0.38, curve: Curves.easeOut),
      ),
    );

    _orb2Opacity = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _mainCtrl,
        curve: const Interval(0.06, 0.48, curve: Curves.easeOut),
      ),
    );

    _progressWidth = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _mainCtrl,
        curve: const Interval(0.20, 0.97, curve: Curves.easeInOutCubic),
      ),
    );

    _mainCtrl.forward();

    Future.delayed(const Duration(milliseconds: 3400), () {
      if (mounted) _navigateToShell();
    });
  }

  void _navigateToShell() {
    SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      systemNavigationBarColor: Colors.white,
      systemNavigationBarIconBrightness: Brightness.dark,
    ));
    Navigator.of(context).pushReplacement(
      PageRouteBuilder(
        transitionDuration: const Duration(milliseconds: 640),
        pageBuilder: (_, __, ___) => const AppShell(),
        transitionsBuilder: (_, anim, __, child) {
          return FadeTransition(
            opacity: CurvedAnimation(parent: anim, curve: Curves.easeOut),
            child: SlideTransition(
              position: Tween<Offset>(
                begin: const Offset(0, 0.05),
                end: Offset.zero,
              ).animate(CurvedAnimation(parent: anim, curve: Curves.easeOutCubic)),
              child: child,
            ),
          );
        },
      ),
    );
  }

  @override
  void dispose() {
    _mainCtrl.dispose();
    _floatCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const bgTop = Color(0xFF0B1020);
    const bgMid = Color(0xFF151A33);
    const accentA = Color(0xFF6366F1);
    const accentB = Color(0xFF8B5CF6);

    return Scaffold(
      backgroundColor: bgTop,
      body: Stack(
        children: [
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [bgTop, bgMid, bgTop],
                stops: [0.0, 0.52, 1.0],
              ),
            ),
          ),

          const Positioned.fill(child: _AuroraMesh()),

          AnimatedBuilder(
            animation: Listenable.merge([_orb1Opacity, _floatCtrl]),
            builder: (_, __) {
              final dy = math.sin(_floatCtrl.value * math.pi) * 12.0;
              return Positioned(
                top: -100 + dy,
                right: -80,
                child: Opacity(
                  opacity: (_orb1Opacity.value * 0.65).clamp(0.0, 1.0),
                  child: Container(
                    width: 320,
                    height: 320,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: RadialGradient(
                        colors: [
                          accentA.withOpacity(0.34),
                          Colors.transparent,
                        ],
                      ),
                    ),
                  ),
                ),
              );
            },
          ),

          AnimatedBuilder(
            animation: Listenable.merge([_orb2Opacity, _floatCtrl]),
            builder: (_, __) {
              final dy = math.cos(_floatCtrl.value * math.pi) * 10.0;
              return Positioned(
                bottom: -80 + dy,
                left: -100,
                child: Opacity(
                  opacity: (_orb2Opacity.value * 0.55).clamp(0.0, 1.0),
                  child: Container(
                    width: 280,
                    height: 280,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: RadialGradient(
                        colors: [
                          accentB.withOpacity(0.28),
                          Colors.transparent,
                        ],
                      ),
                    ),
                  ),
                ),
              );
            },
          ),

          Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                AnimatedBuilder(
                  animation: Listenable.merge([
                    _mainCtrl,
                    _markOpacity,
                    _markScale,
                    _markFramePulse,
                    _scanPhase,
                  ]),
                  builder: (_, __) {
                    return Opacity(
                      opacity: _markOpacity.value,
                      child: Transform.scale(
                        scale: _markScale.value,
                        child: CustomPaint(
                          size: const Size(_kMarkWidth, _kMarkHeight),
                          painter: _ImagingViewportPainter(
                            frameStrength: _markFramePulse.value,
                            scanT: _scanPhase.value,
                          ),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 36),
                FadeTransition(
                  opacity: _titleOpacity,
                  child: SlideTransition(
                    position: _titleSlide,
                    child: Column(
                      children: [
                        Text(
                          'Smarter Health',
                          textAlign: TextAlign.center,
                          style: GoogleFonts.workSans(
                            fontSize: 34,
                            fontWeight: FontWeight.w700,
                            color: Colors.white,
                            letterSpacing: -1.2,
                            height: 1.05,
                          ),
                        ),
                        ShaderMask(
                          blendMode: BlendMode.srcIn,
                          shaderCallback: (bounds) => const LinearGradient(
                            begin: Alignment.centerLeft,
                            end: Alignment.centerRight,
                            colors: [Color(0xFF93C5FD), accentA, accentB],
                          ).createShader(bounds),
                          child: Text(
                            'Better You',
                            textAlign: TextAlign.center,
                            style: GoogleFonts.workSans(
                              fontSize: 34,
                              fontWeight: FontWeight.w700,
                              color: Colors.white,
                              letterSpacing: -1.2,
                              height: 1.05,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                FadeTransition(
                  opacity: _taglineOpacity,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 3,
                        height: 14,
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(2),
                          gradient: const LinearGradient(
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                            colors: [accentA, accentB],
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Text(
                        'AI-powered bone fracture detection',
                        style: GoogleFonts.workSans(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                          color: Colors.white.withOpacity(0.48),
                          letterSpacing: 0.15,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: SafeArea(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(40, 0, 40, 32),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    AnimatedBuilder(
                      animation: _progressWidth,
                      builder: (_, __) {
                        return LayoutBuilder(builder: (_, c) {
                          return ClipRRect(
                            borderRadius: BorderRadius.circular(999),
                            child: Stack(
                              children: [
                                Container(
                                  height: 3,
                                  width: c.maxWidth,
                                  color: Colors.white.withOpacity(0.07),
                                ),
                                Align(
                                  alignment: Alignment.centerLeft,
                                  child: Container(
                                    height: 3,
                                    width: c.maxWidth * _progressWidth.value,
                                    decoration: BoxDecoration(
                                      borderRadius: BorderRadius.circular(999),
                                      gradient: const LinearGradient(
                                        colors: [accentA, accentB],
                                      ),
                                      boxShadow: [
                                        BoxShadow(
                                          color: accentA.withOpacity(0.55),
                                          blurRadius: 12,
                                          spreadRadius: 0,
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          );
                        });
                      },
                    ),
                    const SizedBox(height: 20),
                    Text(
                      'v1.0.0',
                      style: GoogleFonts.workSans(
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                        color: Colors.white.withOpacity(0.22),
                        letterSpacing: 0.6,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Soft vignette + sparse grid (vector-only depth).
class _AuroraMesh extends StatelessWidget {
  const _AuroraMesh();

  @override
  Widget build(BuildContext context) {
    return CustomPaint(painter: _AuroraMeshPainter());
  }
}

class _AuroraMeshPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final vignette = Paint()
      ..shader = RadialGradient(
        center: Alignment.center,
        radius: 0.95,
        colors: [
          Colors.transparent,
          const Color(0xFF0B1020).withOpacity(0.55),
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));
    canvas.drawRect(Offset.zero & size, vignette);

    final dot = Paint()..color = Colors.white.withOpacity(0.04);
    const spacing = 28.0;
    const r = 1.0;
    for (double x = spacing; x < size.width; x += spacing) {
      for (double y = spacing; y < size.height; y += spacing) {
        canvas.drawCircle(Offset(x, y), r, dot);
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

/// Abstract “imaging” viewport: corner brackets, inner field, traveling scan band.
class _ImagingViewportPainter extends CustomPainter {
  _ImagingViewportPainter({
    required this.frameStrength,
    required this.scanT,
  });

  final double frameStrength;
  final double scanT;

  static const _corner = 18.0;
  static const _stroke = 1.35;

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;
    final rrect = RRect.fromRectAndRadius(
      Rect.fromLTWH(0, 0, w, h),
      const Radius.circular(22),
    );

    final baseStroke = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = _stroke
      ..strokeCap = StrokeCap.round
      ..color = Color.lerp(
            Colors.white.withOpacity(0.08),
            Colors.white.withOpacity(0.22),
            frameStrength,
          ) ??
          Colors.white24;

    canvas.drawRRect(rrect, baseStroke);

    final glow = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.5
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 10)
      ..color = const Color(0xFF6366F1).withOpacity(0.22 * frameStrength);
    canvas.drawRRect(rrect, glow);

    _drawCorners(canvas, w, h);

    final inner = RRect.fromRectAndRadius(
      Rect.fromLTWH(10, 14, w - 20, h - 28),
      const Radius.circular(14),
    );
    final field = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          const Color(0xFF6366F1).withOpacity(0.06 * frameStrength),
          const Color(0xFF8B5CF6).withOpacity(0.03 * frameStrength),
        ],
      ).createShader(inner.outerRect);
    canvas.drawRRect(inner, field);

    final scanY = 14 + (inner.outerRect.height - 20) * scanT;
    final scanRect = Rect.fromLTWH(12, scanY, w - 24, 14);
    final scanPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          const Color(0xFF818CF8).withOpacity(0.0),
          const Color(0xFFA78BFA).withOpacity(0.45 * frameStrength),
          const Color(0xFF818CF8).withOpacity(0.0),
        ],
        stops: const [0.0, 0.5, 1.0],
      ).createShader(scanRect);
    canvas.drawRRect(
      RRect.fromRectAndRadius(scanRect, const Radius.circular(6)),
      scanPaint,
    );

    final tick = Paint()
      ..color = Colors.white.withOpacity(0.12 * frameStrength)
      ..strokeWidth = 1
      ..strokeCap = StrokeCap.round;
    const step = 11.0;
    double x = 18;
    while (x < w - 18) {
      canvas.drawLine(Offset(x, h * 0.52), Offset(x + 5, h * 0.52), tick);
      x += step;
    }
  }

  void _drawCorners(Canvas canvas, double w, double h) {
    final p = Paint()
      ..color = Color.lerp(
            const Color(0xFF818CF8).withOpacity(0.25),
            const Color(0xFF818CF8).withOpacity(0.75),
            frameStrength,
          )!
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    void bracket(Offset o, double sx, double sy) {
      canvas.drawPath(
        Path()
          ..moveTo(o.dx, o.dy + _corner * sy)
          ..lineTo(o.dx, o.dy)
          ..lineTo(o.dx + _corner * sx, o.dy),
        p,
      );
    }

    bracket(const Offset(0, 0), 1, 1);
    bracket(Offset(w, 0), -1, 1);
    bracket(Offset(0, h), 1, -1);
    bracket(Offset(w, h), -1, -1);
  }

  @override
  bool shouldRepaint(covariant _ImagingViewportPainter oldDelegate) {
    return oldDelegate.frameStrength != frameStrength ||
        oldDelegate.scanT != scanT;
  }
}
