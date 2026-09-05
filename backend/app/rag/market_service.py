import os
import time
from typing import Dict

import requests


class MarketService:

    BASE_URL = os.getenv("MARKET_API_URL")

    CACHE = {}

    CACHE_DURATION = 3600      # 1 hour

    DEFAULT_BENCHMARK = {
        "rice": {
            "status": "success",
            "crop": "Rice (Paddy)",
            "market": "APMC Mandi",
            "district": "Regional Market",
            "state": "National Market",
            "modal_price": "₹2,200 / quintal",
            "min_price": "₹2,040 / quintal",
            "max_price": "₹2,350 / quintal",
            "arrival": "150 Quintals"
        },
        "paddy": {
            "status": "success",
            "crop": "Rice (Paddy)",
            "market": "APMC Mandi",
            "district": "Regional Market",
            "state": "National Market",
            "modal_price": "₹2,200 / quintal",
            "min_price": "₹2,040 / quintal",
            "max_price": "₹2,350 / quintal",
            "arrival": "150 Quintals"
        },
        "wheat": {
            "status": "success",
            "crop": "Wheat",
            "market": "APMC Mandi",
            "district": "Regional Market",
            "state": "National Market",
            "modal_price": "₹2,275 / quintal",
            "min_price": "₹2,125 / quintal",
            "max_price": "₹2,400 / quintal",
            "arrival": "180 Quintals"
        },
        "maize": {
            "status": "success",
            "crop": "Maize",
            "market": "APMC Mandi",
            "district": "Regional Market",
            "state": "National Market",
            "modal_price": "₹2,090 / quintal",
            "min_price": "₹1,950 / quintal",
            "max_price": "₹2,250 / quintal",
            "arrival": "110 Quintals"
        },
        "cotton": {
            "status": "success",
            "crop": "Cotton",
            "market": "APMC Mandi",
            "district": "Regional Market",
            "state": "National Market",
            "modal_price": "₹6,620 / quintal",
            "min_price": "₹6,200 / quintal",
            "max_price": "₹7,100 / quintal",
            "arrival": "85 Quintals"
        },
        "tomato": {
            "status": "success",
            "crop": "Tomato",
            "market": "Local Mandi",
            "district": "Regional Market",
            "state": "National Market",
            "modal_price": "₹2,400 / quintal",
            "min_price": "₹1,800 / quintal",
            "max_price": "₹3,200 / quintal",
            "arrival": "65 Quintals"
        },
        "potato": {
            "status": "success",
            "crop": "Potato",
            "market": "Local Mandi",
            "district": "Regional Market",
            "state": "National Market",
            "modal_price": "₹1,500 / quintal",
            "min_price": "₹1,200 / quintal",
            "max_price": "₹1,800 / quintal",
            "arrival": "140 Quintals"
        }
    }

    @classmethod
    def get_market_price(
        cls,
        crop: str,
        state: str = "",
        district: str = ""
    ) -> Dict:

        crop_key = (crop or "").lower().strip()

        if not cls.BASE_URL:
            if crop_key in cls.DEFAULT_BENCHMARK:
                res = dict(cls.DEFAULT_BENCHMARK[crop_key])
                if state:
                    res["state"] = state
                if district:
                    res["district"] = district
                return res
            return {
                "status": "success",
                "crop": crop.title() if crop else "Crop",
                "market": "Regional Mandi",
                "district": district or "Regional Market",
                "state": state or "National Market",
                "modal_price": "₹2,200 / quintal",
                "min_price": "₹2,000 / quintal",
                "max_price": "₹2,400 / quintal",
                "arrival": "100 Quintals"
            }

        cache_key = (
            crop.lower(),
            state.lower(),
            district.lower()
        )

        current_time = time.time()

        # =====================================================
        # Cache
        # =====================================================

        if cache_key in cls.CACHE:

            cached = cls.CACHE[cache_key]

            if current_time - cached["timestamp"] < cls.CACHE_DURATION:

                print(f"Using cached market data for {crop}")

                return cached["data"]

        try:

            params = {
                "commodity": crop
            }

            if state:
                params["state"] = state

            if district:
                params["district"] = district

            response = requests.get(
                cls.BASE_URL,
                params=params,
                timeout=15
            )

            response.raise_for_status()

            records = response.json()

            if not records:

                return {
                    "status": "not_found",
                    "message": f"No market data found for {crop}."
                }

            # =================================================
            # Sort by modal price
            # =================================================

            records.sort(
                key=lambda x: float(
                    x.get("modal_price", 0)
                ),
                reverse=True
            )

            best_market = records[0]

            prices = []

            for record in records:

                try:
                    prices.append(
                        float(record.get("modal_price", 0))
                    )
                except Exception:
                    pass

            average_price = (
                round(sum(prices) / len(prices), 2)
                if prices
                else 0
            )

            highest_price = max(prices) if prices else 0

            lowest_price = min(prices) if prices else 0

            recommendation = "Average"

            if float(best_market.get("modal_price", 0)) >= average_price:

                recommendation = "Good Time to Sell"

            if float(best_market.get("modal_price", 0)) >= highest_price * 0.95:

                recommendation = "Excellent Time to Sell"

            result = {

                "status": "success",

                "crop": crop,

                "market": best_market.get("market"),

                "district": best_market.get("district"),

                "state": best_market.get("state"),

                "modal_price": best_market.get("modal_price"),

                "min_price": best_market.get("min_price"),

                "max_price": best_market.get("max_price"),

                "arrival": best_market.get("arrival"),

                "analysis": {

                    "average_price": average_price,

                    "highest_price": highest_price,

                    "lowest_price": lowest_price,

                    "markets_available": len(records),

                    "selling_recommendation": recommendation

                },

                "top_markets": [

                    {

                        "market": r.get("market"),

                        "district": r.get("district"),

                        "state": r.get("state"),

                        "modal_price": r.get("modal_price")

                    }

                    for r in records[:5]

                ]

            }

            cls.CACHE[cache_key] = {

                "timestamp": current_time,

                "data": result

            }

            return result

        except requests.exceptions.Timeout:

            return {

                "status": "error",

                "message": "Market API request timed out."

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