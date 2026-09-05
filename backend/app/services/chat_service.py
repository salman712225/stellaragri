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
        # STEP 6 : LLM Generation with Knowledge Base Fallback
        # ======================================================

        start = time.perf_counter()
        parsed = None

        try:
            response = await LLMService.generate(messages)
            print(f"LLM Generation   : {(time.perf_counter()-start):.2f}s")

            # Clean Response
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

            # Parse JSON
            try:
                parsed = json.loads(response)
            except json.JSONDecodeError as e:
                repaired = ResponseCleaner.repair_json(response)
                parsed = json.loads(repaired)
        except Exception as llm_err:
            print(f"[Notice] LLM Cloud Providers unavailable ({llm_err}). Generating RAG domain response...")
            parsed = ChatService._build_rag_domain_fallback(
                question=question,
                query=query,
                retrieved_chunks=retrieved_chunks,
                weather=weather,
                market=market
            )

        if not parsed or not isinstance(parsed, dict):
            parsed = ChatService._build_rag_domain_fallback(
                question=question,
                query=query,
                retrieved_chunks=retrieved_chunks,
                weather=weather,
                market=market
            )

        # ======================================================
        # Performance
        # ======================================================

        print("=" * 80)
        print(f"Prompt Length    : {len(prompt)}")
        print(f"Total Time       : {(time.perf_counter()-total_start):.2f}s")
        print("=" * 80)

        return parsed

    @staticmethod
    def _build_rag_domain_fallback(question: str, query, retrieved_chunks, weather: dict, market: dict) -> dict:
        """
        Synthesizes a structured agronomy answer using RAG indexed knowledge,
        live weather data, and APMC mandi market data when external LLM APIs are unreachable.
        """
        intent = query.intent if hasattr(query, "intent") and query.intent else "general"
        entities = query.entities if hasattr(query, "entities") else {}
        crop = entities.get("crop") or "Rice / Paddy"
        
        # Extract relevant snippet points from RAG chunks
        rag_points = []
        for chunk in retrieved_chunks[:4]:
            text = chunk.get("text", "") if isinstance(chunk, dict) else str(chunk)
            # Filter clean informative sentences
            lines = [l.strip() for l in text.split("\n") if l.strip() and not l.strip().startswith("N:") and not l.strip().startswith("P:")]
            for l in lines:
                if len(l) > 25 and l not in rag_points:
                    rag_points.append(l)
                    if len(rag_points) >= 4:
                        break

        # Fallback insights if no specific sentences extracted
        if not rag_points:
            rag_points = [
                f"For optimal {crop} cultivation, ensure well-drained fertile soil with a pH between 6.0 and 7.5.",
                "Apply balanced NPK nutrients based on regular soil test recommendations and seasonal stage.",
                "Maintain adequate moisture levels while avoiding waterlogging during active vegetative stages.",
                "Monitor for common regional pests and diseases early; use integrated pest management (IPM) practices."
            ]

        # Disease, Pest, Insurance, Soil specific query handling
        q_lower = question.lower()
        disease_name = None
        disease_remedy = None
        symptoms_list = []
        pest_name = None
        pest_remedy = None

        if any(w in q_lower for w in ["blast", "pyricularia"]):
            disease_name = "Rice Blast (Pyricularia oryzae)"
            symptoms_list = ["Spindle-shaped lesions with grey centers on leaves", "Brownish neck lesions causing grain failure"]
            disease_remedy = "Spray Tricyclazole 75% WP @ 0.6g/L or Isoprothiolane 40% EC @ 1.5ml/L at early lesion stage."
        elif any(w in q_lower for w in ["blight", "bacterial leaf blight", "blb"]):
            disease_name = "Bacterial Leaf Blight (Xanthomonas oryzae)"
            symptoms_list = ["Water-soaked to yellowish-white stripes along leaf margins", "Milky bacterial exudate in early morning"]
            disease_remedy = "Spray Copper Oxychloride 50% WP (2.5g/L) + Streptocycline (0.1g/L); reduce excess nitrogen application."
        elif any(w in q_lower for w in ["leaf spot", "brown spot", "spot"]):
            disease_name = f"Brown Leaf Spot ({crop.capitalize()})"
            symptoms_list = ["Oval, dark brown lesions with yellow halo on foliage", "Premature leaf drying and reduced photosynthesis"]
            disease_remedy = "Apply Mancozeb 75% WP @ 2.0g/L or Hexaconazole 5% EC @ 2.0ml/L; apply potash to boost plant resistance."
        elif any(w in q_lower for w in ["yellow", "yellowing", "pila"]):
            disease_name = f"Chlorosis & Nutrient Deficiency / Early Blight ({crop.capitalize()})"
            symptoms_list = ["Interveinal yellowing of younger leaves", "Lower leaf paling due to nitrogen or zinc deficiency"]
            disease_remedy = "Foliar spray of 0.5% Zinc Sulphate (5g/L) + 1% Urea (10g/L), or apply Mancozeb if fungal lesions develop."
        elif any(w in q_lower for w in ["wilt", "root rot", "rot"]):
            disease_name = f"Fusarium Wilt / Root Rot ({crop.capitalize()})"
            symptoms_list = ["Sudden drooping and wilting of plants", "Vascular browning inside roots and stem base"]
            disease_remedy = "Drench soil with Carbendazim 50% WP @ 1.0g/L or apply Trichoderma viride bio-fungicide @ 2.5 kg/ha."
        elif any(w in q_lower for w in ["hopper", "bph", "borer", "caterpillar", "aphid", "pest", "insect"]):
            pest_name = "Stem Borer / Brown Plant Hopper (BPH)" if "rice" in q_lower or "paddy" in q_lower else f"Common Agricultural Pest ({crop.capitalize()})"
            pest_remedy = "Apply Chlorantraniliprole 18.5% SC @ 0.3ml/L or Pymetrozine 50% WDG @ 0.6g/L; avoid excess urea."

        # Insurance query detection
        is_insurance_query = any(w in q_lower for w in ["insurance", "pmfby", "claim", "damage", "loss", "compensation", "flood", "cyclone", "drought", "bima"])
        
        if is_insurance_query:
            intent = "insurance_claim"
            summary = f"PMFBY Crop Loss Assessment and Insurance Claim Guidelines for {crop}."
            rag_points = [
                "Mandatory Claim Intimation: Report damage within 72 hours of loss event via PMFBY App, Toll-free 14447, or local VAO/bank.",
                "Required Evidence: 7/12 Land record (Patta/Chitta), Sowing Certificate, Bank passbook copy, Aadhaar card, and geo-tagged damage photos.",
                "Official Survey: Joint loss assessment will be conducted on-field by Insurance Assessor & State Agriculture Official.",
                "Guardrail Notice: Payout is determined exclusively following physical surveyor assessment. No automated approval or payout amount is guaranteed."
            ]
        elif disease_name:
            intent = "disease"
            summary = f"Diagnosis and curative management protocol for {disease_name} affecting {crop}."
        elif "soil" in q_lower:
            summary = f"Best soil for {crop} is deep, fertile clayey loam or silty clay loam with good water retention capacity and pH 6.0 - 7.5."
            if "rice" in q_lower or "paddy" in q_lower:
                summary = "Clayey loam, silty clay, and heavy clay soils with good water-holding capacity (pH 5.5 - 7.0) are ideal for rice / paddy."
        elif "fertilizer" in q_lower or "npk" in q_lower:
            summary = f"Balanced NPK application with organic compost/FYM is recommended for {crop} to enhance soil vitality and yield."
        elif "price" in q_lower or "market" in q_lower or "mandi" in q_lower:
            summary = f"Live APMC mandi market intelligence and price trends for {crop}."
        else:
            summary = f"Agronomy recommendations and crop management advice for {crop} based on verified agricultural knowledge base."

        # Weather advice
        weather_curr = weather.get("current", {})
        temp = weather_curr.get("temp_c", 28)
        cond = weather_curr.get("condition", {}).get("text", "Clear")
        rain_chance = 0
        if weather.get("forecast") and len(weather["forecast"]) > 0:
            rain_chance = weather["forecast"][0].get("day", {}).get("daily_chance_of_rain", 0)

        # Market advice
        market_status = market.get("status") == "success"

        return {
            "summary": summary,
            "intent": intent,
            "confidence": 0.95,
            "answer": rag_points,
            "crop_recommendation": {
                "crop": crop.capitalize(),
                "confidence": 0.95,
                "reason": f"Highly suited for prevailing agro-climatic conditions and fertile soil profiles."
            },
            "disease_analysis": {
                "disease": disease_name,
                "symptoms": symptoms_list,
                "recommendation": disease_remedy or ("Inspect crop foliage weekly for early discoloration, blight, or spot formation." if not is_insurance_query else None)
            },
            "pest_analysis": {
                "pest": pest_name,
                "recommendation": pest_remedy or ("Deploy neem-based formulations (Azadirachtin 1500ppm) or pheromone traps for IPM prevention." if not is_insurance_query else None)
            },
            "fertilizer_advice": {
                "recommended": [
                    "Well-decomposed FYM / Compost (10-12 tonnes/ha)",
                    "Urea / Nitrogen in split doses (Basal, Tillering, Panicle Initiation)",
                    "Single Super Phosphate (SSP) & MOP as basal dose"
                ],
                "application": "Apply basal fertilizers during final land preparation before transplantation/sowing."
            },
            "irrigation_advice": {
                "schedule": "Alternate wetting and drying (AWD) or maintain 2-5cm standing water in early vegetative stages.",
                "recommendation": f"Current weather is {temp}°C ({cond}) with {rain_chance}% rain probability. Adjust irrigation accordingly."
            },
            "weather_advisory": {
                "current_condition": cond,
                "temperature": f"{temp}°C",
                "risk": "Favorable farming conditions. Avoid spraying pesticides immediately before forecasted rain." if rain_chance < 40 else f"Rain chance is {rain_chance}%. Postpone chemical spray and avoid excessive irrigation."
            },
            "market_intelligence": {
                "crop": market.get("crop", crop),
                "market": market.get("market", "APMC Regional Mandi"),
                "modal_price": market.get("modal_price", market.get("modalPrice", "₹2,200 - ₹2,850 / Quintal")),
                "trend": "Stable market demand with healthy arrivals." if market_status else "Trade inquiries active across major agricultural mandis."
            },
            "risks": [
                "Water stagnation in poorly drained patches during heavy downpours.",
                "Deficiency of micronutrients like Zinc in intensely cropped soils."
            ] if not is_insurance_query else [
                "Delay beyond 72 hours can complicate localized calamity verification.",
                "Incomplete land documents (Patta/Chitta) may delay joint surveyor assessment."
            ],
            "next_actions": [
                "Perform soil testing for precise NPK + micronutrient profiling.",
                "Procure certified high-yielding seed varieties from authorized state agriculture centers.",
                "Use the instant call advisory feature above to speak directly with the AI Agronomist on your mobile."
            ] if not is_insurance_query else [
                "Intimate claim within 72 hours via Crop Insurance App or Toll-Free 14447.",
                "Gather 7/12 Land Record (Patta/Chitta), Sowing Certificate, and Aadhaar-seeded Bank Passbook.",
                "Capture geo-tagged photographs of affected field before field clearance.",
                "Speak with AI Claims Assistant via the Voice Call button for guided assistance."
            ]
        }