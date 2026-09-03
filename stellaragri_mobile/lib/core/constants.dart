class AppConstants {
  static const String appName = 'Stellar Agri AI';
  static const String appSubtitle = 'Intelligent Agronomy & Voice Advisory';
  
  // Production Backend URL
  static const String baseUrl = 'https://stellaragri.site';

  // API Endpoints
  static const String chatEndpoint = '$baseUrl/chat';
  static const String requestCallEndpoint = '$baseUrl/api/request-call';
  static const String loginEndpoint = '$baseUrl/api/auth/login';
  static const String logoutEndpoint = '$baseUrl/api/auth/logout';
  static const String adminStatusEndpoint = '$baseUrl/api/admin/status';
  static const String adminAgentsEndpoint = '$baseUrl/api/admin/agents';
  static const String adminCallsEndpoint = '$baseUrl/api/admin/calls';
  static const String adminEnquiriesEndpoint = '$baseUrl/api/admin/enquiries';
  static const String adminErrorsEndpoint = '$baseUrl/api/admin/errors-and-logs';
  static const String adminOutboundCallEndpoint = '$baseUrl/api/admin/calls/outbound';
  static const String audioRecordingBase = '$baseUrl/api/admin/storage/recordings';

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
