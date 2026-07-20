from collections import defaultdict
from typing import Dict, List


class ContextBuilder:

    MAX_CHUNKS_PER_DATASET = 3

    # ==========================================================
    # Build Structured Context
    # ==========================================================

    @staticmethod
    def build(
        query_result,
        rag_chunks: List[Dict],
        weather_data: Dict | None = None,
        market_data: Dict | None = None
    ) -> Dict:

        context = {
            "question": query_result.original_query,
            "intent": query_result.intent,
            "confidence": query_result.confidence,
            "entities": query_result.entities,
            "knowledge": [],
            "weather": weather_data or {},
            "market": market_data or {}
        }

        grouped = defaultdict(list)
        seen = set()

        # -----------------------------------------------
        # Remove duplicate chunks
        # -----------------------------------------------

        for chunk in rag_chunks:

            text = chunk.get("text", "").strip()

            if not text:
                continue

            if text in seen:
                continue

            seen.add(text)

            dataset = chunk.get("dataset", "general")

            grouped[dataset].append(
                {
                    "dataset": dataset,
                    "source": chunk.get("source", ""),
                    "score": round(chunk.get("score", 0), 3),
                    "content": text
                }
            )

        # -----------------------------------------------
        # Highest scored chunks first
        # -----------------------------------------------

        for dataset in grouped:

            grouped[dataset] = sorted(
                grouped[dataset],
                key=lambda x: x["score"],
                reverse=True
            )[:ContextBuilder.MAX_CHUNKS_PER_DATASET]

            context["knowledge"].extend(grouped[dataset])

        return context

    # ==========================================================
    # Format Context For LLM
    # ==========================================================

    @staticmethod
    def format_for_llm(context: Dict) -> str:

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
        prompt.append("INTENT")
        prompt.append("=" * 70)
        prompt.append(context["intent"])

        # =====================================================
        # Confidence
        # =====================================================

        prompt.append("\n" + "=" * 70)
        prompt.append("CONFIDENCE")
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
        # Knowledge
        # =====================================================

        dataset_titles = {

            "crop": "CROP RECOMMENDATION",

            "fertilizer": "FERTILIZER KNOWLEDGE",

            "disease": "DISEASE KNOWLEDGE",

            "pest": "PEST KNOWLEDGE",

            "management": "CROP MANAGEMENT",

            "general": "GENERAL KNOWLEDGE"
        }

        grouped = defaultdict(list)

        for item in context["knowledge"]:
            grouped[item["dataset"]].append(item)

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

            prompt.append("\n")
            prompt.append("=" * 70)
            prompt.append(dataset_titles.get(dataset, dataset.upper()))
            prompt.append("=" * 70)

            for item in grouped[dataset]:

                prompt.append(f"\nSource : {item['source']}")
                prompt.append(f"Score  : {item['score']}")
                prompt.append(item["content"])

        # =====================================================
        # Weather
        # =====================================================

        if context["weather"] and context["weather"].get("status") == "success":

            weather = context["weather"]

            prompt.append("\n")
            prompt.append("=" * 70)
            prompt.append("LIVE WEATHER")
            prompt.append("=" * 70)

            prompt.append(f"Location : {weather.get('location')}")
            prompt.append(f"Region : {weather.get('region')}")
            prompt.append(f"Country : {weather.get('country')}")
            prompt.append(f"Temperature : {weather.get('temperature')} °C")
            prompt.append(f"Humidity : {weather.get('humidity')} %")
            prompt.append(f"Wind : {weather.get('wind_kph')} km/h")
            prompt.append(f"Rainfall : {weather.get('precipitation_mm')} mm")
            prompt.append(f"Condition : {weather.get('condition')}")
            prompt.append(f"UV Index : {weather.get('uv')}")

            forecast = weather.get("forecast", [])

            if forecast:

                prompt.append("\n7-DAY FORECAST")

                for day in forecast[:7]:

                    date = day.get("date", "")

                    day_data = day.get("day", {})

                    prompt.append(
                        f"{date}: "
                        f"{day_data.get('condition', {}).get('text')} | "
                        f"Max {day_data.get('maxtemp_c')}°C | "
                        f"Min {day_data.get('mintemp_c')}°C | "
                        f"Rain {day_data.get('daily_chance_of_rain')}%"
                    )

        # =====================================================
        # Market
        # =====================================================

        if context["market"] and context["market"].get("status") == "success":

            market = context["market"]

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

        prompt.append("\n")
        prompt.append("=" * 70)
        prompt.append("INSTRUCTIONS")
        prompt.append("=" * 70)

        prompt.append(
"""
Answer the farmer's question using ONLY the information provided.

Priority:
1. Use retrieved agricultural knowledge first.
2. Use weather information only if it is relevant.
3. Use market information only if it is relevant.
4. Never invent facts.
5. If information is unavailable, clearly state it.
6. Keep the answer practical, concise, and farmer-friendly.
7. If weather indicates rain, drought, frost, or extreme heat, include suitable farming advice.
8. If market prices are available, mention whether selling now appears favorable based on the provided data.
9. Prefer bullet points where appropriate.
"""
        )

        return "\n".join(prompt)