"""
Plausibility Cross-Check Engine
Validates farmer-reported loss claims against live/historical weather data and disaster event registries.
Flags anomalies, calculates plausibility scores, and identifies fraud/mismatch risks.
"""
import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logger import logger


class PlausibilityEngine:
    """
    Evaluates reported crop damage plausibility against meteorological and disaster records.
    """

    # Reference disaster registry for known major Indian agricultural events
    HISTORICAL_DISASTER_REGISTRY = [
        {
            "event": "Cyclone Michaung",
            "type": "cyclone",
            "regions": ["chennai", "tiruvallur", "kanchipuram", "chengalpattu", "cuddalore", "nellore", "bapatla"],
            "states": ["tamil nadu", "andhra pradesh"],
            "start_date": "2023-12-01",
            "end_date": "2023-12-08",
            "characteristics": "Extreme precipitation >250mm, wind speeds >100km/h, widespread agricultural flooding."
        },
        {
            "event": "Cyclone Remal",
            "type": "cyclone",
            "regions": ["south 24 parganas", "north 24 parganas", "kolkata", "howrah", "hooghly", "coastal odisha"],
            "states": ["west bengal", "odisha"],
            "start_date": "2024-05-24",
            "end_date": "2024-05-30",
            "characteristics": "Severe cyclonic storm, heavy coastal surge, salinization of paddy fields."
        },
        {
            "event": "Marathwada & Vidarbha Drought",
            "type": "drought",
            "regions": ["beed", "dharashiv", "osmanabad", "jalna", "latur", "aurangabad", "chhatrapati sambhajinagar"],
            "states": ["maharashtra"],
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
            "characteristics": "Prolonged dry spell >45 days, groundwater deficit, crop desiccation."
        },
        {
            "event": "North India Unseasonal Hailstorm & Western Disturbance",
            "type": "hailstorm",
            "regions": ["punjab", "haryana", "sangrur", "ludhiana", "karnal", "kurukshetra", "meerut"],
            "states": ["punjab", "haryana", "uttar pradesh"],
            "start_date": "2024-03-01",
            "end_date": "2024-03-10",
            "characteristics": "Hailstorm with 20-30mm hail diameter causing lodging in mature wheat."
        },
        {
            "event": "Cauvery Delta Flash Floods / Inundation",
            "type": "flood",
            "regions": ["thanjavur", "tiruvarur", "nagapattinam", "mayiladuthurai", "cuddalore"],
            "states": ["tamil nadu"],
            "start_date": "2023-11-15",
            "end_date": "2024-01-15",
            "characteristics": "Intense localized cloudburst and riverine overflow submerging Samba paddy crop."
        }
    ]

    @classmethod
    def evaluate_claim(
        cls,
        crop: str,
        damage_type: str,
        location: str,
        event_date: Optional[str] = None,
        acres_affected: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Cross-validates reported claim against weather APIs and disaster registry.
        Returns plausibility rating, risk flags, and verification notes.
        """
        loc_clean = location.lower().strip() if location else "india"
        dmg_clean = damage_type.lower().strip() if damage_type else "general"
        crop_clean = crop.lower().strip() if crop else "crop"

        # 1. Check historical disaster registry
        registry_match = None
        for entry in cls.HISTORICAL_DISASTER_REGISTRY:
            # Check region/state match
            region_match = any(r in loc_clean for r in entry["regions"]) or any(s in loc_clean for s in entry["states"])
            type_match = entry["type"] in dmg_clean or dmg_clean in entry["type"]
            
            if region_match and type_match:
                registry_match = entry
                break
            elif region_match and dmg_clean in ["flood", "cyclone", "heavy_rainfall", "unseasonal_rain"] and entry["type"] in ["cyclone", "flood"]:
                registry_match = entry
                break

        # 2. Query Live / Historical Weather
        weather_telemetry = cls._query_weather(loc_clean)

        # 3. Compute Plausibility Matrix
        plausibility_score = 0.85
        status = "plausible"
        evidence_notes = []
        flags = []

        if registry_match:
            plausibility_score = 0.95
            status = "highly_plausible"
            evidence_notes.append(f"Direct match with documented event '{registry_match['event']}' ({registry_match['characteristics']}).")
        else:
            # Weather plausibility checks
            precip = weather_telemetry.get("precip_mm", 0.0)
            temp = weather_telemetry.get("temp_c", 28.0)
            humidity = weather_telemetry.get("humidity", 60)
            condition = weather_telemetry.get("condition", "Clear").lower()

            if any(k in dmg_clean for k in ["flood", "inundation", "excess_rain", "cyclone"]):
                if precip > 15.0 or "rain" in condition or "storm" in condition or humidity > 80:
                    plausibility_score = 0.90
                    status = "plausible"
                    evidence_notes.append(f"Recorded precipitation ({precip}mm) and high humidity ({humidity}%) support rainfall/waterlogging claim.")
                elif precip == 0.0 and humidity < 40 and "clear" in condition and not event_date:
                    plausibility_score = 0.40
                    status = "potential_mismatch"
                    flags.append("WEATHER_ANOMALY: Current telemetry shows 0mm rainfall and dry conditions in the declared region.")
                    evidence_notes.append("Requires field surveyor check or verification of exact past date rainfall logs.")
                else:
                    plausibility_score = 0.75
                    status = "plausible_with_verification"
                    evidence_notes.append(f"Weather telemetry recorded {precip}mm rainfall. Localized micro-climate inundation plausible.")

            elif any(k in dmg_clean for k in ["drought", "dry", "heat"]):
                if temp > 35.0 or humidity < 45 or precip == 0:
                    plausibility_score = 0.92
                    status = "plausible"
                    evidence_notes.append(f"High temperature ({temp}°C) and low precipitation confirm drought/moisture stress conditions.")
                else:
                    plausibility_score = 0.70
                    evidence_notes.append("Moderate temperatures recorded. Sub-soil moisture deficit should be verified via remote sensing.")

            elif any(k in dmg_clean for k in ["pest", "disease", "blast", "blight", "hopper"]):
                plausibility_score = 0.88
                status = "plausible"
                evidence_notes.append(f"Favorable conditions (Temp {temp}°C, Humidity {humidity}%) support fungal/pest multiplication.")

            else:
                plausibility_score = 0.80
                status = "plausible"
                evidence_notes.append("Reported damage category is standard under PMFBY mid-season adversity provisions.")

        # Flag for large acreage without registration
        if acres_affected and acres_affected > 20:
            flags.append("LARGE_AREA_FLAG: Affected land exceeds 20 acres; mandatory joint inspection by District Collectorate recommended.")

        return {
            "plausibility_score": round(plausibility_score, 2),
            "status": status,
            "is_mismatch": status == "potential_mismatch",
            "flags": flags,
            "evidence_notes": evidence_notes,
            "telemetry_snapshot": {
                "location": location,
                "temperature": f"{weather_telemetry.get('temp_c', 28)}°C",
                "precipitation": f"{weather_telemetry.get('precip_mm', 0)} mm",
                "condition": weather_telemetry.get("condition", "Normal"),
                "humidity": f"{weather_telemetry.get('humidity', 60)}%"
            },
            "recommendation": (
                "Proceed with standard PMFBY claim registration and assign surveyor."
                if status != "potential_mismatch" else
                "Flag for Human Officer Review: Cross-check local Mandal/Taluk rainfall station data."
            )
        }

    @classmethod
    def _query_weather(cls, location: str) -> Dict[str, Any]:
        """Fetch live weather indicators safely with fallback."""
        key = settings.WEATHER_API_KEY
        if not key or location in ["india", ""]:
            return {"temp_c": 30.0, "precip_mm": 5.0, "humidity": 65, "condition": "Partly Cloudy"}

        try:
            loc_enc = urllib.parse.quote(location)
            url = f"https://api.weatherapi.com/v1/current.json?key={key}&q={loc_enc}&aqi=no"
            req = urllib.request.Request(url, headers={"User-Agent": "StellarAgriAI/1.0"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                current = data.get("current", {})
                return {
                    "temp_c": current.get("temp_c", 28.0),
                    "precip_mm": current.get("precip_mm", 0.0),
                    "humidity": current.get("humidity", 60),
                    "condition": current.get("condition", {}).get("text", "Clear")
                }
        except Exception as e:
            logger.debug(f"Plausibility weather fetch fallback: {e}")
            return {"temp_c": 29.0, "precip_mm": 2.0, "humidity": 62, "condition": "Moderate"}
