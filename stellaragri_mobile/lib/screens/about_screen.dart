import 'package:flutter/material.dart';
import '../core/theme.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('About Stellar Agri AI'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppTheme.cardDark,
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: AppTheme.borderGlow),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('🌾 Agricultural Intelligence Platform', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: AppTheme.mintAccent)),
                  SizedBox(height: 8),
                  Text(
                    'Stellar Agri AI bridges the digital divide for Indian farmers by delivering real-time agronomy, crop health diagnosis, and mandi market prices through conversational AI and autonomous voice telephony in 10 native Indic languages.',
                    style: TextStyle(fontSize: 13.5, color: AppTheme.textMuted, height: 1.45),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Key Modules
            const Text(
              '🧠 Core Architecture & Modules',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppTheme.textMain),
            ),
            const SizedBox(height: 14),

            _buildModuleTile(
              icon: '📞',
              title: 'Autonomous Voice Telephony',
              description: 'Powered by SnapServe.ai & Vobiz.ai (+918071581407). Dials farmers directly with Tamil, Telugu, Hindi, and Kannada ASR and spoken voice synthesis.',
            ),
            _buildModuleTile(
              icon: '📚',
              title: 'Agronomy RAG Knowledge Base',
              description: '3,199 indexed agricultural chunks covering crop recommendations, NPK fertilizer ratios, pest management, and disease cures.',
            ),
            _buildModuleTile(
              icon: '🌦️',
              title: 'Live Weather Telemetry Engine',
              description: 'Fetches real-time temperature, humidity, rain probability, and calculates fungal risk factors to guide irrigation schedules.',
            ),
            _buildModuleTile(
              icon: '📈',
              title: 'APMC Mandi Bhav Intelligence',
              description: 'Integrates official mandi commodity rates per quintal to prevent distress selling and empower farmers with fair pricing.',
            ),

            const SizedBox(height: 24),

            // Datasets & Benchmarks
            const Text(
              '📊 Agricultural Datasets Used',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppTheme.textMain),
            ),
            const SizedBox(height: 14),

            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.surfaceDark,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: AppTheme.borderSubtle),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('• Crop Recommendation Dataset (N, P, K, Temperature, Humidity, pH, Rainfall)', style: TextStyle(fontSize: 13, height: 1.4)),
                  SizedBox(height: 6),
                  Text('• Fertilizer Prediction Dataset (Soil Type, Crop Type, Nitrogen, Phosphorus, Potassium)', style: TextStyle(fontSize: 13, height: 1.4)),
                  SizedBox(height: 6),
                  Text('• PlantVillage Crop Disease Recognition Corpus', style: TextStyle(fontSize: 13, height: 1.4)),
                  SizedBox(height: 6),
                  Text('• Agmarknet / APMC Daily Mandi Commodity Prices', style: TextStyle(fontSize: 13, height: 1.4)),
                  SizedBox(height: 6),
                  Text('• WeatherAPI Agricultural Telemetry API', style: TextStyle(fontSize: 13, height: 1.4)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildModuleTile({required String icon, required String title, required String description}) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.borderSubtle),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(icon, style: const TextStyle(fontSize: 22)),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AppTheme.mintAccent)),
                const SizedBox(height: 4),
                Text(description, style: const TextStyle(fontSize: 12.5, color: AppTheme.textMuted, height: 1.35)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
