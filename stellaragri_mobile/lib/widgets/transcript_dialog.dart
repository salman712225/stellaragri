import 'package:flutter/material.dart';
import '../core/theme.dart';
import '../models/admin_models.dart';
import 'audio_player_widget.dart';

class TranscriptDialog extends StatelessWidget {
  final CallLogModel call;

  const TranscriptDialog({super.key, required this.call});

  @override
  Widget build(BuildContext context) {
    String? audioUrl = call.recordingUrl;
    if (audioUrl != null && !audioUrl.startsWith('http')) {
      audioUrl = 'https://stellaragri.site$audioUrl';
    } else if (audioUrl == null || audioUrl.isEmpty) {
      audioUrl = 'https://stellaragri.site/api/admin/storage/recordings/${call.id}';
    }

    final transcriptLines = (call.transcript ?? '')
        .split('\n')
        .where((l) => l.trim().isNotEmpty)
        .toList();

    return Dialog(
      backgroundColor: AppTheme.surfaceDark,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: AppTheme.borderGlow),
      ),
      insetPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 650, maxHeight: 750),
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Call #${call.id} (${call.toNumber})',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: AppTheme.textMain,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${call.agentName} · ${call.durationSeconds}s · Status: ${call.status.toUpperCase()}',
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppTheme.mintAccent,
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close_rounded, color: AppTheme.textMuted),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
            const SizedBox(height: 14),
            const Divider(color: AppTheme.borderSubtle, height: 1),
            const SizedBox(height: 14),

            // Scrollable Content
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Audio Player
                    if (audioUrl != null && audioUrl.isNotEmpty) ...[
                      AudioPlayerWidget(
                        audioUrl: audioUrl,
                        title: '🎙️ Call Audio Recording (#${call.id})',
                      ),
                      const SizedBox(height: 16),
                    ],

                    // AI Summary Card
                    if (call.callSummary != null && call.callSummary!.isNotEmpty) ...[
                      Container(
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: AppTheme.cardDark,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppTheme.borderSubtle),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              '💡 AI Conversation Summary',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w700,
                                color: AppTheme.goldAccent,
                              ),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              call.callSummary!,
                              style: const TextStyle(
                                fontSize: 13.5,
                                color: AppTheme.textMain,
                                height: 1.4,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // Conversation Transcript
                    const Text(
                      '💬 Transcript Stream',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.mintAccent,
                      ),
                    ),
                    const SizedBox(height: 10),

                    if (transcriptLines.isEmpty)
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(24),
                        alignment: Alignment.center,
                        child: const Text(
                          'No conversation transcript recorded for this session.',
                          style: TextStyle(color: AppTheme.textDim, fontSize: 13),
                        ),
                      )
                    else
                      ...transcriptLines.map((line) {
                        final isAgent = line.toLowerCase().startsWith('agent:') ||
                            line.toLowerCase().startsWith('assistant:');
                        final author = isAgent ? call.agentName : 'Farmer';
                        final text = line.replaceFirst(RegExp(r'^(Agent:|Assistant:|Caller:|User:)\s*', caseSensitive: false), '');

                        return Align(
                          alignment: isAgent ? Alignment.centerLeft : Alignment.centerRight,
                          child: Container(
                            margin: const EdgeInsets.symmetric(vertical: 4),
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                            constraints: const BoxConstraints(maxWidth: 480),
                            decoration: BoxDecoration(
                              color: isAgent ? AppTheme.cardDark : AppTheme.emeraldPrimary.withOpacity(0.15),
                              borderRadius: BorderRadius.circular(14),
                              border: Border.all(
                                color: isAgent ? AppTheme.borderSubtle : AppTheme.emeraldPrimary.withOpacity(0.4),
                              ),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  author,
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w700,
                                    color: isAgent ? AppTheme.mintAccent : AppTheme.goldAccent,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  text,
                                  style: const TextStyle(
                                    fontSize: 13.5,
                                    color: AppTheme.textMain,
                                    height: 1.35,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      }),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
