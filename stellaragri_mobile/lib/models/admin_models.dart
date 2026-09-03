class SystemStatusModel {
  final bool isConnected;
  final String server;
  final int toolCount;
  final int pingLatencyMs;
  final double balanceInr;
  final int balanceCents;
  final String activePhoneDid;
  final int totalCalls;
  final int totalAgents;
  final int activeAgents;
  final List<AgentModel> agentsList;

  SystemStatusModel({
    required this.isConnected,
    required this.server,
    required this.toolCount,
    required this.pingLatencyMs,
    required this.balanceInr,
    required this.balanceCents,
    required this.activePhoneDid,
    required this.totalCalls,
    required this.totalAgents,
    required this.activeAgents,
    required this.agentsList,
  });

  factory SystemStatusModel.fromJson(Map<String, dynamic> json) {
    final mcp = json['mcp'] is Map ? json['mcp'] : {};
    final wallet = json['wallet'] is Map ? json['wallet'] : {};
    final telephony = json['telephony'] is Map ? json['telephony'] : {};
    final agents = json['agents'] is Map ? json['agents'] : {};

    List<AgentModel> parsedAgents = [];
    if (agents['list'] is List) {
      parsedAgents = (agents['list'] as List)
          .map((a) => AgentModel.fromJson(a as Map<String, dynamic>))
          .toList();
    }

    String phoneDid = 'No number linked';
    if (telephony['numbers'] is List && (telephony['numbers'] as List).isNotEmpty) {
      phoneDid = telephony['numbers'][0]['number']?.toString() ?? 'No number linked';
    }

    return SystemStatusModel(
      isConnected: mcp['connected'] == true || parsedAgents.isNotEmpty,
      server: mcp['server']?.toString() ?? '@snapserveai/mcp',
      toolCount: mcp['toolCount'] is int ? mcp['toolCount'] : 76,
      pingLatencyMs: mcp['pingLatencyMs'] is int ? mcp['pingLatencyMs'] : 0,
      balanceInr: wallet['balanceInr'] is num ? (wallet['balanceInr'] as num).toDouble() : 0.0,
      balanceCents: wallet['balanceCents'] is int ? wallet['balanceCents'] : 0,
      activePhoneDid: phoneDid,
      totalCalls: json['totalCalls'] is int ? json['totalCalls'] : 0,
      totalAgents: agents['total'] is int ? agents['total'] : parsedAgents.length,
      activeAgents: agents['activeCount'] is int ? agents['activeCount'] : 0,
      agentsList: parsedAgents,
    );
  }
}

class AgentModel {
  final int id;
  final String name;
  final String status;
  final String language;
  final String? greetingMessage;
  final String? asrProvider;
  final String? llmModel;
  final String? ttsVoice;

  AgentModel({
    required this.id,
    required this.name,
    required this.status,
    required this.language,
    this.greetingMessage,
    this.asrProvider,
    this.llmModel,
    this.ttsVoice,
  });

  factory AgentModel.fromJson(Map<String, dynamic> json) {
    return AgentModel(
      id: json['id'] is int ? json['id'] : int.tryParse(json['id']?.toString() ?? '0') ?? 0,
      name: json['name']?.toString() ?? 'Agent',
      status: json['status']?.toString() ?? 'draft',
      language: json['language']?.toString() ?? 'hi-IN',
      greetingMessage: json['greetingMessage']?.toString(),
      asrProvider: json['asrProvider']?.toString(),
      llmModel: json['llmModel']?.toString(),
      ttsVoice: json['ttsVoice']?.toString(),
    );
  }
}

class CallLogModel {
  final int id;
  final String toNumber;
  final String fromNumber;
  final String agentName;
  final int? agentId;
  final String status;
  final int durationSeconds;
  final int costCents;
  final String? createdAt;
  final String? recordingUrl;
  final String? transcript;
  final String? callSummary;
  final String? successEvaluation;

  CallLogModel({
    required this.id,
    required this.toNumber,
    required this.fromNumber,
    required this.agentName,
    this.agentId,
    required this.status,
    required this.durationSeconds,
    required this.costCents,
    this.createdAt,
    this.recordingUrl,
    this.transcript,
    this.callSummary,
    this.successEvaluation,
  });

  factory CallLogModel.fromJson(Map<String, dynamic> json) {
    String? rec = json['recordingUrl']?.toString() ?? 
                  json['audioUrl']?.toString() ?? 
                  json['recording_url']?.toString() ?? 
                  (json['recording'] is String ? json['recording']?.toString() : null);

    return CallLogModel(
      id: json['id'] is int ? json['id'] : int.tryParse(json['id']?.toString() ?? '0') ?? 0,
      toNumber: json['toNumber']?.toString() ?? 'Anonymous',
      fromNumber: json['fromNumber']?.toString() ?? '+918071581407',
      agentName: json['agentName']?.toString() ?? 'Stellar Agri Advisor',
      agentId: json['agentId'] is int ? json['agentId'] : null,
      status: json['status']?.toString() ?? 'completed',
      durationSeconds: json['durationSeconds'] is int ? json['durationSeconds'] : 0,
      costCents: json['costCents'] is int ? json['costCents'] : 0,
      createdAt: json['createdAt']?.toString(),
      recordingUrl: rec,
      transcript: json['transcript']?.toString(),
      callSummary: json['callSummary']?.toString(),
      successEvaluation: json['successEvaluation']?.toString(),
    );
  }
}

class FarmerEnquiryModel {
  final String id;
  final String farmerName;
  final String phoneNumber;
  final String crop;
  final String language;
  final String? issue;
  final dynamic callId;
  final String status;
  final String? createdAt;

  FarmerEnquiryModel({
    required this.id,
    required this.farmerName,
    required this.phoneNumber,
    required this.crop,
    required this.language,
    this.issue,
    this.callId,
    required this.status,
    this.createdAt,
  });

  factory FarmerEnquiryModel.fromJson(Map<String, dynamic> json) {
    return FarmerEnquiryModel(
      id: json['id']?.toString() ?? json['_id']?.toString() ?? '',
      farmerName: json['farmer_name']?.toString() ?? 'Farmer',
      phoneNumber: json['phone_number']?.toString() ?? '',
      crop: json['crop']?.toString() ?? 'Paddy',
      language: json['language']?.toString() ?? 'hi-IN',
      issue: json['issue']?.toString(),
      callId: json['call_id'],
      status: json['status']?.toString() ?? 'pending',
      createdAt: json['created_at']?.toString(),
    );
  }
}
