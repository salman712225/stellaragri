import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../core/theme.dart';
import '../models/admin_models.dart';
import '../services/api_service.dart';
import '../widgets/server_settings_dialog.dart';
import '../widgets/transcript_dialog.dart';
import 'home_advisory_screen.dart';

class AdminDashboardScreen extends StatefulWidget {
  const AdminDashboardScreen({super.key});

  @override
  State<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _isLoading = true;
  SystemStatusModel? _systemStatus;
  List<CallLogModel> _callsList = [];
  List<FarmerEnquiryModel> _enquiriesList = [];
  Map<String, dynamic> _diagnosticsData = {};

  // Dialer fields
  final TextEditingController _dialerNumberController = TextEditingController();
  final TextEditingController _dialerNameController = TextEditingController(text: 'Farmer');
  final TextEditingController _dialerCropController = TextEditingController(text: 'Paddy');
  final TextEditingController _dialerAlertController = TextEditingController();
  String _dialerLanguage = 'ta-IN';
  int _dialerAgentId = 1028;
  bool _isDialing = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
    _refreshAllData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _dialerNumberController.dispose();
    _dialerNameController.dispose();
    _dialerCropController.dispose();
    _dialerAlertController.dispose();
    super.dispose();
  }

  Future<void> _refreshAllData() async {
    setState(() => _isLoading = true);
    final status = await ApiService.fetchAdminStatus();
    final calls = await ApiService.fetchCallLogs();
    final enquiries = await ApiService.fetchFarmerEnquiries();
    final diagnostics = await ApiService.fetchErrorsAndLogs();

    if (status != null && status.agentsList.isNotEmpty) {
      _dialerAgentId = status.agentsList.first.id;
    }

    if (mounted) {
      setState(() {
        _systemStatus = status;
        _callsList = calls;
        _enquiriesList = enquiries;
        _diagnosticsData = diagnostics;
        _isLoading = false;
      });
    }
  }

  Future<void> _handleToggleAgent(int agentId) async {
    final success = await ApiService.toggleAgent(agentId);
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Agent status toggled successfully!'), backgroundColor: AppTheme.emeraldPrimary),
      );
      _refreshAllData();
    }
  }

  Future<void> _handleRedialFarmer(FarmerEnquiryModel enquiry) async {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('📞 Redialing ${enquiry.farmerName} (${enquiry.phoneNumber})...')),
    );

    final res = await ApiService.dispatchOutboundCall(
      agentId: _dialerAgentId,
      toNumber: enquiry.phoneNumber,
      farmerName: enquiry.farmerName,
      crop: enquiry.crop,
      language: enquiry.language,
      alertMessage: enquiry.issue,
    );

    if (res['success'] == true) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Outbound call dispatched!'), backgroundColor: AppTheme.emeraldPrimary),
      );
      _refreshAllData();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Call failed: ${res['error'] ?? 'Unknown error'}'), backgroundColor: AppTheme.redAccent),
      );
    }
  }

  Future<void> _handleDispatchDialerCall() async {
    final phone = _dialerNumberController.text.trim();
    if (phone.isEmpty || phone.length < 10) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a valid 10-digit phone number.'), backgroundColor: AppTheme.redAccent),
      );
      return;
    }

    setState(() => _isDialing = true);
    final res = await ApiService.dispatchOutboundCall(
      agentId: _dialerAgentId,
      toNumber: phone,
      farmerName: _dialerNameController.text.trim().isEmpty ? 'Farmer' : _dialerNameController.text.trim(),
      crop: _dialerCropController.text.trim().isEmpty ? 'Paddy' : _dialerCropController.text.trim(),
      language: _dialerLanguage,
      alertMessage: _dialerAlertController.text.trim().isNotEmpty ? _dialerAlertController.text.trim() : null,
    );
    setState(() => _isDialing = false);

    if (res['success'] == true) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('📞 Outbound phone call dispatched!'), backgroundColor: AppTheme.emeraldPrimary),
      );
      _refreshAllData();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Dialer error: ${res['error'] ?? 'Failed to call'}'), backgroundColor: AppTheme.redAccent),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Admin Operations Center'),
        actions: [
          IconButton(
            icon: const Icon(Icons.dns_outlined),
            tooltip: 'Server Settings (${AppConstants.baseUrl})',
            onPressed: () async {
              final changed = await ServerSettingsDialog.show(context);
              if (changed == true && mounted) {
                _refreshAllData();
              }
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Refresh Data',
            onPressed: _refreshAllData,
          ),
          IconButton(
            icon: const Icon(Icons.logout_rounded),
            tooltip: 'Sign Out',
            onPressed: () {
              ApiService.adminLogout();
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const HomeAdvisoryScreen()),
              );
            },
          ),
          const SizedBox(width: 8),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          indicatorColor: AppTheme.emeraldPrimary,
          labelColor: AppTheme.mintAccent,
          unselectedLabelColor: AppTheme.textMuted,
          tabs: const [
            Tab(icon: Icon(Icons.smart_toy_outlined), text: 'Voice Agents'),
            Tab(icon: Icon(Icons.call_outlined), text: 'Live Call Logs'),
            Tab(icon: Icon(Icons.assignment_outlined), text: 'Farmer Enquiries'),
            Tab(icon: Icon(Icons.terminal_outlined), text: 'Diagnostics'),
            Tab(icon: Icon(Icons.phone_forwarded_outlined), text: 'Test Dialer'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.emeraldPrimary))
          : Column(
              children: [
                // ── KPI Summary Header ──
                _buildKpiHeader(),

                // ── Tab Views ──
                Expanded(
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _buildAgentsTab(),
                      _buildCallsTab(),
                      _buildEnquiriesTab(),
                      _buildDiagnosticsTab(),
                      _buildDialerTab(),
                    ],
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildKpiHeader() {
    final status = _systemStatus;
    final isConnected = status?.isConnected ?? false;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: const BoxDecoration(
        color: AppTheme.surfaceDark,
        border: Border(bottom: BorderSide(color: AppTheme.borderSubtle)),
      ),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            _buildKpiCard(
              title: 'MCP Server',
              value: '${status?.pingLatencyMs ?? 0} ms',
              subtitle: isConnected ? '🟢 Connected (76 tools)' : '🔴 Disconnected',
              accent: isConnected ? AppTheme.mintAccent : AppTheme.redAccent,
            ),
            const SizedBox(width: 10),
            _buildKpiCard(
              title: 'Prepaid Balance',
              value: '₹${(status?.balanceInr ?? 0).toStringAsFixed(2)}',
              subtitle: '${status?.balanceCents ?? 0} paise',
              accent: AppTheme.goldAccent,
            ),
            const SizedBox(width: 10),
            _buildKpiCard(
              title: 'Active Phone DID',
              value: status?.activePhoneDid ?? '+918071581407',
              subtitle: 'Inbound & Outbound PSTN',
              accent: AppTheme.emeraldPrimary,
            ),
            const SizedBox(width: 10),
            _buildKpiCard(
              title: 'Total Call Sessions',
              value: '${_callsList.length}',
              subtitle: '${status?.activeAgents ?? 1} Active Agents',
              accent: AppTheme.blueAccent,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildKpiCard({
    required String title,
    required String value,
    required String subtitle,
    required Color accent,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: accent.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
          const SizedBox(height: 2),
          Text(value, style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: accent)),
          const SizedBox(height: 2),
          Text(subtitle, style: const TextStyle(fontSize: 10, color: AppTheme.textDim)),
        ],
      ),
    );
  }

  // ── Tab 1: Voice Agents ──
  Widget _buildAgentsTab() {
    final agents = _systemStatus?.agentsList ?? [];
    if (agents.isEmpty) {
      return const Center(child: Text('No voice agents configured.'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: agents.length,
      itemBuilder: (context, index) {
        final agent = agents[index];
        final isActive = agent.status == 'active';

        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: (isActive ? AppTheme.emeraldPrimary : AppTheme.textDim).withOpacity(0.15),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        '#${agent.id}',
                        style: TextStyle(
                          fontWeight: FontWeight.w800,
                          color: isActive ? AppTheme.mintAccent : AppTheme.textDim,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            agent.name,
                            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                          ),
                          Text(
                            'Language: ${agent.language} · Status: ${agent.status.toUpperCase()}',
                            style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                          ),
                        ],
                      ),
                    ),
                    Switch(
                      value: isActive,
                      activeColor: AppTheme.emeraldPrimary,
                      onChanged: (_) => _handleToggleAgent(agent.id),
                    ),
                  ],
                ),
                if (agent.greetingMessage != null) ...[
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppTheme.surfaceDark,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      'Opening Greeting: "${agent.greetingMessage}"',
                      style: const TextStyle(fontSize: 12, color: AppTheme.textDim, fontStyle: FontStyle.italic),
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  // ── Tab 2: Call Logs ──
  Widget _buildCallsTab() {
    if (_callsList.isEmpty) {
      return const Center(child: Text('No call logs recorded.'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _callsList.length,
      itemBuilder: (context, index) {
        final call = _callsList[index];
        final hasAudio = call.recordingUrl != null && call.recordingUrl!.isNotEmpty;

        return Card(
          margin: const EdgeInsets.only(bottom: 10),
          child: ListTile(
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            onTap: () {
              showDialog(
                context: context,
                builder: (_) => TranscriptDialog(call: call),
              );
            },
            title: Row(
              children: [
                Text(
                  call.toNumber,
                  style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: (call.status == 'completed' ? AppTheme.emeraldPrimary : AppTheme.goldAccent).withOpacity(0.15),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    call.status,
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: call.status == 'completed' ? AppTheme.mintAccent : AppTheme.goldAccent,
                    ),
                  ),
                ),
              ],
            ),
            subtitle: Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text(
                '${call.agentName} · ${call.durationSeconds}s · Cost: ₹${(call.costCents / 100).toStringAsFixed(2)}',
                style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
              ),
            ),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (hasAudio)
                  IconButton(
                    icon: const Icon(Icons.play_circle_fill_rounded, color: AppTheme.emeraldPrimary, size: 28),
                    tooltip: 'Play Call Recording',
                    onPressed: () {
                      showDialog(
                        context: context,
                        builder: (_) => TranscriptDialog(call: call),
                      );
                    },
                  ),
                const Icon(Icons.chevron_right_rounded, color: AppTheme.textDim),
              ],
            ),
          ),
        );
      },
    );
  }

  // ── Tab 3: Farmer Enquiries ──
  Widget _buildEnquiriesTab() {
    if (_enquiriesList.isEmpty) {
      return const Center(child: Text('No farmer enquiries registered yet.'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _enquiriesList.length,
      itemBuilder: (context, index) {
        final enquiry = _enquiriesList[index];

        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            enquiry.farmerName,
                            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppTheme.textMain),
                          ),
                          Text(
                            '${enquiry.phoneNumber} · Crop: ${enquiry.crop} (${enquiry.language})',
                            style: const TextStyle(fontSize: 12, color: AppTheme.mintAccent),
                          ),
                        ],
                      ),
                    ),
                    ElevatedButton.icon(
                      onPressed: () => _handleRedialFarmer(enquiry),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.emeraldPrimary,
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      ),
                      icon: const Icon(Icons.phone_rounded, size: 16, color: Colors.black),
                      label: const Text('Redial', style: TextStyle(fontSize: 12, color: Colors.black)),
                    ),
                  ],
                ),
                if (enquiry.issue != null && enquiry.issue!.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  Text(
                    'Query: "${enquiry.issue}"',
                    style: const TextStyle(fontSize: 12.5, color: AppTheme.textMuted),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  // ── Tab 4: System Diagnostics ──
  Widget _buildDiagnosticsTab() {
    final metrics = _diagnosticsData['metrics'] is Map ? _diagnosticsData['metrics'] : {};
    final errors = _diagnosticsData['recentErrors'] is List ? _diagnosticsData['recentErrors'] as List : [];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '⚡ Voice Telephony Latency Benchmarks',
            style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: AppTheme.mintAccent),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildKpiCard(
                  title: 'STT Latency',
                  value: '${metrics['avgSttLatencyMs'] ?? 240} ms',
                  subtitle: 'Sarvam Realtime',
                  accent: AppTheme.mintAccent,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildKpiCard(
                  title: 'LLM 1st-Token',
                  value: '${metrics['avgLlmLatencyMs'] ?? 310} ms',
                  subtitle: 'Groq / Llama 3.3',
                  accent: AppTheme.goldAccent,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildKpiCard(
                  title: 'TTS Chunk',
                  value: '${metrics['avgTtsFirstChunkMs'] ?? 180} ms',
                  subtitle: 'Sarvam Audio',
                  accent: AppTheme.blueAccent,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          const Text(
            '📋 Real-Time Error Stream & Event Logs',
            style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: AppTheme.textMain),
          ),
          const SizedBox(height: 12),
          if (errors.isEmpty)
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppTheme.cardDark,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.emeraldPrimary.withOpacity(0.3)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.check_circle_outline, color: AppTheme.mintAccent),
                  SizedBox(width: 12),
                  Text('System Diagnostics Normal · 0 Reported Runtime Errors', style: TextStyle(color: AppTheme.mintAccent, fontSize: 13)),
                ],
              ),
            )
          else
            ...errors.map((err) {
              final cat = err['category']?.toString() ?? 'Error';
              final msg = err['message']?.toString() ?? 'Details';
              return Container(
                margin: const EdgeInsets.only(bottom: 8),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.surfaceDark,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppTheme.redAccent.withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(cat, style: const TextStyle(fontWeight: FontWeight.w700, color: AppTheme.redAccent, fontSize: 12)),
                    const SizedBox(height: 4),
                    Text(msg, style: const TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                  ],
                ),
              );
            }),
        ],
      ),
    );
  }

  // ── Tab 5: Test Dialer ──
  Widget _buildDialerTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 550),
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppTheme.cardDark,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: AppTheme.borderGlow),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.phone_in_talk_rounded, color: AppTheme.goldAccent, size: 24),
                SizedBox(width: 10),
                Text('Outbound Test Dialer', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.goldAccent)),
              ],
            ),
            const SizedBox(height: 6),
            const Text(
              'Dispatch test calls with dynamic multilingual prompts and live telemetry injection.',
              style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
            ),
            const SizedBox(height: 18),
            const Divider(color: AppTheme.borderSubtle, height: 1),
            const SizedBox(height: 18),

            TextField(
              controller: _dialerNumberController,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(
                labelText: 'Destination Mobile Number',
                hintText: 'e.g. 9876543210',
                prefixIcon: Icon(Icons.phone_android, color: AppTheme.textMuted),
              ),
            ),
            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _dialerNameController,
                    decoration: const InputDecoration(labelText: 'Farmer Name'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: _dialerCropController,
                    decoration: const InputDecoration(labelText: 'Crop'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            DropdownButtonFormField<String>(
              value: _dialerLanguage,
              decoration: const InputDecoration(labelText: 'Dialect / Language'),
              items: AppConstants.supportedLanguages.map((lang) {
                return DropdownMenuItem(
                  value: lang['code'],
                  child: Text(lang['name']!, style: const TextStyle(fontSize: 13)),
                );
              }).toList(),
              onChanged: (val) {
                if (val != null) setState(() => _dialerLanguage = val);
              },
            ),
            const SizedBox(height: 12),

            TextField(
              controller: _dialerAlertController,
              maxLines: 2,
              decoration: const InputDecoration(
                labelText: 'Advisory Alert Message (Optional)',
                hintText: 'e.g. Heavy rainfall alert in Thanjavur. Postpone urea spray.',
              ),
            ),
            const SizedBox(height: 18),

            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _isDialing ? null : _handleDispatchDialerCall,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.goldAccent,
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
                icon: _isDialing
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black),
                      )
                    : const Icon(Icons.phone_forwarded_rounded, size: 20),
                label: Text(_isDialing ? 'Dialing...' : '📞 Trigger Outbound Phone Call'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
