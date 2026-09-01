import asyncio
import json
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional
from datetime import datetime

from app.core.config import settings
from app.core.logger import logger
from app.rag.weather_service import WeatherService
from app.rag.market_service import MarketService


class SnapServeService:
    """
    SnapServe AI Voice Platform & MCP Integration Service
    """

    # In-memory circular log buffer for admin error tracking & diagnostics
    _system_error_logs: List[Dict[str, Any]] = []
    _max_logs: int = 100

    @classmethod
    def log_error_event(cls, category: str, message: str, status_code: Optional[int] = None, details: Optional[Any] = None):
        """Record an error event for the Admin Diagnostics console."""
        entry = {
            "id": f"err_{int(time.time() * 1000)}",
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "message": message,
            "status_code": status_code,
            "details": details
        }
        cls._system_error_logs.insert(0, entry)
        if len(cls._system_error_logs) > cls._max_logs:
            cls._system_error_logs.pop()

    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.SNAPSERVE_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) StellarAgriAI/1.0"
        }

    @classmethod
    def _sync_request(
        cls,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform a synchronous HTTP request to the SnapServe API."""
        base_url = settings.SNAPSERVE_BASE_URL.rstrip("/")
        url = f"{base_url}{path}"
        headers = cls.get_headers()
        data = json.dumps(payload).encode("utf-8") if payload is not None else None

        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        start_time = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                elapsed_ms = int((time.perf_counter() - start_time) * 1000)
                body = resp.read().decode("utf-8")
                if not body.strip():
                    return {"success": True, "statusCode": resp.status, "latencyMs": elapsed_ms}
                result = json.loads(body)
                return {
                    "success": True,
                    "data": result,
                    "statusCode": resp.status,
                    "latencyMs": elapsed_ms
                }
        except urllib.error.HTTPError as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            err_body = e.read().decode("utf-8", errors="ignore")
            cls.log_error_event(
                category="SnapServe API HTTPError",
                message=f"HTTP {e.code} on {method} {path}: {err_body}",
                status_code=e.code,
                details={"path": path, "method": method, "response": err_body}
            )
            return {
                "success": False,
                "error": f"HTTP {e.code}: {e.reason}",
                "statusCode": e.code,
                "details": err_body,
                "latencyMs": elapsed_ms
            }
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            cls.log_error_event(
                category="Network / Connection Error",
                message=f"Request failed for {method} {path}: {str(e)}",
                details={"path": path, "method": method, "error": str(e)}
            )
            return {
                "success": False,
                "error": str(e),
                "statusCode": 500,
                "latencyMs": elapsed_ms
            }

    @classmethod
    async def request(
        cls,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute request non-blockingly via asyncio thread."""
        return await asyncio.to_thread(cls._sync_request, method, path, payload)

    # ── Wallet & Usage ──
    @classmethod
    async def get_wallet(cls) -> Dict[str, Any]:
        res = await cls.request("GET", "/wallet")
        if res.get("success"):
            return res.get("data", {})
        return {}

    # ── Indic Multi-Language Configurations ──
    LANGUAGE_CONFIGS = {
        "hi-IN": {
            "name": "Hindi",
            "asrLanguage": "hi-IN",
            "greeting_template": "Namaste {farmer_name}! Main Stellar Agri AI se bol raha hoon. Aapne {crop} fasal ke baare mein advisory maangi thi. Main aapki kya madad kar sakta hoon?",
            "default_greeting": "Namaste! Main Stellar Agri AI se bol raha hoon. Fasal, beemari, khad ya mandi bhav se judi kya madad chahiye aapko?",
            "language_instruction": "You MUST converse strictly in polite, natural Hindi (हिंदी). Use standard Indian farming terms (Khad, Urea, DAP, Fasal, Mandi, Keetnashak)."
        },
        "ta-IN": {
            "name": "Tamil",
            "asrLanguage": "ta-IN",
            "greeting_template": "Vanakkam {farmer_name}! Naan Stellar Agri AI vivasaya aalochagar pesugiren. Ungaludaiya {crop} payir pathiya vivaram eppadi udhava mudiyum?",
            "default_greeting": "Vanakkam! Naan Stellar Agri AI vivasaya aalochagar. Ungalukku payir, uram, nooi kattuppaadu matriya vivaram thevaiya?",
            "language_instruction": "You MUST converse strictly in polite, natural Tamil (தமிழ்). Use familiar farming terms (Payir, Uram, Nooi, Mandi, Pasumai)."
        },
        "te-IN": {
            "name": "Telugu",
            "asrLanguage": "te-IN",
            "greeting_template": "Namaskaram {farmer_name} garu! Nenu Stellar Agri AI vyavasaya salahadarunini. Mee {crop} panta gurinchi emaina sahayam kaavala?",
            "default_greeting": "Namaskaram! Nenu Stellar Agri AI vyavasaya salahadarunini. Panta, eruuvulu, thegullu mariyu mandi dharala gurinchi emaina sahayam kaavala?",
            "language_instruction": "You MUST converse strictly in polite, natural Telugu (తెలుగు). Use familiar agriculture terms (Panta, Eruuvulu, Thegullu, Mandi)."
        },
        "kn-IN": {
            "name": "Kannada",
            "asrLanguage": "kn-IN",
            "greeting_template": "Namaskara {farmer_name}! Naanu Stellar Agri AI krushi salahagara mathaduthidene. Nimma {crop} beleya bagge yava sahaya beku?",
            "default_greeting": "Namaskara! Naanu Stellar Agri AI krushi salahagara mathaduthidene. Bele, gobbarada mahiti athava roga niyantrana bagge yava sahaya beku?",
            "language_instruction": "You MUST converse strictly in polite, natural Kannada (ಕನ್ನಡ). Use familiar farming terms (Bele, Gobbara, Roga, Mandi)."
        },
        "mr-IN": {
            "name": "Marathi",
            "asrLanguage": "mr-IN",
            "greeting_template": "Namaskar {farmer_name}! Mi Stellar Agri AI krushi sallyagar bolat ahe. Aplya {crop} pikababt kay madat havi ahe?",
            "default_greeting": "Namaskar! Mi Stellar Agri AI madhun bolat ahe. Pik, khati, rog kiva bajarbhavababt kai madat havi ahe?",
            "language_instruction": "You MUST converse strictly in polite, natural Marathi (मराठी). Use familiar agricultural vocabulary (Pik, Khat, Rog, Bajarbhav)."
        },
        "bn-IN": {
            "name": "Bengali",
            "asrLanguage": "bn-IN",
            "greeting_template": "Nomoshkar {farmer_name}! Aami Stellar Agri AI krishi poramorshok bolchi. Aaponar {crop} chash niye ki shahajjo korte pari?",
            "default_greeting": "Nomoshkar! Aami Stellar Agri AI theke bolchi. Fasol, shar, rog ba bajar dor niye ki shahajjo lagbe?",
            "language_instruction": "You MUST converse strictly in polite, natural Bengali (বাংলা). Use familiar farming terms (Fasol, Shar, Rog, Mandi)."
        },
        "gu-IN": {
            "name": "Gujarati",
            "asrLanguage": "gu-IN",
            "greeting_template": "Namaste {farmer_name}! Hu Stellar Agri AI krushi salahkar bolu chu. Tamara {crop} pak maate shu madat joiye che?",
            "default_greeting": "Namaste! Hu Stellar Agri AI mathi bolu chu. Pak, khatar, rog niyantran ke mandi bhav mate shu mahiti joiye che?",
            "language_instruction": "You MUST converse strictly in polite, natural Gujarati (ગુજરાતી). Use familiar farming terms (Pak, Khatar, Rog, Mandi bhav)."
        },
        "pa-IN": {
            "name": "Punjabi",
            "asrLanguage": "pa-IN",
            "greeting_template": "Sat Sri Akal {farmer_name} ji! Main Stellar Agri AI kheti salahkar bol reha haan. Tuhadi {crop} di fasal baare ki madad chaahidi hai?",
            "default_greeting": "Sat Sri Akal! Main Stellar Agri AI walon bol reha haan. Fasal, khaad, beemari ya mandi bhav baare ki jankari chahidi hai?",
            "language_instruction": "You MUST converse strictly in polite, natural Punjabi (ਪੰਜਾਬੀ). Use familiar farming terms (Fasal, Khaad, Beemari, Mandi)."
        },
        "ml-IN": {
            "name": "Malayalam",
            "asrLanguage": "ml-IN",
            "greeting_template": "Namaskaram {farmer_name}! Njan Stellar Agri AI krishi aalochakan samsarikunnu. Ningalude {crop} krishiyil enthu sahayamanu vendathu?",
            "default_greeting": "Namaskaram! Njan Stellar Agri AI il ninnu samsarikunnu. Krishi, valaprayogam, roganiyanthranam ennivaye kurichu enthu ariyannam?",
            "language_instruction": "You MUST converse strictly in polite, natural Malayalam (മലയാളം). Use familiar farming vocabulary (Krishi, Valam, Rogam, Mandi)."
        },
        "en-IN": {
            "name": "English",
            "asrLanguage": "en-IN",
            "greeting_template": "Hello {farmer_name}! I am your Stellar Agri AI agricultural assistant. I am calling regarding your {crop} query. How may I help you today?",
            "default_greeting": "Hello! I am your Stellar Agri AI agricultural assistant. How can I help you with your crop, fertilizer, pest diagnosis, or mandi prices today?",
            "language_instruction": "You MUST converse in clear, courteous Indian English. Provide direct, practical agricultural advice on crops, fertilizers, pest control, and mandi prices."
        }
    }

    # ── Agents ──
    @classmethod
    async def get_agents(cls) -> List[Dict[str, Any]]:
        res = await cls.request("GET", "/agents")
        if res.get("success") and isinstance(res.get("data"), list):
            return res["data"]
        return []

    @classmethod
    async def get_agent(cls, agent_id: int) -> Optional[Dict[str, Any]]:
        res = await cls.request("GET", f"/agents/{agent_id}")
        if res.get("success"):
            return res.get("data")
        return None

    @classmethod
    async def update_agent(cls, agent_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update agent settings (language, greeting, system prompt, etc.) via PATCH."""
        return await cls.request("PATCH", f"/agents/{agent_id}", payload)

    @classmethod
    async def toggle_agent(cls, agent_id: int) -> Dict[str, Any]:
        res = await cls.request("PATCH", f"/agents/{agent_id}/toggle")
        return res

    @classmethod
    async def create_agent(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await cls.request("POST", "/agents", payload)

    @classmethod
    async def configure_agent_for_call(
        cls,
        agent_id: int,
        language: str = "hi-IN",
        farmer_name: str = "Farmer",
        crop: str = "Paddy",
        issue: Optional[str] = None
    ) -> bool:
        """
        Dynamically configure the agent's language, ASR acoustic model,
        personalized opening greeting, and language-specific instructions with live weather & mandi prices before placing a call.
        """
        lang_key = language if language in cls.LANGUAGE_CONFIGS else "hi-IN"
        config = cls.LANGUAGE_CONFIGS[lang_key]

        # ── 1. Fetch Real-Time Weather Telemetry ──
        weather_info = "Weather telemetry: Normal agricultural temperature (28°C to 34°C), stable humidity, moderate conditions."
        try:
            w = WeatherService.get_weather(location="New Delhi")
            if w.get("status") == "success":
                temp = w.get("temperature", 30)
                feels = w.get("feels_like", temp)
                cond = w.get("condition", "Clear")
                hum = w.get("humidity", 50)
                agri = w.get("agriculture", {})
                irr = "Irrigation is needed due to low recent precipitation" if agri.get("irrigation_needed") else "Soil moisture is adequate, irrigation can be delayed"
                rain_prob = agri.get("rain_probability", 0)
                fungal = agri.get("fungal_risk", "Low")
                heat = "High heat stress warning" if agri.get("heat_stress") else "Normal temperature range"
                weather_info = (
                    f"- Current Weather: {temp}°C (Feels like {feels}°C), Sky: {cond}\n"
                    f"- Humidity: {hum}%, Probability of Rain: {rain_prob}%\n"
                    f"- Agronomy Alert: {irr}. Fungal disease risk is {fungal}. {heat}."
                )
        except Exception as e:
            logger.warning(f"Could not fetch live weather for agent prompt: {e}")

        # ── 2. Fetch Real-Time APMC Mandi Market Prices ──
        market_info = f"Market Prices: Benchmark APMC Mandi rates available for {crop}."
        try:
            m = MarketService.get_market_price(crop=crop or "Rice")
            if m.get("status") == "success":
                crop_name = m.get("crop", crop)
                modal = m.get("modal_price", "₹2,200 / quintal")
                p_min = m.get("min_price", "₹2,000 / quintal")
                p_max = m.get("max_price", "₹2,400 / quintal")
                rec = m.get("analysis", {}).get("selling_recommendation", "Good time to sell at local APMC mandi")
                market_info = (
                    f"- Target Crop: {crop_name}\n"
                    f"- APMC Mandi Modal Price: {modal}\n"
                    f"- Market Price Range: {p_min} to {p_max}\n"
                    f"- Selling Recommendation: {rec}."
                )
        except Exception as e:
            logger.warning(f"Could not fetch live market prices for agent prompt: {e}")

        # Generate personalized opening greeting in selected language
        if farmer_name and farmer_name.strip() and farmer_name.strip().lower() != "farmer":
            greeting = config["greeting_template"].format(farmer_name=farmer_name.strip(), crop=crop or "crop")
        else:
            greeting = config["default_greeting"]

        # Build specialized system prompt tailored for the farmer & selected language
        prompt = f"""You are Stellar Agri AI, an expert agricultural advisor, agronomist, and crop doctor.

CRITICAL LANGUAGE REQUIREMENT:
{config["language_instruction"]}
The caller specifically requested advisory in {config["name"]}. You MUST converse and answer exclusively in {config["name"]}.

CALLER CONTEXT:
- Farmer Name: {farmer_name}
- Target Crop: {crop}
- Reported Query / Issue: {issue or 'General agronomy, fertilizer, or crop health consultation'}

LIVE REAL-TIME AGRI TELEMETRY & MARKET PRICES (Use these exact figures when asked about weather, rain, watering, or mandi rates):
[LIVE WEATHER FORECAST]
{weather_info}

[LIVE APMC MANDI COMMODITY PRICES]
{market_info}

CONVERSATION & ADVISORY GUIDELINES:
1. When asked about MANDI PRICES / MARKET RATES (bhav / dharalu / vilai / rate):
   - Quote the APMC modal price (e.g. {market_info.splitlines()[1] if len(market_info.splitlines()) > 1 else 'latest benchmark price'}) and price range per quintal.
   - Advise whether it is currently a good time to sell.
2. When asked about WEATHER / RAIN / IRRIGATION:
   - Provide the current temperature, rain forecast, and irrigation necessity.
3. When asked about CROPS & FERTILIZERS:
   - Give exact fertilizer dosage (Urea, DAP, MOP, SSP) and pest/disease spray remedies.
4. Keep responses brief, natural, spoken, and conversational (1 to 3 short sentences per turn).
5. Always remain respectful, encouraging, and supportive of the farmer.
"""

        patch_payload = {
            "language": lang_key,
            "asrLanguage": config["asrLanguage"],
            "greetingMessage": greeting,
            "systemPrompt": prompt,
            "status": "active"
        }

        logger.info(f"🌐 Configuring Agent #{agent_id} for Language '{config['name']}' ({lang_key}) with live weather & mandi data. Greeting: '{greeting}'")
        res = await cls.update_agent(agent_id, patch_payload)
        return res.get("success", False)

    # ── Phone Numbers ──
    @classmethod
    async def get_phone_numbers(cls) -> List[Dict[str, Any]]:
        res = await cls.request("GET", "/phone-numbers")
        if res.get("success") and isinstance(res.get("data"), list):
            return res["data"]
        return []

    @classmethod
    async def assign_phone(cls, phone_id: int, agent_id: int) -> Dict[str, Any]:
        return await cls.request("PATCH", f"/phone-numbers/{phone_id}/assign", {"agentId": agent_id})

    # ── Knowledge Sources ──
    @classmethod
    async def get_knowledge_sources(cls) -> List[Dict[str, Any]]:
        res = await cls.request("GET", "/knowledge-sources")
        if res.get("success") and isinstance(res.get("data"), list):
            return res["data"]
        return []

    # ── Calls & Logs ──
    @classmethod
    async def get_calls(cls, agent_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        path = "/calls"
        params = []
        if agent_id:
            params.append(f"agentId={agent_id}")
        if status:
            params.append(f"status={status}")
        if params:
            path += "?" + "&".join(params)

        res = await cls.request("GET", path)
        if res.get("success") and isinstance(res.get("data"), list):
            return res["data"]
        return []

    @classmethod
    async def get_call(cls, call_id: int) -> Optional[Dict[str, Any]]:
        res = await cls.request("GET", f"/calls/{call_id}")
        if res.get("success"):
            return res.get("data")
        return None

    @classmethod
    async def trigger_outbound_call(
        cls,
        agent_id: int,
        to_number: str,
        language: str = "hi-IN",
        farmer_name: str = "Farmer",
        crop: str = "Paddy",
        issue: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Dynamically configures the agent for the requested language and triggers the outbound call.
        """
        # Step 1: Dynamically configure the agent's language, ASR, and opening greeting
        try:
            await cls.configure_agent_for_call(
                agent_id=agent_id,
                language=language,
                farmer_name=farmer_name,
                crop=crop,
                issue=issue
            )
        except Exception as e:
            logger.warning(f"Could not update agent language config prior to call: {e}")

        # Step 2: Trigger outbound call via SnapServe
        payload: Dict[str, Any] = {
            "agentId": agent_id,
            "toNumber": to_number
        }
        if variables:
            payload["variables"] = variables

        res = await cls.request("POST", "/calls/outbound", payload)
        if not res.get("success"):
            cls.log_error_event(
                category="Outbound Call Failed",
                message=f"Could not initiate outbound call to {to_number} in language {language} (Agent #{agent_id})",
                status_code=res.get("statusCode"),
                details=res
            )
        return res

    # ── Comprehensive Diagnostic Status ──
    @classmethod
    async def get_system_status(cls) -> Dict[str, Any]:
        start = time.perf_counter()
        
        # Parallel fetch of core indicators
        wallet, agents, phones, knowledge = await asyncio.gather(
            cls.get_wallet(),
            cls.get_agents(),
            cls.get_phone_numbers(),
            cls.get_knowledge_sources()
        )
        ping_latency = int((time.perf_counter() - start) * 1000)

        # Compute aggregates
        is_connected = bool(wallet or agents or phones)
        active_agents = [a for a in agents if a.get("status") == "active"]
        draft_agents = [a for a in agents if a.get("status") == "draft"]
        assigned_phones = [p for p in phones if p.get("agentId") is not None]

        return {
            "mcp": {
                "server": "@snapserveai/mcp",
                "connected": is_connected,
                "status": "online" if is_connected else "offline",
                "toolCount": 76,
                "pingLatencyMs": ping_latency,
                "baseUrl": settings.SNAPSERVE_BASE_URL,
                "apiKeyMasked": f"sk_live_...{settings.SNAPSERVE_API_KEY[-6:]}" if settings.SNAPSERVE_API_KEY else "Not Configured"
            },
            "wallet": {
                "balanceInr": wallet.get("balanceInr", 0.0),
                "balanceCents": wallet.get("balanceCents", 0),
                "currency": wallet.get("currency", "INR"),
                "effectiveRatePerMin": wallet.get("effectiveRateCentsPerMin", 500) / 100
            },
            "telephony": {
                "totalNumbers": len(phones),
                "assignedNumbers": len(assigned_phones),
                "numbers": phones
            },
            "agents": {
                "total": len(agents),
                "activeCount": len(active_agents),
                "draftCount": len(draft_agents),
                "list": agents
            },
            "knowledge": {
                "totalSources": len(knowledge),
                "sources": knowledge
            },
            "recentErrors": cls._system_error_logs[:15]
        }
