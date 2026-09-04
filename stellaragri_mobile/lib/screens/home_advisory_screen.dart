import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../core/theme.dart';
import '../models/advisory_response.dart';
import '../services/api_service.dart';
import '../widgets/advice_card.dart';
import '../widgets/server_settings_dialog.dart';
import 'about_screen.dart';
import 'admin_login_screen.dart';
import 'admin_dashboard_screen.dart';

class HomeAdvisoryScreen extends StatefulWidget {
  const HomeAdvisoryScreen({super.key});

  @override
  State<HomeAdvisoryScreen> createState() => _HomeAdvisoryScreenState();
}

class _HomeAdvisoryScreenState extends State<HomeAdvisoryScreen> {
  final TextEditingController _queryController = TextEditingController();
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _cropController = TextEditingController(text: 'Paddy');
  final TextEditingController _issueController = TextEditingController();

  String _selectedLanguage = 'ta-IN';
  bool _isLoadingQuery = false;
  bool _isRequestingCall = false;
  String? _queryError;
  String? _callStatusMessage;
  bool _callSuccess = false;

  AdvisoryResponse? _advisoryResponse;

  @override
  void dispose() {
    _queryController.dispose();
    _nameController.dispose();
    _phoneController.dispose();
    _cropController.dispose();
    _issueController.dispose();
    super.dispose();
  }

  Future<void> _submitAdvisoryQuery(String query) async {
    if (query.trim().isEmpty) return;
    FocusScope.of(context).unfocus();

    setState(() {
      _isLoadingQuery = true;
      _queryError = null;
    });

    try {
      final res = await ApiService.sendAdvisoryQuery(query);
      setState(() {
        _advisoryResponse = res;
        _isLoadingQuery = false;
      });
    } catch (e) {
      setState(() {
        _queryError = e.toString().replaceAll('Exception:', '').trim();
        _isLoadingQuery = false;
      });
    }
  }

