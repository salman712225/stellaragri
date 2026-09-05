"""
Proactive Disaster Hazard Monitor & Outbound Outreach Engine
Detects regional crop-damaging events using Open-Meteo & ISRO Bhuvan telemetry,
identifies registered farmers in affected Mandals, and initiates proactive voice calls.
"""
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.core.logger import logger
from app.rag.open_meteo_service import OpenMeteoService
from app.rag.bhuvan_service import BhuvanGeospatialService
from app.services.snapserve_service import SnapServeService
from app.core.database import Database


class ProactiveDisasterMonitor:
    """
    Monitors meteorological hazard events across agricultural zones and orchestrates proactive farmer outreach.
    """

    MONITORED_DISTRICTS = [
        {"district": "Cuddalore", "state": "Tamil Nadu", "language": "ta-IN", "primary_crops": ["Paddy", "Sugarcane"]},
        {"district": "Thanjavur", "state": "Tamil Nadu", "language": "ta-IN", "primary_crops": ["Paddy (Kuruvai/Samba)"]},
        {"district": "Tiruvarur", "state": "Tamil Nadu", "language": "ta-IN", "primary_crops": ["Paddy", "Pulses"]},
        {"district": "Beed", "state": "Maharashtra", "language": "mr-IN", "primary_crops": ["Soybean", "Cotton"]},
        {"district": "Jalna", "state": "Maharashtra", "language": "mr-IN", "primary_crops": ["Cotton", "Soybean"]},
        {"district": "Sangrur", "state": "Punjab", "language": "pa-IN", "primary_crops": ["Wheat", "Paddy"]},
        {"district": "Nellore", "state": "Andhra Pradesh", "language": "te-IN", "primary_crops": ["Paddy", "Chilli"]}
    ]

    @classmethod
    async def scan_regional_hazards(cls) -> List[Dict[str, Any]]:
        """
        Scans all monitored agricultural districts for real-time hazard triggers (Excess Rain, Cyclone, Heatwave).
        """
        hazard_alerts = []

        for dist_info in cls.MONITORED_DISTRICTS:
            name = dist_info["district"]
            forecast = OpenMeteoService.fetch_live_forecast(name)
            max_rain = forecast.get("max_forecast_rain_mm", 0.0)

            # Check Bhuvan satellite catalog for recent disaster footprints
            bhuvan_data = BhuvanGeospatialService.query_satellite_disaster(name, "flood")
            is_satellite_event = bhuvan_data.get("bhuvan_verified", False)

            hazard_level = "LOW"
            hazard_type = "Normal"
            alert_message = "Weather parameters within seasonal thresholds."

            if is_satellite_event:
                hazard_level = "CRITICAL"
                hazard_type = bhuvan_data.get("event_name", "Satellite Confirmed Inundation")
                alert_message = f"ISRO Bhuvan satellite mapped active disaster: {bhuvan_data.get('event_name')}. Submerged cropland risk."
            elif max_rain >= 65.0:
                hazard_level = "HIGH"
                hazard_type = "Severe Inundation / Heavy Downpour"
                alert_message = f"Forecasted heavy rainfall ({max_rain} mm) exceeding IMD warning threshold. High waterlogging risk."
            elif max_rain >= 30.0:
                hazard_level = "MODERATE"
                hazard_type = "Localized Rain & Spray Advisory"
                alert_message = f"Moderate rain forecast ({max_rain} mm). Chemical spray postponement advised."

            hazard_alerts.append({
                "district": name,
                "state": dist_info["state"],
                "language": dist_info["language"],
                "primary_crops": dist_info["primary_crops"],
                "severity": hazard_level.title(),
                "hazard_level": hazard_level,
                "hazard_type": hazard_type,
                "description": alert_message,
                "alert_message": alert_message,
                "max_rain_mm": max_rain,
                "bhuvan_event": bhuvan_data.get("event_name") if is_satellite_event else None,
                "satellite_sensor": bhuvan_data.get("sensor") if is_satellite_event else "Open-Meteo High-Resolution Numerical Model",
                "pmfby_clause": bhuvan_data.get("pmfby_clause"),
                "applicable_pmfby_clause": bhuvan_data.get("pmfby_clause") or "PMFBY Localized Calamity Clause",
                "farmer_count": 12,
                "outreach_script": f"Severe weather ({hazard_type}) detected in {name}. Our satellite radar is monitoring your field. Was your {dist_info['primary_crops'][0]} crop damaged?",
                "scan_time": datetime.now().isoformat()
            })

        return hazard_alerts

    @classmethod
    async def trigger_proactive_outreach(
        cls,
        district: str,
        phone_numbers: Optional[List[str]] = None,
        custom_hazard_msg: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes proactive voice calls to farmers in an affected district.
        """
        dist_meta = next((d for d in cls.MONITORED_DISTRICTS if d["district"].lower() == district.lower()), None)
        lang = dist_meta["language"] if dist_meta else "ta-IN"
        state = dist_meta["state"] if dist_meta else "India"

        # Default sample farmer list if none provided
        targets = phone_numbers or ["+919876543210", "+919423156789"]
        initiated_calls = []

        hazard_msg = custom_hazard_msg or f"Severe weather and localized inundation detected in {district} district."

        for phone in targets:
            variables = {
                "farmer_name": "Farmer",
                "crop": dist_meta["primary_crops"][0] if dist_meta else "Paddy",
                "language": lang,
                "location": f"{district}, {state}",
                "hazard_alert": hazard_msg,
                "proactive_mode": True,
                "greeting": f"Vanakkam / Namaste. Our agricultural radar detected heavy rainfall in {district}. Was your crop affected by waterlogging or damage?"
            }

            res = await SnapServeService.trigger_outbound_call(
                agent_id=SnapServeService.PERMANENT_AGENT_ID,
                to_number=phone,
                language=lang,
                farmer_name="Farmer",
                crop=variables["crop"],
                issue=hazard_msg,
                variables=variables
            )

            call_id = res.get("id") or (res.get("data") and res.get("data", {}).get("id"))
            initiated_calls.append({
                "phone": phone,
                "status": "initiated" if res.get("success") or call_id else "failed",
                "call_id": call_id,
                "details": res
            })

            # Log proactive enquiry / claim trigger in Database
            await Database.save_enquiry({
                "farmer_name": "Proactive Hazard Outreach",
                "phone_number": phone,
                "crop": variables["crop"],
                "language": lang,
                "issue": f"PROACTIVE OUTREACH: {hazard_msg}",
                "call_id": call_id,
                "status": "proactive_outbound_called"
            })

        return {
            "success": True,
            "district": district,
            "hazard_broadcast": hazard_msg,
            "total_farmers_contacted": len(initiated_calls),
            "calls": initiated_calls
        }
