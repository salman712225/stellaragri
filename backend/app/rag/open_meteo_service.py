"""
Open-Meteo Weather & Historical Meteorological Archive Service
Docs: https://open-meteo.com/en/docs
Forecast API: https://api.open-meteo.com/v1/forecast
Historical API: https://archive-api.open-meteo.com/v1/archive
Auth: No API key required for public agricultural verification usage.
"""
import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from app.core.logger import logger


class OpenMeteoService:
    """
    Interfaces with Open-Meteo Forecast & Historical Archive APIs for agricultural disaster validation.
    """

    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

    # Default Indian district geo-coordinates lookup table
    DISTRICT_COORDINATES = {
        "cuddalore": (11.7480, 79.7714),
        "thanjavur": (10.7870, 79.1378),
        "tiruvarur": (10.7725, 79.6365),
        "nagapattinam": (10.7672, 79.8449),
        "chennai": (13.0827, 80.2707),
        "tiruvallur": (13.1438, 79.9080),
        "kanchipuram": (12.8342, 79.7036),
        "beed": (18.9891, 75.7601),
        "jalna": (19.8410, 75.8864),
        "latur": (18.4088, 76.5604),
        "sangrur": (30.2458, 75.8421),
        "ludhiana": (30.9010, 75.8573),
        "karnal": (29.6857, 76.9905),
        "nellore": (14.4426, 79.9865),
        "bapatla": (15.9042, 80.4674),
        "new delhi": (28.6139, 77.2090),
        "jaipur": (26.9124, 75.7873),
        "patna": (25.5941, 85.1376)
    }

    @classmethod
    def get_coordinates(cls, location: str) -> tuple[float, float]:
        """Resolves district/city name to (latitude, longitude)."""
        loc_clean = location.lower().strip()
        for district, coords in cls.DISTRICT_COORDINATES.items():
            if district in loc_clean:
                return coords
        # Default to Central India
        return (20.5937, 78.9629)

    @classmethod
    def fetch_historical_weather(
        cls,
        location: str,
        start_date: str,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Queries Open-Meteo Historical Archive API (archive-api.open-meteo.com) for past weather on the claimed disaster date.
        """
        lat, lon = cls.get_coordinates(location)
        target_end = end_date or start_date

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": target_end,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,wind_speed_10m_max,wind_gusts_10m_max",
            "timezone": "Asia/Kolkata"
        }

        query_string = urllib.parse.urlencode(params)
        url = f"{cls.ARCHIVE_URL}?{query_string}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "StellarAgriAI-OpenMeteo/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                daily = data.get("daily", {})
                
                precip_list = daily.get("precipitation_sum", [0.0])
                total_precip = sum([p for p in precip_list if p is not None])
                max_wind = max(daily.get("wind_gusts_10m_max", [0.0]) or [0.0])
                max_temp = max(daily.get("temperature_2m_max", [28.0]) or [28.0])

                return {
                    "source": "Open-Meteo Historical Weather Archive",
                    "status": "success",
                    "latitude": lat,
                    "longitude": lon,
                    "start_date": start_date,
                    "end_date": target_end,
                    "total_precipitation_mm": round(total_precip, 1),
                    "max_wind_gust_kmh": round(max_wind, 1),
                    "max_temperature_c": round(max_temp, 1),
                    "is_heavy_rain": total_precip >= 64.5,  # IMD heavy rain threshold: >64.5mm/day
                    "is_cyclonic_wind": max_wind >= 62.0,   # Deep depression/cyclone threshold
                    "raw_daily": daily
                }
        except Exception as e:
            logger.warning(f"Open-Meteo Historical Archive query fallback: {e}")
            return {
                "source": "Open-Meteo Historical Weather Archive",
                "status": "fallback",
                "latitude": lat,
                "longitude": lon,
                "total_precipitation_mm": 12.0,
                "max_wind_gust_kmh": 25.0,
                "max_temperature_c": 32.0,
                "is_heavy_rain": False,
                "is_cyclonic_wind": False
            }

    @classmethod
    def fetch_live_forecast(cls, location: str) -> Dict[str, Any]:
        """
        Queries Open-Meteo Live Forecast API (api.open-meteo.com) for real-time hazard detection.
        """
        lat, lon = cls.get_coordinates(location)
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
            "timezone": "Asia/Kolkata",
            "forecast_days": 7
        }

        query_string = urllib.parse.urlencode(params)
        url = f"{cls.FORECAST_URL}?{query_string}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "StellarAgriAI-OpenMeteo/1.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                daily = data.get("daily", {})
                
                precip_sums = daily.get("precipitation_sum", [])
                max_rain_forecast = max(precip_sums) if precip_sums else 0.0

                return {
                    "source": "Open-Meteo Live Forecast API",
                    "status": "success",
                    "latitude": lat,
                    "longitude": lon,
                    "max_forecast_rain_mm": round(max_rain_forecast, 1),
                    "hazard_detected": max_rain_forecast >= 50.0,
                    "forecast_daily": daily
                }
        except Exception as e:
            logger.warning(f"Open-Meteo Forecast query fallback: {e}")
            return {
                "source": "Open-Meteo Live Forecast API",
                "status": "fallback",
                "max_forecast_rain_mm": 5.0,
                "hazard_detected": False
            }
