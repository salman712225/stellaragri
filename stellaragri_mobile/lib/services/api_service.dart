import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants.dart';
import '../models/advisory_response.dart';
import '../models/admin_models.dart';

class ApiService {
  static String? _adminToken;

  static bool get isAuthenticated => _adminToken != null && _adminToken!.isNotEmpty;

  static Map<String, String> get _headers {
    final map = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (_adminToken != null) {
      map['Authorization'] = 'Bearer $_adminToken';
      map['Cookie'] = 'stellar_admin_session=$_adminToken';
    }
    return map;
  }

  // ── 1. Farmer Natural Language Query ──
  static asyncQuery(String question) async {
    return sendAdvisoryQuery(question);
  }

  static Future<AdvisoryResponse> sendAdvisoryQuery(String question) async {
    try {
      final response = await http.post(
        Uri.parse(AppConstants.chatEndpoint),
        headers: _headers,
        body: jsonEncode({'question': question}),
      ).timeout(const Duration(seconds: 45));

      if (response.statusCode == 200) {
        final decoded = jsonDecode(utf8.decode(response.bodyBytes));
        return AdvisoryResponse.fromJson(decoded);
      } else {
        throw Exception('Server returned code ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to communicate with Stellar Agri AI: $e');
    }
  }

  // ── 2. Request Instant AI Voice Call ──
  static Future<Map<String, dynamic>> requestVoiceCall({
    required String farmerName,
    required String phoneNumber,
    required String crop,
    required String language,
    String? issue,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(AppConstants.requestCallEndpoint),
        headers: _headers,
        body: jsonEncode({
          'farmer_name': farmerName,
          'phone_number': phoneNumber,
          'crop': crop,
          'language': language,
          'issue': issue ?? 'General agriculture consultation',
        }),
      ).timeout(const Duration(seconds: 25));

      final decoded = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 200) {
        return {
          'success': true,
          'call_id': decoded['call_id'],
          'message': decoded['message'] ?? 'Call initiated successfully!',
        };
      } else {
        return {
          'success': false,
          'error': decoded['error'] ?? 'Failed to initiate phone call.',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network connection error: $e',
      };
    }
  }

  // ── 3. Admin Authentication ──
  static Future<bool> adminLogin(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse(AppConstants.loginEndpoint),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final decoded = jsonDecode(utf8.decode(response.bodyBytes));
        if (decoded['success'] == true && decoded['token'] != null) {
          _adminToken = decoded['token'].toString();
          return true;
        }
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  static void adminLogout() {
    _adminToken = null;
  }

  // ── 4. Admin System Status ──
  static Future<SystemStatusModel?> fetchAdminStatus() async {
    try {
      final response = await http.get(
        Uri.parse(AppConstants.adminStatusEndpoint),
        headers: _headers,
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final decoded = jsonDecode(utf8.decode(response.bodyBytes));
        return SystemStatusModel.fromJson(decoded);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  // ── 5. Admin Call Logs ──
  static Future<List<CallLogModel>> fetchCallLogs() async {
    try {
      final response = await http.get(
        Uri.parse(AppConstants.adminCallsEndpoint),
        headers: _headers,
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final decoded = jsonDecode(utf8.decode(response.bodyBytes));
        if (decoded is List) {
          return decoded.map((c) => CallLogModel.fromJson(c as Map<String, dynamic>)).toList();
        }
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  // ── 6. Admin Farmer Enquiries ──
  static Future<List<FarmerEnquiryModel>> fetchFarmerEnquiries() async {
    try {
      final response = await http.get(
        Uri.parse(AppConstants.adminEnquiriesEndpoint),
        headers: _headers,
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final decoded = jsonDecode(utf8.decode(response.bodyBytes));
        if (decoded is List) {
          return decoded.map((e) => FarmerEnquiryModel.fromJson(e as Map<String, dynamic>)).toList();
        }
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  // ── 7. Toggle Agent Status ──
  static Future<bool> toggleAgent(int agentId) async {
    try {
      final response = await http.patch(
        Uri.parse('${AppConstants.adminAgentsEndpoint}/$agentId/toggle'),
        headers: _headers,
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  // ── 8. Dispatch Test Outbound Call ──
  static Future<Map<String, dynamic>> dispatchOutboundCall({
    required int agentId,
    required String toNumber,
    required String farmerName,
    required String crop,
    required String language,
    String? alertMessage,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(AppConstants.adminOutboundCallEndpoint),
        headers: _headers,
        body: jsonEncode({
          'agentId': agentId,
          'toNumber': toNumber,
          'farmerName': farmerName,
          'crop': crop,
          'language': language,
          'alertMessage': alertMessage,
        }),
      ).timeout(const Duration(seconds: 20));

      final decoded = jsonDecode(utf8.decode(response.bodyBytes));
      return decoded is Map<String, dynamic> ? decoded : {'success': response.statusCode == 200};
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // ── 9. Error Logs & Diagnostics ──
  static Future<Map<String, dynamic>> fetchErrorsAndLogs() async {
    try {
      final response = await http.get(
        Uri.parse(AppConstants.adminErrorsEndpoint),
        headers: _headers,
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        return jsonDecode(utf8.decode(response.bodyBytes));
      }
      return {};
    } catch (e) {
      return {};
    }
  }
}
