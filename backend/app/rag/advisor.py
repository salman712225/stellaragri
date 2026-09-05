from typing import Dict


class AgricultureAdvisor:

    SYSTEM_PROMPT = """
You are Stellar Agri AI, an expert agricultural scientist, agronomist, crop protection specialist, and certified crop insurance (PMFBY) specialist.

You help farmers using four knowledge sources:

1. Retrieved Agricultural Knowledge (RAG)
2. PMFBY Crop Insurance & Loss Guidelines
3. Live Weather Information
4. Live Market Information

STRICT RULES

1. Use ONLY the provided information.
2. Never invent facts.
3. Never guess crop names, diseases, pests, fertilizers or prices.
4. If information is unavailable, return null.
5. Never contradict the retrieved agricultural knowledge.
6. Weather should influence recommendations only when relevant.
7. Market information should be used only when relevant.
8. Explain WHY every recommendation is made.
9. Keep responses practical and farmer-friendly.
10. Return ONLY valid JSON.
11. Never use markdown.
12. PMFBY & INSURANCE GUARDRAILS: If the farmer asks about crop loss, damage, flood, cyclone, drought, hail, or insurance claims, provide clear PMFBY intimation steps (72-hour mandatory intimation, 5 required evidence records: Patta/Chitta, Sowing certificate, Aadhaar, Bank passbook, Geo-tagged photos). NEVER guarantee claim approval, payout amounts, or timelines.
"""

    @staticmethod
    def build_prompt(context: Dict):

        prompt = []

        # =====================================================
        # Question
        # =====================================================

        prompt.append("=" * 70)
        prompt.append("FARMER QUESTION")
        prompt.append("=" * 70)
        prompt.append(context["question"])

        # =====================================================
        # Intent
        # =====================================================

        prompt.append("\n" + "=" * 70)
        prompt.append("DETECTED INTENT")
        prompt.append("=" * 70)
        prompt.append(context["intent"])

        # =====================================================
        # Confidence
        # =====================================================

        prompt.append("\n" + "=" * 70)
        prompt.append("INTENT CONFIDENCE")
        prompt.append("=" * 70)
        prompt.append(str(context["confidence"]))

        # =====================================================
        # Entities
        # =====================================================

        prompt.append("\n" + "=" * 70)
        prompt.append("DETECTED ENTITIES")
        prompt.append("=" * 70)

        for key, value in context["entities"].items():

            if value in [None, "", [], {}]:
                continue

            prompt.append(f"{key}: {value}")

        # =====================================================
        # Agricultural Knowledge
        # =====================================================

        grouped = {}

        for item in context["knowledge"]:
            grouped.setdefault(item["dataset"], []).append(item)

        titles = {
            "crop": "CROP RECOMMENDATION",
            "fertilizer": "FERTILIZER KNOWLEDGE",
            "disease": "DISEASE KNOWLEDGE",
            "pest": "PEST KNOWLEDGE",
            "management": "CROP MANAGEMENT",
            "general": "GENERAL KNOWLEDGE"
        }

        prompt.append("\n")
        prompt.append("=" * 70)
        prompt.append("RETRIEVED AGRICULTURAL KNOWLEDGE")
        prompt.append("=" * 70)

        for dataset in [
            "crop",
            "fertilizer",
            "disease",
            "pest",
            "management",
            "general"
        ]:

            if dataset not in grouped:
                continue

            prompt.append("\n" + "-" * 70)
            prompt.append(titles.get(dataset, dataset.upper()))
            prompt.append("-" * 70)

            for item in grouped[dataset]:

                prompt.append(f"\nSource : {item['source']}")
                prompt.append(f"Similarity Score : {item['score']}")
                prompt.append(item["content"])

        # =====================================================
        # PMFBY & Crop Insurance Scheme Knowledge
        # =====================================================
        from app.rag.insurance_service import InsuranceService
        q_text = context.get("question", "").lower()
        if context.get("intent") == "insurance_claim" or any(w in q_text for w in ["insurance", "pmfby", "claim", "damage", "loss", "cyclone", "flood", "drought", "bima"]):
            prompt.append("\n")
            prompt.append("=" * 70)
            prompt.append("GOVERNMENT CROP INSURANCE (PMFBY) GUIDELINES & EVIDENCE")
            prompt.append("=" * 70)
            prompt.append(InsuranceService.format_scheme_context_for_llm())

        # =====================================================
        # Weather
        # =====================================================

        weather = context.get("weather", {})

        if weather.get("status") == "success":

            prompt.append("\n")
            prompt.append("=" * 70)
            prompt.append("LIVE WEATHER INFORMATION")
            prompt.append("=" * 70)

            prompt.append(f"Location : {weather.get('location')}")
            prompt.append(f"Temperature : {weather.get('temperature')} °C")
            prompt.append(f"Humidity : {weather.get('humidity')} %")
            prompt.append(f"Condition : {weather.get('condition')}")
            prompt.append(f"Rainfall : {weather.get('precipitation_mm')} mm")
            prompt.append(f"Wind Speed : {weather.get('wind_kph')} km/h")
            prompt.append(f"UV Index : {weather.get('uv')}")

            forecast = weather.get("forecast", [])

            if forecast:

                prompt.append("\n7 DAY FORECAST")

                for day in forecast:

                    d = day.get("day", {})

                    prompt.append(
                        f"{day.get('date')} | "
                        f"{d.get('condition', {}).get('text')} | "
                        f"Max {d.get('maxtemp_c')}°C | "
                        f"Min {d.get('mintemp_c')}°C | "
                        f"Rain Chance {d.get('daily_chance_of_rain')}%"
                    )

        # =====================================================
        # Market
        # =====================================================

        market = context.get("market", {})

        if market.get("status") == "success":

            prompt.append("\n")
            prompt.append("=" * 70)
            prompt.append("LIVE MARKET INFORMATION")
            prompt.append("=" * 70)

            prompt.append(f"Crop : {market.get('crop')}")
            prompt.append(f"Market : {market.get('market')}")
            prompt.append(f"District : {market.get('district')}")
            prompt.append(f"State : {market.get('state')}")
            prompt.append(f"Minimum Price : {market.get('min_price')}")
            prompt.append(f"Maximum Price : {market.get('max_price')}")
            prompt.append(f"Modal Price : {market.get('modal_price')}")
            prompt.append(f"Arrival : {market.get('arrival')}")

        # =====================================================
        # Instructions
        # =====================================================

        prompt.append("""

======================================================================
TASK
======================================================================

Answer the farmer's question using ONLY the provided information.

Reasoning Rules

1. Prioritize Retrieved Agricultural Knowledge.
2. Use Weather Information only if it affects the recommendation.
3. Use Market Information only if it helps answer the question.
4. Never invent missing information.
5. Explain WHY every recommendation is given.
6. Mention possible risks if relevant.
7. If rainfall is expected soon, mention its impact on irrigation or fertilizer application.
8. If market prices are available, explain whether selling appears favorable based ONLY on the provided prices.
9. When asked if a farmer can sow/plant a crop today, synthesize available crop management practices (land preparation, seed treatment, sowing) together with live weather forecast (temperature and rain chance) to provide clear, practical sowing advice.
10. Keep answers concise, direct, and farmer-friendly. Avoid repeating disclaimers.

Return ONLY valid JSON.

{
    "summary": "",

    "intent": "",

    "confidence": 0,

    "answer": [],

    "crop_recommendation": {
        "crop": null,
        "confidence": null,
        "reason": null
    },

    "disease_analysis": {
        "disease": null,
        "symptoms": [],
        "recommendation": null
    },

    "pest_analysis": {
        "pest": null,
        "recommendation": null
    },

    "fertilizer_advice": {
        "recommended": [],
        "application": null
    },

    "irrigation_advice": {
        "schedule": null,
        "recommendation": null
    },

    "crop_management": {
        "growth_stage": null,
        "recommendation": null
    },

    "weather_analysis": {
        "impact": null,
        "recommendation": null
    },

    "market_analysis": {
        "current_price": null,
        "recommendation": null
    },

    "warnings": [],

    "next_steps": []
}

Return ONLY JSON.
""")

        return "\n".join(prompt)