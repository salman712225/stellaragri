import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Color Palette
  static const Color bgDark = Color(0xFF070D09);
  static const Color surfaceDark = Color(0xFF0E1811);
  static const Color cardDark = Color(0xFF142419);
  static const Color cardDarkHover = Color(0xFF1B2F21);
  
  static const Color emeraldPrimary = Color(0xFF10B981);
  static const Color mintAccent = Color(0xFF34D399);
  static const Color goldAccent = Color(0xFFFBBF24);
  static const Color redAccent = Color(0xFFF87171);
  static const Color blueAccent = Color(0xFF60A5FA);
  static const Color orangeAccent = Color(0xFFFB923C);
  
  static const Color textMain = Color(0xFFF3F4F6);
  static const Color textMuted = Color(0xFF9CA3AF);
  static const Color textDim = Color(0xFF6B7280);
  static const Color borderSubtle = Color(0x1F34D399);
  static const Color borderGlow = Color(0x4034D399);

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: bgDark,
      primaryColor: emeraldPrimary,
      colorScheme: const ColorScheme.dark(
        primary: emeraldPrimary,
        secondary: mintAccent,
        surface: surfaceDark,
        background: bgDark,
        error: redAccent,
        onPrimary: Colors.black,
        onSecondary: Colors.black,
        onSurface: textMain,
      ),
      textTheme: GoogleFonts.outfitTextTheme(
        ThemeData.dark().textTheme,
      ).apply(
        bodyColor: textMain,
        displayColor: textMain,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: surfaceDark.withOpacity(0.95),
        elevation: 0,
        centerTitle: false,
        iconTheme: const IconThemeData(color: textMain),
        titleTextStyle: GoogleFonts.outfit(
          fontSize: 18,
          fontWeight: FontWeight.w700,
          color: textMain,
        ),
      ),
      cardTheme: CardThemeData(
        color: cardDark,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: borderSubtle, width: 1),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: emeraldPrimary,
          foregroundColor: Colors.black,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: GoogleFonts.outfit(
            fontSize: 15,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surfaceDark,
        hintStyle: GoogleFonts.outfit(color: textDim, fontSize: 14),
        labelStyle: GoogleFonts.outfit(color: textMuted, fontSize: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: borderSubtle),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: borderSubtle),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: mintAccent, width: 1.5),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      ),
    );
  }
}
