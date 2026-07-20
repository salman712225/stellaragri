import asyncio
import json
import re
import time

from app.rag.rag_service import RAGService
from app.rag.query_processor import QueryProcessor
from app.rag.context_builder import ContextBuilder
from app.rag.advisor import AgricultureAdvisor
from app.rag.weather_service import WeatherService
from app.rag.market_service import MarketService
from app.llm.llm_service import LLMService
from app.llm.utils.response_cleaner import ResponseCleaner


class ChatService:

    WEATHER_INTENTS = {
        "crop_recommendation",
        "fertilizer",
        "disease",
        "pest",
        "management",
        "irrigation",
        "weather",
        "harvest"
    }

    MARKET_INTENTS = {
        "market",
        "harvest",
        "selling"
    }

    @staticmethod
    async def answer(question: str):

        total_start = time.perf_counter()

        print("\n" + "=" * 80)
        print("NEW FARMER QUERY")
        print("=" * 80)
        print(question)

        # ======================================================
        # STEP 1 : Query Processing
        # ======================================================

        start = time.perf_counter()

        query = QueryProcessor.process(question)

        print(f"Query Processing : {(time.perf_counter()-start):.2f}s")

        # ======================================================
        # STEP 2 : Retrieve RAG Knowledge
        # ======================================================

        start = time.perf_counter()

        retrieved_chunks = RAGService.retrieve(question)

        print(f"RAG Retrieval    : {(time.perf_counter()-start):.2f}s")

        # ======================================================
        # STEP 3 : Weather & Market
        # ======================================================

        weather = {}
        market = {}

        async def fetch_weather():

            try:

                location = (
                    query.entities.get("location")
                    or query.entities.get("state")
                    or "India"
                )

                return WeatherService.get_weather(location)

            except Exception as e:

                print("Weather Error :", e)

            return {}

        async def fetch_market():

            try:

                crop = query.entities.get("crop")
                if not crop and any(w in question.lower() for w in ["price", "market", "mandi", "rate", "cost", "sell"]):
                    crop = "rice"

                if crop:

                    return MarketService.get_market_price(

                        crop=crop,

                        state=query.entities.get("state", ""),

                        district=query.entities.get("district", "")
                    )

            except Exception as e:

                print("Market Error :", e)

            return {}

        start = time.perf_counter()

        weather, market = await asyncio.gather(

            fetch_weather(),

            fetch_market()

        )

        print(f"External APIs    : {(time.perf_counter()-start):.2f}s")

        # ======================================================
        # STEP 4 : Build Context
        # ======================================================

        context = ContextBuilder.build(

            query_result=query,

            rag_chunks=retrieved_chunks,

            weather_data=weather,

            market_data=market

        )

        # ======================================================
        # STEP 5 : Prompt
        # ======================================================

        prompt = AgricultureAdvisor.build_prompt(context)

        messages = [

            {
                "role": "system",

                "content": AgricultureAdvisor.SYSTEM_PROMPT
            },

            {
                "role": "user",

                "content": prompt
            }

        ]

        # ======================================================
        # STEP 6 : LLM
        # ======================================================

        start = time.perf_counter()

        response = await LLMService.generate(messages)

        print(f"LLM Generation   : {(time.perf_counter()-start):.2f}s")

        # ======================================================
        # STEP 7 : Clean Response
        # ======================================================

        try:

            response = ResponseCleaner.clean(response)

        except Exception:

            response = response.strip()

            if response.startswith("```json"):
                response = response.replace("```json", "", 1)

            if response.startswith("```"):
                response = response.replace("```", "", 1)

            if response.endswith("```"):
                response = response[:-3]

            response = response.strip()

            match = re.search(r"\{.*\}", response, re.DOTALL)

            if match:
                response = match.group(0)

        # ======================================================
        # STEP 8 : Parse JSON
        # ======================================================

        try:
            parsed = json.loads(response)
        except json.JSONDecodeError as e:
            try:
                repaired = ResponseCleaner.repair_json(response)
                parsed = json.loads(repaired)
            except Exception:
                parsed = {
                    "success": False,
                    "error": "Invalid JSON returned by LLM.",
                    "exception": str(e),
                    "raw_response": response
                }

        except Exception as e:

            parsed = {

                "success": False,

                "error": str(e),

                "raw_response": response
            }

        # ======================================================
        # Performance
        # ======================================================

        print("=" * 80)
        print(f"Prompt Length    : {len(prompt)}")
        print(f"Response Length  : {len(response)}")
        print(f"Total Time       : {(time.perf_counter()-total_start):.2f}s")
        print("=" * 80)

        return parsed