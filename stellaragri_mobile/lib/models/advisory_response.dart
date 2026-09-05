class AdvisoryResponse {
  final String status;
  final String query;
  final String intent;
  final double? confidence;
  final int? chunksRetrieved;
  final double? executionTime;
  final Map<String, dynamic>? entities;
  
  final CropRecommendation? cropRecommendation;
  final FertilizerAdvice? fertilizerAdvice;
  final DiseaseAnalysis? diseaseAnalysis;
  final PestAnalysis? pestAnalysis;
  final WeatherInsights? weatherInsights;
  final MarketAnalysis? marketAnalysis;
  final IrrigationAdvice? irrigationAdvice;
  final CropManagement? cropManagement;
  
  final List<String> warnings;
  final List<String> nextSteps;
  final Map<String, dynamic> rawJson;

  AdvisoryResponse({
    required this.status,
    required this.query,
    required this.intent,
    this.confidence,
    this.chunksRetrieved,
    this.executionTime,
    this.entities,
    this.cropRecommendation,
    this.fertilizerAdvice,
    this.diseaseAnalysis,
    this.pestAnalysis,
    this.weatherInsights,
    this.marketAnalysis,
    this.irrigationAdvice,
    this.cropManagement,
    required this.warnings,
    required this.nextSteps,
    required this.rawJson,
  });

  factory AdvisoryResponse.fromJson(Map<String, dynamic> json) {
    List<String> parseList(dynamic val) {
      if (val is List) {
        return val.map((e) => e.toString()).toList();
      }
      return [];
    }

    return AdvisoryResponse(
      status: json['status']?.toString() ?? 'success',
      query: json['query']?.toString() ?? '',
      intent: json['intent']?.toString() ?? 'general',
      confidence: json['confidence'] is num ? (json['confidence'] as num).toDouble() : null,
      chunksRetrieved: json['chunks_retrieved'] is int ? json['chunks_retrieved'] : null,
      executionTime: json['execution_time'] is num ? (json['execution_time'] as num).toDouble() : null,
      entities: json['entities'] is Map ? Map<String, dynamic>.from(json['entities']) : null,
      cropRecommendation: json['crop_recommendation'] is Map 
          ? CropRecommendation.fromJson(json['crop_recommendation']) : null,
      fertilizerAdvice: json['fertilizer_advice'] is Map 
          ? FertilizerAdvice.fromJson(json['fertilizer_advice']) : null,
      diseaseAnalysis: json['disease_analysis'] is Map 
          ? DiseaseAnalysis.fromJson(json['disease_analysis']) : null,
      pestAnalysis: json['pest_analysis'] is Map 
          ? PestAnalysis.fromJson(json['pest_analysis']) : null,
      weatherInsights: json['weather_insights'] is Map 
          ? WeatherInsights.fromJson(json['weather_insights']) : null,
      marketAnalysis: json['market_price_analysis'] is Map 
          ? MarketAnalysis.fromJson(json['market_price_analysis']) : null,
      irrigationAdvice: json['irrigation_advice'] is Map 
          ? IrrigationAdvice.fromJson(json['irrigation_advice']) : null,
      cropManagement: json['crop_management'] is Map 
          ? CropManagement.fromJson(json['crop_management']) : null,
      warnings: parseList(json['warnings_and_risks']),
      nextSteps: parseList(json['next_steps']),
      rawJson: json,
    );
  }
}

class CropRecommendation {
  final String? crop;
  final String? reason;
  final double? confidence;

  CropRecommendation({this.crop, this.reason, this.confidence});

  factory CropRecommendation.fromJson(Map<String, dynamic> json) {
    return CropRecommendation(
      crop: json['crop']?.toString(),
      reason: json['reason']?.toString(),
      confidence: json['confidence'] is num ? (json['confidence'] as num).toDouble() : null,
    );
  }
}

class FertilizerAdvice {
  final List<String> recommendedFertilizers;
  final String? application;

  FertilizerAdvice({required this.recommendedFertilizers, this.application});

  factory FertilizerAdvice.fromJson(Map<String, dynamic> json) {
    List<String> list = [];
    if (json['recommended_fertilizers'] is List) {
      list = (json['recommended_fertilizers'] as List).map((e) => e.toString()).toList();
    } else if (json['recommended_fertilizers'] is String) {
      list = [json['recommended_fertilizers'].toString()];
    }
    return FertilizerAdvice(
      recommendedFertilizers: list,
      application: json['application']?.toString(),
    );
  }
}

class DiseaseAnalysis {
  final String? detectedDisease;
  final String? symptoms;
  final String? recommendation;

  DiseaseAnalysis({this.detectedDisease, this.symptoms, this.recommendation});

  factory DiseaseAnalysis.fromJson(Map<String, dynamic> json) {
    return DiseaseAnalysis(
      detectedDisease: json['detected_disease']?.toString(),
      symptoms: json['symptoms']?.toString(),
      recommendation: json['recommendation']?.toString(),
    );
  }
}

class PestAnalysis {
  final String? identifiedPest;
  final String? recommendation;

  PestAnalysis({this.identifiedPest, this.recommendation});

  factory PestAnalysis.fromJson(Map<String, dynamic> json) {
    return PestAnalysis(
      identifiedPest: json['identified_pest']?.toString(),
      recommendation: json['recommendation']?.toString(),
    );
  }
}

class WeatherInsights {
  final String? impact;
  final String? recommendation;

  WeatherInsights({this.impact, this.recommendation});

  factory WeatherInsights.fromJson(Map<String, dynamic> json) {
    return WeatherInsights(
      impact: json['impact']?.toString(),
      recommendation: json['recommendation']?.toString(),
    );
  }
}

class MarketAnalysis {
  final String? currentPrice;
  final String? recommendation;

  MarketAnalysis({this.currentPrice, this.recommendation});

  factory MarketAnalysis.fromJson(Map<String, dynamic> json) {
    return MarketAnalysis(
      currentPrice: json['current_price']?.toString(),
      recommendation: json['recommendation']?.toString(),
    );
  }
}

class IrrigationAdvice {
  final String? schedule;
  final String? recommendation;

  IrrigationAdvice({this.schedule, this.recommendation});

  factory IrrigationAdvice.fromJson(Map<String, dynamic> json) {
    return IrrigationAdvice(
      schedule: json['schedule']?.toString(),
      recommendation: json['recommendation']?.toString(),
    );
  }
}

class CropManagement {
  final String? stage;
  final String? recommendation;

  CropManagement({this.stage, this.recommendation});

  factory CropManagement.fromJson(Map<String, dynamic> json) {
    return CropManagement(
      stage: json['stage']?.toString(),
      recommendation: json['recommendation']?.toString(),
    );
  }
}
