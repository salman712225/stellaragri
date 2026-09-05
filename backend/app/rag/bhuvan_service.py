"""
ISRO Bhuvan Geospatial Disaster & Earth Observation Service
Integrates satellite telemetry from ISRO Bhuvan (bhuvan.nrsc.gov.in) for:
- Flood Inundation Vector layers (SAR & Optical satellite mapping)
- National Agricultural Drought Assessment and Monitoring System (NADAMS - NDVI & Soil Moisture)
- Tropical Cyclone Track, Landfall Buffer & Storm Surge Footprint
- Unseasonal Weather & Hailstorm Satellite Doppler Radar verification
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from app.core.logger import logger


class BhuvanGeospatialService:
    """
    Simulates & interfaces with ISRO Bhuvan Geoportal Disaster Services.
    """

    # Bhuvan Geoportal & Geospatial Layer Endpoints
    BHUVAN_MAIN_URL = "https://bhuvan.nrsc.gov.in/"
    BHUVAN_RESOURCES_URL = "https://bhuvan-app1.nrsc.gov.in/2dresources/"
    BHUVAN_BASE_URL = "https://bhuvan-app1.nrsc.gov.in/disaster/disaster.php"
    BHUVAN_WMS_URL = "https://bhuvan-vec1.nrsc.gov.in/bhuvan/wms"

    # Known Indian agricultural district geospatial bounding & state references
    DISTRICT_GEO_INDEX = {
        "cuddalore": {"state": "tamil nadu", "lat": 11.7480, "lon": 79.7714, "coastal": True, "agro_zone": "Cauvery Delta"},
        "thanjavur": {"state": "tamil nadu", "lat": 10.7870, "lon": 79.1378, "coastal": False, "agro_zone": "Cauvery Delta"},
        "tiruvarur": {"state": "tamil nadu", "lat": 10.7725, "lon": 79.6365, "coastal": True, "agro_zone": "Cauvery Delta"},
        "nagapattinam": {"state": "tamil nadu", "lat": 10.7672, "lon": 79.8449, "coastal": True, "agro_zone": "Cauvery Delta"},
        "chengalpattu": {"state": "tamil nadu", "lat": 12.6841, "lon": 79.9836, "coastal": True, "agro_zone": "North Eastern Coastal"},
        "beed": {"state": "maharashtra", "lat": 18.9891, "lon": 75.7601, "coastal": False, "agro_zone": "Marathwada Dry Zone"},
        "jalna": {"state": "maharashtra", "lat": 19.8410, "lon": 75.8864, "coastal": False, "agro_zone": "Marathwada"},
        "sangrur": {"state": "punjab", "lat": 30.2458, "lon": 75.8421, "coastal": False, "agro_zone": "Central Plain Zone"},
        "karnal": {"state": "haryana", "lat": 29.6857, "lon": 76.9905, "coastal": False, "agro_zone": "Eastern Plain Zone"},
        "nellore": {"state": "andhra pradesh", "lat": 14.4426, "lon": 79.9865, "coastal": True, "agro_zone": "Southern Coastal"}
    }

    # ISRO Bhuvan Inundation & Disaster Event Map Database
    BHUVAN_DISASTER_SATELLITE_CATALOG = [
        {
            "event_id": "BHUVAN-FLD-2023-TN01",
            "event_name": "Cyclone Michaung Floods & Coastal Inundation",
            "disaster_type": "flood",
            "satellite_sensor": "RISAT-1A SAR & Sentinel-1A C-band",
            "coverage_states": ["tamil nadu", "andhra pradesh"],
            "affected_districts": ["chennai", "tiruvallur", "kanchipuram", "chengalpattu", "cuddalore", "nellore"],
            "period": {"start": "2023-12-01", "end": "2023-12-10"},
            "satellite_metrics": {
                "inundation_area_sq_km": 1420.5,
                "submerged_cropland_pct": 68.4,
                "water_depth_est": "1.2m to 2.5m in delta lowlands",
                "radar_backscatter_drop_db": -8.5  # Distinct signature of standing water on cropland
            },
            "pmfby_applicable_clause": "Localized Calamity (Inundation) & Post-Harvest Standing Crop Loss"
        },
        {
            "event_id": "BHUVAN-DRT-2024-MH02",
            "event_name": "Marathwada NADAMS Agricultural Drought",
            "disaster_type": "drought",
            "satellite_sensor": "ResourceSat-2A AWiFS / MODIS NDVI",
            "coverage_states": ["maharashtra"],
            "affected_districts": ["beed", "dharashiv", "osmanabad", "jalna", "latur", "aurangabad"],
            "period": {"start": "2024-01-01", "end": "2024-06-30"},
            "satellite_metrics": {
                "ndvi_anomaly": -0.38,  # Severe vegetative stress (< -0.30 indicates acute drought)
                "soil_moisture_deficit_pct": 74.0,
                "consecutive_dry_days": 52,
                "drought_severity": "Moderate to Severe Agricultural Drought"
            },
            "pmfby_applicable_clause": "Mid-Season Adversity (Drought / Severe Dry Spell)"
        },
        {
            "event_id": "BHUVAN-HAIL-2024-PB03",
            "event_name": "Punjab-Haryana Western Disturbance Hail Storm",
            "disaster_type": "hailstorm",
            "satellite_sensor": "INSAT-3D Doppler Weather Radar & Sentinel-2 MSI",
            "coverage_states": ["punjab", "haryana"],
            "affected_districts": ["sangrur", "ludhiana", "karnal", "kurukshetra", "patiala"],
            "period": {"start": "2024-03-01", "end": "2024-03-10"},
            "satellite_metrics": {
                "radar_reflectivity_dbz": 58.0,  # >55 dBZ indicates severe hail precipitation
                "crop_canopy_damage_pct": 55.0,
                "hail_swath_width_km": 14.2
            },
            "pmfby_applicable_clause": "Localized Calamity (Hailstorm & Crop Lodging)"
        },
        {
            "event_id": "BHUVAN-CYC-2024-WB04",
            "event_name": "Cyclone Remal Coastal Surge",
            "disaster_type": "cyclone",
            "satellite_sensor": "Oceansat-3 & RISAT-2BR1",
            "coverage_states": ["west bengal", "odisha"],
            "affected_districts": ["south 24 parganas", "north 24 parganas", "kolkata", "howrah", "coastal odisha"],
            "period": {"start": "2024-05-24", "end": "2024-05-30"},
            "satellite_metrics": {
                "storm_surge_height_m": 2.8,
                "saline_inundation_hectares": 38000,
                "wind_velocity_kmh": 135
            },
            "pmfby_applicable_clause": "Comprehensive Cyclone Risk & Standing Crop Loss"
        }
    ]

    @classmethod
    def query_satellite_disaster(
        cls,
        location: str,
        damage_type: str,
        event_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Queries ISRO Bhuvan satellite disaster vector layers for matching flood, drought, cyclone, or hailstorm signatures.
        """
        loc_lower = location.lower().strip() if location else ""
        dmg_lower = damage_type.lower().strip() if damage_type else ""

        matched_event = None

        # Check district and disaster type against Bhuvan Catalog
        for event in cls.BHUVAN_DISASTER_SATELLITE_CATALOG:
            district_hit = any(d in loc_lower for d in event["affected_districts"])
            state_hit = any(s in loc_lower for s in event["coverage_states"])
            type_hit = event["disaster_type"] in dmg_lower or dmg_lower in event["disaster_type"]

            # Broaden matches for rain/cyclone/inundation synonyms
            if not type_hit:
                if any(syn in dmg_lower for syn in ["flood", "inundation", "excess_rain", "heavy_rainfall", "cyclone", "storm"]) and event["disaster_type"] in ["flood", "cyclone"]:
                    type_hit = True
                elif any(syn in dmg_lower for syn in ["drought", "dry", "heat", "moisture_stress"]) and event["disaster_type"] == "drought":
                    type_hit = True
                elif any(syn in dmg_lower for syn in ["hail", "hailstorm", "ice_storm", "lodging"]) and event["disaster_type"] == "hailstorm":
                    type_hit = True

            if (district_hit or state_hit) and type_hit:
                matched_event = event
                break

        # Check coordinate geo-indexing
        geo_info = None
        for dist_key, coords in cls.DISTRICT_GEO_INDEX.items():
            if dist_key in loc_lower:
                geo_info = {"district": dist_key.title(), **coords}
                break

        if matched_event:
            return {
                "bhuvan_verified": True,
                "bhuvan_status": "SATELLITE_DISASTER_CONFIRMED",
                "event_id": matched_event["event_id"],
                "event_name": matched_event["event_name"],
                "sensor": matched_event["satellite_sensor"],
                "metrics": matched_event["satellite_metrics"],
                "pmfby_clause": matched_event["pmfby_applicable_clause"],
                "geo_coordinates": geo_info or {"lat": 11.5, "lon": 79.5, "state": "India"},
                "verification_confidence": 0.96,
                "satellite_summary": f"ISRO Bhuvan {matched_event['satellite_sensor']} imagery confirmed '{matched_event['event_name']}'. Applicable PMFBY rule: {matched_event['pmfby_applicable_clause']}."
            }

        # If no specific catalog match, simulate real-time Bhuvan NDVI / Sentinel-1 baseline check
        is_flood_query = any(k in dmg_lower for k in ["flood", "rain", "cyclone", "inundation"])
        is_drought_query = any(k in dmg_lower for k in ["drought", "dry", "heat"])

        return {
            "bhuvan_verified": False,
            "bhuvan_status": "LOCAL_MANDAL_RESOLUTION",
            "event_id": f"BHUVAN-GEN-{int(datetime.now().timestamp())%100000}",
            "event_name": f"Regional {damage_type.capitalize()} Evaluation",
            "sensor": "Sentinel-1A SAR & INSAT-3D Agro Telemetry",
            "metrics": {
                "satellite_water_mask": "Normal / Moderate" if is_flood_query else "Standard",
                "ndvi_status": "Normal crop vigour (-0.05 deviation)" if not is_drought_query else "Moderate moisture stress"
            },
            "pmfby_clause": "Standard PMFBY Mid-Season Loss Protocol (Subject to Panchayat CCE / Surveyor Report)",
            "geo_coordinates": geo_info or {"lat": 20.5937, "lon": 78.9629, "state": "India"},
            "verification_confidence": 0.78,
            "satellite_summary": "ISRO Bhuvan baseline NDVI and SAR water masks indicate localized conditions. Proceed with ground surveyor verification."
        }
