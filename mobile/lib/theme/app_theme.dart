import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Design system matching "AI Fitness Nutrition Mobile App - Smarter Health Better You".
class AppTheme {
  AppTheme._();

  static const Color _primaryStart = Color(0xFF6366F1);
  static const Color _primaryEnd = Color(0xFF8B5CF6);
  static const Color _surface = Color(0xFFF8FAFC);
  static const Color _cardBg = Color(0xFFFFFFFF);
  static const Color _textPrimary = Color(0xFF0F172A);
  static const Color _textSecondary = Color(0xFF64748B);
  static const Color _success = Color(0xFF10B981);
  static const Color _warning = Color(0xFFF59E0B);
  static const Color _error = Color(0xFFEF4444);

  static LinearGradient get primaryGradient => const LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [_primaryStart, _primaryEnd],
      );

  static LinearGradient get primaryGradientVertical => const LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [_primaryStart, _primaryEnd],
      );

  static LinearGradient get softGradient => LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          Color.fromRGBO(99, 102, 241, 0.12),
          Color.fromRGBO(139, 92, 246, 0.08),
        ],
      );

  static Color get primaryStart => _primaryStart;
  static Color get primaryEnd => _primaryEnd;
  static Color get surface => _surface;
  static Color get cardBg => _cardBg;
  static Color get textPrimary => _textPrimary;
  static Color get textSecondary => _textSecondary;
  static Color get success => _success;
  static Color get warning => _warning;
  static Color get error => _error;

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      scaffoldBackgroundColor: _surface,
      colorScheme: ColorScheme.light(
        primary: _primaryStart,
        secondary: _primaryEnd,
        surface: _cardBg,
        error: _error,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: _textPrimary,
        onError: Colors.white,
      ),
      textTheme: GoogleFonts.workSansTextTheme(
        ThemeData.light().textTheme.copyWith(
              displayLarge: GoogleFonts.workSans(
                fontSize: 28,
                fontWeight: FontWeight.w700,
                color: _textPrimary,
              ),
              displayMedium: GoogleFonts.workSans(
                fontSize: 24,
                fontWeight: FontWeight.w700,
                color: _textPrimary,
              ),
              headlineMedium: GoogleFonts.workSans(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: _textPrimary,
              ),
              titleLarge: GoogleFonts.workSans(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: _textPrimary,
              ),
              titleMedium: GoogleFonts.workSans(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: _textPrimary,
              ),
              bodyLarge: GoogleFonts.workSans(
                fontSize: 16,
                fontWeight: FontWeight.w400,
                color: _textPrimary,
              ),
              bodyMedium: GoogleFonts.workSans(
                fontSize: 14,
                fontWeight: FontWeight.w400,
                color: _textSecondary,
              ),
              labelLarge: GoogleFonts.workSans(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: _textPrimary,
              ),
            ),
      ),
      appBarTheme: AppBarTheme(
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        backgroundColor: Colors.transparent,
        foregroundColor: _textPrimary,
        titleTextStyle: GoogleFonts.workSans(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: _textPrimary,
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: _cardBg,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        margin: EdgeInsets.zero,
        clipBehavior: Clip.antiAlias,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: 0,
          backgroundColor: _primaryStart,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          textStyle: GoogleFonts.workSans(fontSize: 16, fontWeight: FontWeight.w600),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: _primaryStart,
          side: const BorderSide(color: _primaryStart),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          textStyle: GoogleFonts.workSans(fontSize: 16, fontWeight: FontWeight.w600),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: _cardBg,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      ),
    );
  }
}
