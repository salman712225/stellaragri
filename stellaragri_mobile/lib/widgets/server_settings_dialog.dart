import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../core/theme.dart';
import '../services/api_service.dart';

class ServerSettingsDialog extends StatefulWidget {
  const ServerSettingsDialog({super.key});

  static Future<bool?> show(BuildContext context) {
    return showDialog<bool>(
      context: context,
      builder: (_) => const ServerSettingsDialog(),
    );
  }

  @override
  State<ServerSettingsDialog> createState() => _ServerSettingsDialogState();
}

class _ServerSettingsDialogState extends State<ServerSettingsDialog> {
  late TextEditingController _urlController;
  bool _isTesting = false;
  String? _testResult;
  bool _testSuccess = false;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController(text: AppConstants.baseUrl);
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _testConnection() async {
    final url = _urlController.text.trim();
    if (url.isEmpty) return;

    setState(() {
      _isTesting = true;
      _testResult = null;
    });

    final res = await ApiService.testConnection(url);

    if (!mounted) return;

    setState(() {
      _isTesting = false;
      _testSuccess = res['success'] == true;
      _testResult = res['message'] ?? (res['success'] == true ? 'Connection OK' : 'Connection failed');
    });
  }

  void _applyUrl(String url) {
    var formatted = url.trim();
    if (formatted.endsWith('/')) {
      formatted = formatted.substring(0, formatted.length - 1);
    }
    _urlController.text = formatted;
  }

  void _saveAndClose() {
    var formatted = _urlController.text.trim();
    if (formatted.endsWith('/')) {
      formatted = formatted.substring(0, formatted.length - 1);
    }
    if (formatted.isNotEmpty) {
      AppConstants.baseUrl = formatted;
      Navigator.of(context).pop(true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: AppTheme.cardDark,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: BorderSide(color: AppTheme.borderGlow),
      ),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 480),
        padding: const EdgeInsets.all(22),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppTheme.emeraldPrimary.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(
                      Icons.settings_ethernet_rounded,
                      color: AppTheme.mintAccent,
                      size: 22,
                    ),
                  ),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Backend Server Settings',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            color: AppTheme.textMain,
                          ),
                        ),
                        Text(
                          'Configure API Host & Port',
                          style: TextStyle(
                            fontSize: 11,
                            color: AppTheme.textMuted,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: AppTheme.textMuted, size: 20),
                    onPressed: () => Navigator.of(context).pop(false),
                  ),
                ],
              ),
              const SizedBox(height: 18),

              const Text(
                'Server Base URL:',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.mintAccent,
                ),
              ),
              const SizedBox(height: 6),

              // URL Input
              TextField(
                controller: _urlController,
                style: const TextStyle(fontSize: 13, fontFamily: 'monospace'),
                decoration: InputDecoration(
                  hintText: 'http://10.0.2.2:8000',
                  prefixIcon: const Icon(Icons.link, color: AppTheme.textMuted, size: 18),
                  suffixIcon: IconButton(
                    icon: _isTesting
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.mintAccent),
                          )
                        : const Icon(Icons.refresh, color: AppTheme.mintAccent, size: 20),
                    tooltip: 'Test Connection',
                    onPressed: _isTesting ? null : _testConnection,
                  ),
                ),
              ),
              const SizedBox(height: 14),

              // Quick Presets
              const Text(
                'Quick Presets:',
                style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _PresetChip(
                    label: '📱 Android Emulator',
                    subtitle: '10.0.2.2:8000',
                    onTap: () => _applyUrl('http://10.0.2.2:8000'),
                  ),
                  _PresetChip(
                    label: '💻 Localhost',
                    subtitle: '127.0.0.1:8000',
                    onTap: () => _applyUrl('http://127.0.0.1:8000'),
                  ),
                  _PresetChip(
                    label: '🏠 Local Wi-Fi (LAN)',
                    subtitle: 'http://<your-ip>:8000',
                    onTap: () => _applyUrl('http://192.168.1.100:8000'),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Diagnostic result box
              if (_testResult != null) ...[
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: _testSuccess
                        ? AppTheme.emeraldPrimary.withOpacity(0.15)
                        : AppTheme.redAccent.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: _testSuccess
                          ? AppTheme.emeraldPrimary.withOpacity(0.4)
                          : AppTheme.redAccent.withOpacity(0.4),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        _testSuccess ? Icons.check_circle_rounded : Icons.error_outline_rounded,
                        color: _testSuccess ? AppTheme.mintAccent : AppTheme.redAccent,
                        size: 18,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _testResult!,
                          style: TextStyle(
                            fontSize: 11,
                            color: _testSuccess ? AppTheme.mintAccent : AppTheme.redAccent,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // Actions
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      icon: const Icon(Icons.bolt_rounded, size: 16),
                      label: const Text('Test Connection'),
                      onPressed: _isTesting ? null : _testConnection,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: ElevatedButton.icon(
                      icon: const Icon(Icons.save_rounded, size: 16),
                      label: const Text('Save & Apply'),
                      onPressed: _saveAndClose,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _PresetChip extends StatelessWidget {
  final String label;
  final String subtitle;
  final VoidCallback onTap;

  const _PresetChip({
    required this.label,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: AppTheme.surfaceDark,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: AppTheme.borderGlow),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              label,
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppTheme.mintAccent),
            ),
            Text(
              subtitle,
              style: const TextStyle(fontSize: 9, color: AppTheme.textMuted, fontFamily: 'monospace'),
            ),
          ],
        ),
      ),
    );
  }
}