  Future<void> _submitVoiceCallRequest() async {
    final name = _nameController.text.trim().isEmpty ? 'Farmer' : _nameController.text.trim();
    final phone = _phoneController.text.trim();

    if (phone.isEmpty || phone.length < 10) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter a valid 10-digit mobile number.'),
          backgroundColor: AppTheme.redAccent,
        ),
      );
      return;
    }

    setState(() {
      _isRequestingCall = true;
      _callStatusMessage = null;
    });

    final res = await ApiService.requestVoiceCall(
      farmerName: name,
      phoneNumber: phone,
      crop: _cropController.text.trim().isEmpty ? 'Paddy' : _cropController.text.trim(),
      language: _selectedLanguage,
      issue: _issueController.text.trim().isNotEmpty ? _issueController.text.trim() : null,
    );

    setState(() {
      _isRequestingCall = false;
      _callSuccess = res['success'] == true;
      _callStatusMessage = res['success'] == true
          ? '📞 Call Dispatched! Please answer the incoming call from +918071581407 in a few seconds.'
          : (res['error'] ?? 'Call request failed.');
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: AppTheme.emeraldPrimary.withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text('🌾', style: TextStyle(fontSize: 18)),
            ),
            const SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  AppConstants.appName,
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                ),
                Text(
                  'Indic Voice Agronomist',
                  style: TextStyle(fontSize: 11, color: AppTheme.mintAccent.withOpacity(0.8)),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.dns_outlined),
            tooltip: 'Server Settings (${AppConstants.baseUrl})',
            onPressed: () async {
              final changed = await ServerSettingsDialog.show(context);
              if (changed == true && mounted) {
                setState(() {});
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Server URL set to: ${AppConstants.baseUrl}'),
                    backgroundColor: AppTheme.emeraldPrimary,
                  ),
                );
              }
            },
          ),
          IconButton(
            icon: const Icon(Icons.info_outline_rounded),
            tooltip: 'About & Datasets',
            onPressed: () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const AboutScreen()));
            },
          ),
          IconButton(
            icon: const Icon(Icons.admin_panel_settings_outlined),
            tooltip: 'Admin Center',
            onPressed: () {
              if (ApiService.isAuthenticated) {
                Navigator.push(context, MaterialPageRoute(builder: (_) => const AdminDashboardScreen()));
              } else {
                Navigator.push(context, MaterialPageRoute(builder: (_) => const AdminLoginScreen()));
              }
            },
          ),
          const SizedBox(width: 4),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Hero Agronomy Header ──
            _buildHeroHeader(),

            const SizedBox(height: 20),

            // ── Quick Prompt Chips ──
            _buildQuickPrompts(),

            const SizedBox(height: 20),

            // ── Query Input Box ──
            _buildQueryInput(),

            const SizedBox(height: 24),

            // ── Voice Call Request Form Card ──
            _buildVoiceCallCard(),

            const SizedBox(height: 24),

            // ── Advisory Results Grid ──
            if (_isLoadingQuery)
              _buildLoadingState()
            else if (_queryError != null)
              _buildErrorState()
            else if (_advisoryResponse != null)
              _buildAdvisoryResults(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeroHeader() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppTheme.cardDark,
            AppTheme.emeraldPrimary.withOpacity(0.12),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppTheme.borderGlow),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: AppTheme.emeraldPrimary.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: AppTheme.emeraldPrimary),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text('✨ AI-Powered Agronomist', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.mintAccent)),
                  ],
                ),
              ),
              const Spacer(),
              const Text('🟢 Live Online', style: TextStyle(fontSize: 12, color: AppTheme.mintAccent)),
            ],
          ),
          const SizedBox(height: 12),
          const Text(
            'Smart Crop Advisory & Voice Telephony',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: AppTheme.textMain),
          ),
          const SizedBox(height: 6),
          const Text(
            'Ask any agricultural question or request an instant spoken phone call in Tamil, Telugu, Hindi, Kannada, and 6 other Indian languages.',
            style: TextStyle(fontSize: 13, color: AppTheme.textMuted, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickPrompts() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '⚡ Common Farming Questions',
          style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppTheme.mintAccent),
        ),
        const SizedBox(height: 10),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: AppConstants.quickPrompts.map((p) {
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: ActionChip(
                  avatar: Text(p['icon']!, style: const TextStyle(fontSize: 14)),
                  label: Text(p['label']!, style: const TextStyle(fontSize: 12, color: AppTheme.textMain)),
                  backgroundColor: AppTheme.surfaceDark,
                  side: const BorderSide(color: AppTheme.borderSubtle),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                  onPressed: () {
                    _queryController.text = p['prompt']!;
                    _submitAdvisoryQuery(p['prompt']!);
                  },
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildQueryInput() {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderGlow),
      ),
      padding: const EdgeInsets.all(6),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _queryController,
              decoration: const InputDecoration(
                hintText: 'Ask about fertilizers, crop diseases, rain impact, mandi prices...',
                border: InputBorder.none,
                enabledBorder: InputBorder.none,
                focusedBorder: InputBorder.none,
                filled: false,
                contentPadding: EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              ),
              onSubmitted: _submitAdvisoryQuery,
            ),
          ),
          ElevatedButton.icon(
            onPressed: _isLoadingQuery
                ? null
                : () => _submitAdvisoryQuery(_queryController.text),
            icon: _isLoadingQuery
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black),
                  )
                : const Icon(Icons.auto_awesome, size: 18),
            label: Text(_isLoadingQuery ? 'Analyzing...' : 'Get Advice'),
          ),
        ],
      ),
    );
  }

  Widget _buildVoiceCallCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppTheme.goldAccent.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.goldAccent.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.phone_in_talk_rounded, color: AppTheme.goldAccent, size: 20),
              ),
              const SizedBox(width: 10),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Request Instant AI Voice Call',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppTheme.goldAccent),
                    ),
                    Text(
                      'Our AI agronomist dials your phone within 3 seconds',
                      style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Divider(color: AppTheme.borderSubtle, height: 1),
          const SizedBox(height: 16),

          // Name and Phone fields
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _nameController,
                  decoration: const InputDecoration(
                    labelText: 'Farmer Name',
                    hintText: 'e.g. Ramesh',
                    prefixIcon: Icon(Icons.person_outline, size: 20, color: AppTheme.textMuted),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextField(
                  controller: _phoneController,
                  keyboardType: TextInputType.phone,
                  decoration: const InputDecoration(
                    labelText: 'Mobile Number',
                    hintText: 'e.g. 9876543210',
                    prefixIcon: Icon(Icons.phone_android, size: 20, color: AppTheme.textMuted),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Crop and Language selection
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _cropController,
                  decoration: const InputDecoration(
                    labelText: 'Target Crop',
                    hintText: 'Paddy, Tomato, Cotton...',
                    prefixIcon: Icon(Icons.eco_outlined, size: 20, color: AppTheme.textMuted),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: DropdownButtonFormField<String>(
                  value: _selectedLanguage,
                  decoration: const InputDecoration(
                    labelText: 'Spoken Language',
                    prefixIcon: Icon(Icons.language_rounded, size: 20, color: AppTheme.textMuted),
                  ),
                  items: AppConstants.supportedLanguages.map((lang) {
                    return DropdownMenuItem(
                      value: lang['code'],
                      child: Text(lang['name']!, style: const TextStyle(fontSize: 13)),
                    );
                  }).toList(),
                  onChanged: (val) {
                    if (val != null) setState(() => _selectedLanguage = val);
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          TextField(
            controller: _issueController,
            maxLines: 2,
            decoration: const InputDecoration(
              labelText: 'Question or Problem (Optional)',
              hintText: 'e.g. Yellow leaves on paddy crop after rain, need fertilizer and pest remedy.',
            ),
          ),
          const SizedBox(height: 16),

          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _isRequestingCall ? null : _submitVoiceCallRequest,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.goldAccent,
                foregroundColor: Colors.black,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              icon: _isRequestingCall
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black),
                    )
                  : const Icon(Icons.phone_forwarded_rounded, size: 20),
              label: Text(_isRequestingCall ? 'Triggering Call...' : '📲 Call Me Immediately (Free)'),
            ),
          ),

          // Call Status Feedback
          if (_callStatusMessage != null) ...[
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _callSuccess
                    ? AppTheme.emeraldPrimary.withOpacity(0.15)
                    : AppTheme.redAccent.withOpacity(0.15),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: _callSuccess ? AppTheme.emeraldPrimary : AppTheme.redAccent,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    _callSuccess ? Icons.check_circle_outline : Icons.error_outline,
                    color: _callSuccess ? AppTheme.mintAccent : AppTheme.redAccent,
                    size: 20,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      _callStatusMessage!,
                      style: TextStyle(
                        fontSize: 12.5,
                        color: _callSuccess ? AppTheme.mintAccent : AppTheme.redAccent,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return Container(
      padding: const EdgeInsets.all(40),
      alignment: Alignment.center,
      child: const Column(
        children: [
          CircularProgressIndicator(color: AppTheme.emeraldPrimary),
          SizedBox(height: 16),
          Text(
            'Analyzing agricultural knowledge base & live telemetry...',
            style: TextStyle(color: AppTheme.textMuted, fontSize: 13),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState() {
    final isConnError = _queryError!.toLowerCase().contains('socket') ||
        _queryError!.toLowerCase().contains('lookup') ||
        _queryError!.toLowerCase().contains('failed to communicate') ||
        _queryError!.toLowerCase().contains('connection');

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.redAccent.withOpacity(0.1),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.redAccent.withOpacity(0.4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.error_outline, color: AppTheme.redAccent),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  _queryError!,
                  style: const TextStyle(color: AppTheme.redAccent, fontSize: 13),
                ),
              ),
            ],
          ),
          if (isConnError) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: AppTheme.surfaceDark,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.info_outline, size: 16, color: AppTheme.mintAccent),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Target URL: ${AppConstants.baseUrl}\nMake sure your backend is running.',
                      style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
                    ),
                  ),
                  TextButton.icon(
                    icon: const Icon(Icons.settings, size: 14, color: AppTheme.mintAccent),
                    label: const Text('Change URL', style: TextStyle(fontSize: 12, color: AppTheme.mintAccent)),
                    onPressed: () async {
                      final changed = await ServerSettingsDialog.show(context);
                      if (changed == true && mounted) {
                        setState(() {
                          _queryError = null;
                        });
                      }
                    },
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildAdvisoryResults() {
    final res = _advisoryResponse!;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Status header
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          decoration: BoxDecoration(
            color: AppTheme.surfaceDark,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: AppTheme.borderSubtle),
          ),
          child: Row(
            children: [
              Text(
                'Intent: ${res.intent.toUpperCase()}',
                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.mintAccent),
              ),
              const Spacer(),
              if (res.confidence != null)
                Text(
                  'Confidence: ${(res.confidence! * 100).toStringAsFixed(0)}%',
                  style: const TextStyle(fontSize: 11, color: AppTheme.goldAccent),
                ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // 1. Recommended Crop
        if (res.cropRecommendation?.crop != null)
          AdviceCard(
            icon: '🌾',
            title: 'Recommended Crop',
            accentColor: AppTheme.emeraldPrimary,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  res.cropRecommendation!.crop!,
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: AppTheme.mintAccent),
                ),
                if (res.cropRecommendation?.reason != null) ...[
                  const SizedBox(height: 6),
                  Text(res.cropRecommendation!.reason!, style: const TextStyle(fontSize: 13.5, height: 1.4)),
                ],
              ],
            ),
          ),

        // 2. Fertilizer Advice
        if (res.fertilizerAdvice != null && res.fertilizerAdvice!.recommendedFertilizers.isNotEmpty)
          AdviceCard(
            icon: '🧪',
            title: 'Fertilizer Advice',
            accentColor: AppTheme.mintAccent,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: res.fertilizerAdvice!.recommendedFertilizers.map((fert) {
                    return Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: AppTheme.emeraldPrimary.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: AppTheme.emeraldPrimary.withOpacity(0.4)),
                      ),
                      child: Text(
                        fert,
                        style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w600, color: AppTheme.mintAccent),
                      ),
                    );
                  }).toList(),
                ),
                if (res.fertilizerAdvice?.application != null) ...[
                  const SizedBox(height: 10),
                  Text(
                    res.fertilizerAdvice!.application!,
                    style: const TextStyle(fontSize: 13.5, height: 1.4, color: AppTheme.textMuted),
                  ),
                ],
              ],
            ),
          ),

        // 3. Disease Analysis
        if (res.diseaseAnalysis?.detectedDisease != null)
          AdviceCard(
            icon: '🛡️',
            title: 'Crop Disease Diagnosis',
            accentColor: AppTheme.redAccent,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  res.diseaseAnalysis!.detectedDisease!,
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppTheme.redAccent),
                ),
                if (res.diseaseAnalysis?.symptoms != null) ...[
                  const SizedBox(height: 6),
                  Text('Symptoms: ${res.diseaseAnalysis!.symptoms!}', style: const TextStyle(fontSize: 13, color: AppTheme.textMuted)),
                ],
                if (res.diseaseAnalysis?.recommendation != null) ...[
                  const SizedBox(height: 8),
                  Text(res.diseaseAnalysis!.recommendation!, style: const TextStyle(fontSize: 13.5, height: 1.4)),
                ],
              ],
            ),
          ),

        // 4. Pest Control
        if (res.pestAnalysis?.identifiedPest != null)
          AdviceCard(
            icon: '🐛',
            title: 'Pest Control & Spray Remedy',
            accentColor: AppTheme.orangeAccent,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  res.pestAnalysis!.identifiedPest!,
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppTheme.orangeAccent),
                ),
                if (res.pestAnalysis?.recommendation != null) ...[
                  const SizedBox(height: 6),
                  Text(res.pestAnalysis!.recommendation!, style: const TextStyle(fontSize: 13.5, height: 1.4)),
                ],
              ],
            ),
          ),

        // 5. Weather Insights
        if (res.weatherInsights?.impact != null || res.weatherInsights?.recommendation != null)
          AdviceCard(
            icon: '🌧️',
            title: 'Weather Telemetry & Impact',
            accentColor: AppTheme.blueAccent,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (res.weatherInsights?.impact != null)
                  Text(res.weatherInsights!.impact!, style: const TextStyle(fontSize: 13.5, height: 1.4)),
                if (res.weatherInsights?.recommendation != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    res.weatherInsights!.recommendation!,
                    style: const TextStyle(fontSize: 13, color: AppTheme.blueAccent, fontWeight: FontWeight.w600),
                  ),
                ],
              ],
            ),
          ),

        // 6. Market Mandi Prices
        if (res.marketAnalysis?.currentPrice != null || res.marketAnalysis?.recommendation != null)
          AdviceCard(
            icon: '📈',
            title: 'Live APMC Mandi Market Bhav',
            accentColor: AppTheme.goldAccent,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (res.marketAnalysis?.currentPrice != null)
                  Text(
                    res.marketAnalysis!.currentPrice!,
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.goldAccent),
                  ),
                if (res.marketAnalysis?.recommendation != null) ...[
                  const SizedBox(height: 6),
                  Text(res.marketAnalysis!.recommendation!, style: const TextStyle(fontSize: 13.5, height: 1.4)),
                ],
              ],
            ),
          ),

        // 7. Irrigation Advice
        if (res.irrigationAdvice?.schedule != null || res.irrigationAdvice?.recommendation != null)
          AdviceCard(
            icon: '💧',
            title: 'Irrigation & Watering Schedule',
            accentColor: AppTheme.blueAccent,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (res.irrigationAdvice?.schedule != null)
                  Text(res.irrigationAdvice!.schedule!, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700)),
                if (res.irrigationAdvice?.recommendation != null) ...[
                  const SizedBox(height: 6),
                  Text(res.irrigationAdvice!.recommendation!, style: const TextStyle(fontSize: 13.5, height: 1.4, color: AppTheme.textMuted)),
                ],
              ],
            ),
          ),

        // 8. Warnings and Next Steps
        if (res.warnings.isNotEmpty) ...[
          Container(
            padding: const EdgeInsets.all(16),
            margin: const EdgeInsets.only(bottom: 16),
            decoration: BoxDecoration(
              color: AppTheme.redAccent.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppTheme.redAccent.withOpacity(0.3)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.warning_amber_rounded, color: AppTheme.redAccent, size: 20),
                    SizedBox(width: 8),
                    Text('⚠️ Critical Warnings & Risks', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AppTheme.redAccent)),
                  ],
                ),
                const SizedBox(height: 10),
                ...res.warnings.map((w) => Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Text('• $w', style: const TextStyle(fontSize: 13, height: 1.35, color: AppTheme.textMain)),
                    )),
              ],
            ),
          ),
        ],

        if (res.nextSteps.isNotEmpty) ...[
          Container(
            padding: const EdgeInsets.all(16),
            margin: const EdgeInsets.only(bottom: 16),
            decoration: BoxDecoration(
              color: AppTheme.emeraldPrimary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppTheme.emeraldPrimary.withOpacity(0.3)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.checklist_rounded, color: AppTheme.mintAccent, size: 20),
                    SizedBox(width: 8),
                    Text('✅ Recommended Action Items', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AppTheme.mintAccent)),
                  ],
                ),
                const SizedBox(height: 10),
                ...res.nextSteps.map((s) => Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Text('• $s', style: const TextStyle(fontSize: 13, height: 1.35, color: AppTheme.textMain)),
                    )),
              ],
            ),
          ),
        ],
      ],
    );
  }
}
