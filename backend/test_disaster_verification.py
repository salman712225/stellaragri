import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.rag.bhuvan_service import BhuvanGeospatialService
from app.rag.open_meteo_service import OpenMeteoService
from app.rag.insurance_service import InsuranceService
from app.rag.plausibility_engine import PlausibilityEngine
from app.services.proactive_disaster_monitor import ProactiveDisasterMonitor

def run_tests():
    print("=== 1. ISRO Bhuvan Query Test ===")
    bhuvan_res = BhuvanGeospatialService.query_satellite_disaster("Cuddalore, Tamil Nadu", "flood")
    print(f"Event: {bhuvan_res.get('event_name')} | Sensor: {bhuvan_res.get('sensor')}")
    print(f"Confidence: {bhuvan_res.get('verification_confidence')} | Clause: {bhuvan_res.get('pmfby_clause')}")

    print("\n=== 2. Open-Meteo Historical Archive Test ===")
    meteo_hist = OpenMeteoService.fetch_historical_weather("Cuddalore", "2023-12-04")
    print(f"Precipitation: {meteo_hist.get('total_precipitation_mm')} mm | Heavy Rain: {meteo_hist.get('is_heavy_rain')}")

    print("\n=== 3. PMFBY Guidelines & Scheme Knowledge Test ===")
    pmfby = InsuranceService.get_scheme_overview("PMFBY")
    print(f"Scheme: {pmfby.get('name')}")
    print(f"Guidelines: {pmfby.get('guidelines_url')}")
    print(f"Downloads: {pmfby.get('downloads_url')}")
    print(f"Intimation Window: {pmfby.get('intimation_window_hours')} Hours")

    print("\n=== 4. Tri-Tier Plausibility Engine Test ===")
    # Legitimate flood claim
    legit_eval = PlausibilityEngine.evaluate_claim("Paddy", "flood", "Cuddalore, Tamil Nadu", "2023-12-04", 3.5)
    print(f"Legit Claim Score: {legit_eval.get('plausibility_score')} | Status: {legit_eval.get('status')}")

    # Fabricated drought claim in non-drought zone
    bogus_eval = PlausibilityEngine.evaluate_claim("Wheat", "drought", "New Delhi", "2024-07-15", 50.0)
    print(f"Bogus Claim Score: {bogus_eval.get('plausibility_score')} | Mismatch Flag: {bogus_eval.get('is_mismatch')} | Status: {bogus_eval.get('status')}")

    print("\n=== 5. Mode B Proactive Hazard Monitor Test ===")
    hazards = asyncio.run(ProactiveDisasterMonitor.scan_regional_hazards())
    print(f"Hazards Detected Across Districts: {len(hazards)}")
    for h in hazards:
        print(f" - [{h['severity'].upper()}] {h['district']} ({h['state']}): {h['hazard_type']} -> {h['applicable_pmfby_clause']}")

if __name__ == "__main__":
    run_tests()
