import 'package:flutter/foundation.dart';

class AppConstants {
  static const String appName = 'Stellar Agri AI';
  static const String appSubtitle = 'Intelligent Agronomy & Voice Advisory';
  
  // Dynamic Backend Base URL
  // Android emulator uses 10.0.2.2 to access host machine; Web/Desktop/iOS uses 127.0.0.1
  static String baseUrl = _defaultBaseUrl();

  static String _defaultBaseUrl() {
    if (kIsWeb) return 'http://127.0.0.1:8000';
    if (defaultTargetPlatform == TargetPlatform.android) {
      return 'http://10.0.2.2:8000';
    }
    return 'http://127.0.0.1:8000';
  }

  // API Endpoints (Dynamic Getters)
  static String get chatEndpoint => '$baseUrl/chat';
  static String get requestCallEndpoint => '$baseUrl/api/request-call';
  static String get loginEndpoint => '$baseUrl/api/auth/login';
  static String get logoutEndpoint => '$baseUrl/api/auth/logout';
  static String get adminStatusEndpoint => '$baseUrl/api/admin/status';
  static String get adminAgentsEndpoint => '$baseUrl/api/admin/agents';
  static String get adminCallsEndpoint => '$baseUrl/api/admin/calls';
  static String get adminEnquiriesEndpoint => '$baseUrl/api/admin/enquiries';
  static String get adminErrorsEndpoint => '$baseUrl/api/admin/errors-and-logs';
  static String get adminOutboundCallEndpoint => '$baseUrl/api/admin/calls/outbound';
  static String get audioRecordingBase => '$baseUrl/api/admin/storage/recordings';
  static String get healthEndpoint => '$baseUrl/health';

  // Supported Indic Languages for AI Telephony
  static const List<Map<String, String>> supportedLanguages = [
    {'code': 'hi-IN', 'name': 'Hindi (हिंदी)'},
    {'code': 'ta-IN', 'name': 'Tamil (தமிழ்)'},
    {'code': 'te-IN', 'name': 'Telugu (తెలుగు)'},
    {'code': 'kn-IN', 'name': 'Kannada (ಕನ್ನಡ)'},
    {'code': 'mr-IN', 'name': 'Marathi (मराठी)'},
    {'code': 'bn-IN', 'name': 'Bengali (বাংলা)'},
    {'code': 'gu-IN', 'name': 'Gujarati (ગુજરાતી)'},
    {'code': 'pa-IN', 'name': 'Punjabi (ਪੰਜਾਬੀ)'},
    {'code': 'ml-IN', 'name': 'Malayalam (മലയാളം)'},
    {'code': 'en-IN', 'name': 'English (Indian)'},
  ];

  // Quick Prompt Chips
  static const List<Map<String, String>> quickPrompts = [
    {'icon': '🧪', 'label': 'Rice Fertilizer', 'prompt': 'Which fertilizer should I use for rice in clayey soil?'},
    {'icon': '🌾', 'label': 'Crop Recommendation', 'prompt': 'Recommend crops for high NPK and black soil with moderate rainfall'},
    {'icon': '🌧️', 'label': 'Tamil Nadu Weather', 'prompt': 'Live weather forecast and agricultural rain impact for Tamil Nadu'},
    {'icon': '🐛', 'label': 'Tomato Pest Control', 'prompt': 'Pest control and fungicide spray for tomato leaf curl disease'},
    {'icon': '📈', 'label': 'Paddy Mandi Price', 'prompt': 'What is the current APMC mandi market price for paddy per quintal?'},
  ];
}
