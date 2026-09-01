from typing import Dict
import requests
import os
import time
from app.core.config import settings


class WeatherService:

    BASE_URL = "https://api.weatherapi.com/v1/forecast.json"

    # Cache weather for 15 minutes
    CACHE = {}

    CACHE_DURATION = 900

    @classmethod
    def get_weather(cls, location: str = "New Delhi") -> Dict:

        api_key = settings.WEATHER_API_KEY or os.getenv("WEATHER_API_KEY") or "59595d305ea74112b9c105207261907"

        if not api_key:

            return {
                "status": "error",
                "message": "Weather API key not configured."
            }

        location = location.strip()

        current_time = time.time()

        # =====================================================
        # Cache
        # =====================================================

        if location in cls.CACHE:

            cached = cls.CACHE[location]

            if current_time - cached["timestamp"] < cls.CACHE_DURATION:

                print(f"Using cached weather for {location}")

                return cached["data"]

        # =====================================================
        # API Call
        # =====================================================

        try:

            response = requests.get(

                cls.BASE_URL,

                params={

                    "key": api_key,

                    "q": location,

                    "days": 7,

                    "aqi": "yes",

                    "alerts": "yes"

                },

                timeout=15

            )

            response.raise_for_status()

            data = response.json()

            location_data = data["location"]

            current = data["current"]

            forecast = data["forecast"]["forecastday"]

            alerts = data.get("alerts", {}).get("alert", [])

            # =================================================
            # Agriculture Insights
            # =================================================

            rainfall_today = current["precip_mm"]

            humidity = current["humidity"]

            temperature = current["temp_c"]

            rain_probability = 0

            if forecast:

                rain_probability = int(

                    forecast[0]["day"].get(
                        "daily_chance_of_rain",
                        0
                    )

                )

            irrigation_needed = (

                rainfall_today < 2

                and rain_probability < 50

            )

            fungal_risk = "Low"

            if humidity >= 90:

                fungal_risk = "High"

            elif humidity >= 75:

                fungal_risk = "Moderate"

            heat_stress = temperature >= 38

            frost_risk = temperature <= 3

            weather_summary = {

                "status": "success",

                "location": location_data["name"],

                "region": location_data["region"],

                "country": location_data["country"],

                "latitude": location_data["lat"],

                "longitude": location_data["lon"],

                "local_time": location_data["localtime"],

                "temperature": temperature,

                "feels_like": current["feelslike_c"],

                "humidity": humidity,

                "wind_kph": current["wind_kph"],

                "wind_direction": current["wind_dir"],

                "pressure_mb": current["pressure_mb"],

                "visibility_km": current["vis_km"],

                "precipitation_mm": rainfall_today,

                "condition": current["condition"]["text"],

                "uv": current["uv"],

                "air_quality": current.get("air_quality", {}),

                "forecast": forecast,

                "alerts": alerts,

                "agriculture": {

                    "irrigation_needed": irrigation_needed,

                    "rain_probability": rain_probability,

                    "fungal_risk": fungal_risk,

                    "heat_stress": heat_stress,

                    "frost_risk": frost_risk

                }

            }

            cls.CACHE[location] = {

                "timestamp": current_time,

                "data": weather_summary

            }

            return weather_summary

        except requests.exceptions.Timeout:

            return {

                "status": "error",

                "message": "Weather API request timed out."

            }

        except requests.exceptions.HTTPError as e:

            return {

                "status": "error",

                "message": f"HTTP Error: {str(e)}"

            }

        except requests.exceptions.RequestException as e:

            return {

                "status": "error",

                "message": f"Request Error: {str(e)}"

            }

        except Exception as e:

            return {

                "status": "error",

                "message": str(e)

            }