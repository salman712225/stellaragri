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

    PERMANENT_AGENT_ID: int = 1028

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
            "insurance_greeting_template": "Namaste {farmer_name}! Main Stellar Agri AI Crop Insurance Advisor bol raha hoon. Aapne {location} kshetra mein fasal nuksan ya PMFBY bima claim intimation ke baare mein request kiya tha. Main aapki claim intimation mein madad kar sakta hoon.",
            "default_greeting": "Namaste! Main Stellar Agri AI se bol raha hoon. Fasal, beemari, khad, ya PMFBY fasal bima claim se judi kya madad chahiye aapko?",
            "language_instruction": "You MUST converse strictly in polite, natural Hindi (हिंदी). Use standard Indian farming terms (Khad, Urea, DAP, Fasal, Mandi, Bima, Khasra, Patta)."
        },
        "ta-IN": {
            "name": "Tamil",
            "asrLanguage": "ta-IN",
            "greeting_template": "Vanakkam {farmer_name}! Naan Stellar Agri AI vivasaya aalochagar pesugiren. Ungaludaiya {crop} payir pathiya vivaram eppadi udhava mudiyum?",
            "insurance_greeting_template": "Vanakkam {farmer_name}! Naan Stellar Agri AI vivasaya bima aalochagar. {location} la ungalukku aana payir sedhaara PMFBY claim intimation pathi pesalaama?",
            "default_greeting": "Vanakkam! Naan Stellar Agri AI vivasaya aalochagar. Ungalukku payir, uram, nooi kattuppaadu matrum PMFBY bima claim pathiya vivaram thevaiya?",
            "language_instruction": "You MUST converse strictly in polite, natural Tamil (தமிழ்). Use familiar farming terms (Payir, Uram, Nooi, Mandi, Patta, Chitta, Bima)."
        },
        "te-IN": {
            "name": "Telugu",
            "asrLanguage": "te-IN",
            "greeting_template": "Namaskaram {farmer_name} garu! Nenu Stellar Agri AI vyavasaya salahadarunini. Mee {crop} panta gurinchi emaina sahayam kaavala?",
            "insurance_greeting_template": "Namaskaram {farmer_name} garu! Nenu Stellar Agri AI bima salahadarunini. {location} lo panta nashtam mariyu PMFBY bima claim intimation gurinchi maatladuthunnanu.",
            "default_greeting": "Namaskaram! Nenu Stellar Agri AI vyavasaya salahadarunini. Panta, thegullu mariyu PMFBY panta bima claim gurinchi emaina sahayam kaavala?",
            "language_instruction": "You MUST converse strictly in polite, natural Telugu (తెలుగు). Use familiar agriculture terms (Panta, Eruuvulu, Thegullu, Bima, Adangal, Pahani)."
        },
        "kn-IN": {
            "name": "Kannada",
            "asrLanguage": "kn-IN",
            "greeting_template": "Namaskara {farmer_name}! Naanu Stellar Agri AI krushi salahagara mathaduthidene. Nimma {crop} beleya bagge yava sahaya beku?",
            "insurance_greeting_template": "Namaskara {farmer_name}! Naanu Stellar Agri AI bima salahagara. {location} nalli bele hani mathu PMFBY bima claim bagge mathaduthidene.",
            "default_greeting": "Namaskara! Naanu Stellar Agri AI krushi salahagara mathaduthidene. Bele, roga niyantrana athava PMFBY bima claim bagge yava sahaya beku?",
            "language_instruction": "You MUST converse strictly in polite, natural Kannada (ಕನ್ನಡ). Use familiar farming terms (Bele, Gobbara, Roga, Bima, RTC, Pahani)."
        },
        "mr-IN": {
            "name": "Marathi",
            "asrLanguage": "mr-IN",
            "greeting_template": "Namaskar {farmer_name}! Mi Stellar Agri AI krushi sallyagar bolat ahe. Aplya {crop} pikababt kay madat havi ahe?",
            "insurance_greeting_template": "Namaskar {farmer_name}! Mi Stellar Agri AI peak vima sallyagar bolat ahe. {location} madhil pik nuksan v PMFBY claim intimation babat aplyala madat karu shakto.",
            "default_greeting": "Namaskar! Mi Stellar Agri AI madhun bolat ahe. Pik, khati, rog kiva PMFBY peak vima claim babat kai madat havi ahe?",
            "language_instruction": "You MUST converse strictly in polite, natural Marathi (मराठी). Use familiar agricultural vocabulary (Pik, Khat, Rog, 7/12 Extract, Peak Vima)."
        },
        "bn-IN": {
            "name": "Bengali",
            "asrLanguage": "bn-IN",
            "greeting_template": "Nomoshkar {farmer_name}! Aami Stellar Agri AI krishi poramorshok bolchi. Aaponar {crop} chash niye ki shahajjo korte pari?",
            "insurance_greeting_template": "Nomoshkar {farmer_name}! Aami Stellar Agri AI theke bolchi. {location} e fasol khotikriti o PMFBY bima claim intimation niye kotha bolte pari.",
            "default_greeting": "Nomoshkar! Aami Stellar Agri AI theke bolchi. Fasol, shar, rog ba PMFBY fasol bima claim niye ki shahajjo lagbe?",
            "language_instruction": "You MUST converse strictly in polite, natural Bengali (বাংলা). Use familiar farming terms (Fasol, Shar, Rog, Bima, Khatian)."
        },
        "gu-IN": {
            "name": "Gujarati",
            "asrLanguage": "gu-IN",
            "greeting_template": "Namaste {farmer_name}! Hu Stellar Agri AI krushi salahkar bolu chu. Tamara {crop} pak maate shu madat joiye che?",
            "insurance_greeting_template": "Namaste {farmer_name}! Hu Stellar Agri AI pak vima salahkar chu. {location} ma pak nuksan ane PMFBY claim intimation maate madat kari shaku chu.",
            "default_greeting": "Namaste! Hu Stellar Agri AI mathi bolu chu. Pak, khatar, rog niyantran ke PMFBY pak vima claim mate shu mahiti joiye che?",
            "language_instruction": "You MUST converse strictly in polite, natural Gujarati (ગુજરાતી). Use familiar farming terms (Pak, Khatar, Rog, 7/12, Pak Vima)."
        },
        "pa-IN": {
            "name": "Punjabi",
            "asrLanguage": "pa-IN",
            "greeting_template": "Sat Sri Akal {farmer_name} ji! Main Stellar Agri AI kheti salahkar bol reha haan. Tuhadi {crop} di fasal baare ki madad chaahidi hai?",
            "insurance_greeting_template": "Sat Sri Akal {farmer_name} ji! Main Stellar Agri AI fasal bima salahkar bol reha haan. {location} ch nuksan te PMFBY bima claim intimation baare madad kar sakda haan.",
            "default_greeting": "Sat Sri Akal! Main Stellar Agri AI walon bol reha haan. Fasal, khaad, beemari ya PMFBY fasal bima claim baare ki jankari chahidi hai?",
            "language_instruction": "You MUST converse strictly in polite, natural Punjabi (ਪੰਜਾਬੀ). Use familiar farming terms (Fasal, Khaad, Beemari, Fard, Bima)."
        },
        "ml-IN": {
            "name": "Malayalam",
            "asrLanguage": "ml-IN",
            "greeting_template": "Namaskaram {farmer_name}! Njan Stellar Agri AI krishi aalochakan samsarikunnu. Ningalude {crop} krishiyil enthu sahayamanu vendathu?",
            "insurance_greeting_template": "Namaskaram {farmer_name}! Njan Stellar Agri AI crop insurance salahakan samsarikunnu. {location} le krishi nashtam, PMFBY claim intimation sambandhichu sahayam cheyyam.",
            "default_greeting": "Namaskaram! Njan Stellar Agri AI il ninnu samsarikunnu. Krishi, valaprayogam, athava PMFBY crop insurance claim ennivaye kurichu enthu ariyannam?",
            "language_instruction": "You MUST converse strictly in polite, natural Malayalam (മലയാളം). Use familiar farming vocabulary (Krishi, Valam, Rogam, Bima, Pattayam)."
        },
        "en-IN": {
            "name": "English",
            "asrLanguage": "en-IN",
            "greeting_template": "Hello {farmer_name}! I am your Stellar Agri AI agricultural assistant. I am calling regarding your {crop} query. How may I help you today?",
            "insurance_greeting_template": "Hello {farmer_name}! I am your Stellar Agri AI Crop Insurance Advisor calling regarding crop loss in {location}. How can I assist with your PMFBY claim intimation today?",
            "default_greeting": "Hello! I am your Stellar Agri AI assistant. How can I help you with crop advice, weather warnings, or PMFBY crop insurance claims today?",
            "language_instruction": "You MUST converse in clear, courteous Indian English. Provide direct, practical agricultural advice and official PMFBY crop insurance claim guidance."
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

    # ── Universal Multi-Lingual Inbound & Outbound Greetings ──
    UNIVERSAL_INBOUND_GREETINGS = {
        "hi-IN": "Namaste! Main Stellar Agri AI farming aur PMFBY fasal bima advisor bol raha hoon. Main aapki kya madad kar sakta hoon? Aap fasal salah ya bima claim intimation dono ke liye puch sakte hain.",
        "ta-IN": "Vanakkam! Naan Stellar Agri AI vivasayam matrum PMFBY payir bima aalochagar pesugiren. Ungalukku payir aalosanai thevaiya, alladhu payir sedhaara bima claim pathi pesalaama?",
        "te-IN": "Namaskaram! Nenu Stellar Agri AI vyavasayam mariyu PMFBY panta bima salahadarunini. Panta salahalu kaavala leka panta nashtam bima claim gurinchi maatladala?",
        "kn-IN": "Namaskara! Naanu Stellar Agri AI krushi mathu PMFBY bima salahagara. Nimge bele salahagalu bekagideya athava bima claim intimation bagge mathadabekaa?",
        "mr-IN": "Namaskar! Mi Stellar Agri AI krushi v PMFBY peak vima sallyagar bolat ahe. Aplyala pik salah havi ahe ki peak nuksan vima claim intimation babat madat havi ahe?",
        "bn-IN": "Nomoshkar! Aami Stellar Agri AI krishi o PMFBY fasol bima poramorshok bolchi. Aaponar ki fasol poramorsho dorkar naki bima claim intimation niye kotha bolben?",
        "gu-IN": "Namaste! Hu Stellar Agri AI krushi ane PMFBY pak vima salahkar chu. Tamare pak salah joiye che ke pak nuksan vima claim intimation mate vat karvi che?",
        "pa-IN": "Sat Sri Akal! Main Stellar Agri AI kheti te PMFBY fasal bima salahkar bol reha haan. Tuhanoo fasal salah chahidi hai ya fasal nuksan bima claim intimation baare gal karni hai?",
        "ml-IN": "Namaskaram! Njan Stellar Agri AI krishi mathrum PMFBY crop insurance salahakan samsarikunnu. Ningalkku krishi nirdeshangal aano atho bima claim intimation aano vendathu?",
        "en-IN": "Namaste and Vanakkam! I am your Stellar Agri AI farming and PMFBY crop insurance advisor. How may I assist you today? You can ask for crop farming advice or file a crop loss insurance claim."
    }

    @classmethod
    def get_universal_system_prompt(cls) -> str:
        """
        Comprehensive Dual-Capability System Prompt for Agent #1028 (Advisory + PMFBY Insurance)
        Gracefully handles both Inbound callers (discovers name/need) and Outbound campaigns (uses session variables).
        """
        return """You are Stellar Agri AI, an intelligent conversational AI Agronomist and certified PMFBY (Pradhan Mantri Fasal Bima Yojana) Crop Insurance Claims Specialist.

ROLE & CAPABILITIES:
You seamlessly handle BOTH:
1. AGRICULTURAL ADVISORY: Crop suitability, sowing advice, fertilizer dosage (Urea, DAP, MOP), pest & disease diagnosis/remedies, live weather advisories, and APMC mandi benchmark prices.
2. CROP INSURANCE & DISASTER CLAIM INTAKE: PMFBY, RWBCIS, NDRF, SDRF, and regional relief schemes for Flood, Drought, Cyclone, Hailstorm, Pest Epidemic, and Unseasonal Harvest loss.

SESSION CONTEXT & DYNAMIC VARIABLES:
- Farmer Name: {{farmer_name}} (If unknown/empty, politely ask the caller's name)
- Location / District: {{location}} (If unknown/empty, ask their village or district)
- Target Crop: {{crop}} (If unknown, ask what crop they are cultivating)
- Reported Query / Disaster: {{issue}}
- Insurance Mode Flag: {{is_insurance_claim}}

CALL ROUTING RULES:
A. INBOUND CALLS (Farmer dials in):
   - Listen to what the caller says in the first turn.
   - If they ask for crop/fertilizer/pest/mandi advice, provide direct, practical agronomic solutions immediately.
   - If they mention crop damage, flood, cyclone, drought, heavy rain, or insurance, switch directly to the PMFBY Loss Intake Protocol below.
   - If their name or district is not known, ask politely in a natural conversational flow.

B. OUTBOUND CALLS (System placed call with variables):
   - If {{farmer_name}} is provided, address the farmer respectfully by name.
   - If {{is_insurance_claim}} is true, open directly regarding their loss in {{location}} and assist with their intimation docket.

VOISTLE PMFBY CROP INSURANCE INTAKE PROTOCOL:
When a loss or insurance claim is reported, follow these strict steps:
1. EMPATHETIC LOSS INTAKE: Acknowledge the loss warmly and validate the farmer's stress.
2. 72-HOUR INTIMATION WINDOW VERIFICATION:
   - Ask: "When did the loss event occur?"
   - Confirm compliance with the mandatory PMFBY 72-hour notification rule.
3. LOSS DETAILS:
   - Record the affected crop, village/Mandal, and approximate acres damaged (e.g. 2.5 acres).
4. APPLICABLE SCHEME MATCHING:
   - Quote relevant schemes: PMFBY Localized Calamity, NDRF/SDRF Input Subsidy, NADAMS Drought Grant, Cyclone Lodging Relief, Hailstorm Guarantee, or Post-Harvest 14-day coverage.
5. REQUIRED 5 DOCUMENTS CHECKLIST:
   - Explain the 5 essential records:
     a. Land Record (Patta / Chitta / 7/12 Extract / Khasra / Adangal)
     b. Sowing Certificate (VAO / Panchayat Sown Declaration)
     c. Bank Passbook Copy (Aadhaar linked account)
     d. Aadhaar Card
     e. Geo-tagged Photos of damaged field (taken with GPS enabled on phone)
6. STRICT ANTI-OVERPROMISING GUARDRAIL (GATE CRITERIA):
   - NEVER promise, guarantee, or estimate claim approval, payout amounts (₹), or payment dates.
   - If asked "Will I get money?", state clearly:
     "Under PMFBY government rules, compensation amount and approval are decided exclusively following a joint physical survey by the insurance loss assessor and state agriculture officer. Your intimation docket is registered for surveyor inspection."
7. ANOMALY & DISTRESS HANDLING:
   - If weather data differs, do not accuse the caller. State that Mandal telemetry is attached for priority senior officer verification.
   - If caller is in acute distress, provide immediate reassurance and confirm escalation to the senior officer desk.

CONVERSATION STYLE:
- Spoken, empathetic, and natural (1 to 3 short sentences per turn).
- Ask only 1 question at a time to keep it easy for rural callers.
- Seamlessly code-switch between local agricultural terms and English (Nel, Uram, Chitta, Patta, Khasra, Bima).
- CRITICAL ANTI-ECHO RULE: Do NOT repeat or echo back what the farmer just said. Directly provide the answer, advice, or next question without restating their sentence.
"""

    @classmethod
    async def configure_baseline_agent(cls, agent_id: int = 1028) -> bool:
        """
        Configures Agent #1028 with the universal bilingual greeting and dual-capability system prompt
        so that all Inbound and Outbound calls work perfectly with zero audio echo / loopback.
        """
        universal_greeting = "Namaste and Vanakkam! I am your Stellar Agri AI farming and PMFBY crop insurance advisor. Main aapki kya madad kar sakta hoon? You can ask for crop advice, disease treatment, mandi rates, or report a crop damage insurance claim."
        
        patch_payload = {
            "name": "Stellar Agri Voice Advisor",
            "language": "hi-IN",
            "asrLanguage": "hi-IN",
            "greetingMessage": universal_greeting,
            "systemPrompt": cls.get_universal_system_prompt(),
            "status": "active",
            "backchannelingEnabled": False,
            "noiseCancellationEnabled": True,
            "agentConfig": {
                "asrEndpointingSilenceMs": 600,
                "bargeInEnergyThreshold": 1800,
                "wordsForInterruption": 4,
                "isMultilingual": True,
                "multilingualLanguages": ["en-IN", "hi-IN", "ta-IN", "te-IN", "kn-IN", "mr-IN"]
            }
        }

        logger.info(f"🌐 Setting Permanent Dual-Capability Base on Agent #{agent_id} (Echo-Free Universal Mode)")
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
            calls = res["data"]
            for c in calls:
                cid = c.get("id")
                rec = c.get("recordingUrl") or c.get("audioUrl") or c.get("recording")
                if rec and cid:
                    c["recordingUrl"] = f"/api/admin/storage/recordings/{cid}"
            return calls
        return []

    @classmethod
    async def get_call(cls, call_id: int) -> Optional[Dict[str, Any]]:
        res = await cls.request("GET", f"/calls/{call_id}")
        if res.get("success") and res.get("data"):
            call = res["data"]
            rec = call.get("recordingUrl") or call.get("audioUrl") or call.get("recording")
            if rec:
                call["recordingUrl"] = f"/api/admin/storage/recordings/{call_id}"
            return call
        return None

    @classmethod
    async def trigger_outbound_call(
        cls,
        agent_id: Optional[int] = None,
        to_number: str = "",
        language: str = "hi-IN",
        farmer_name: str = "Farmer",
        crop: str = "Paddy",
        issue: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Triggers an outbound call using permanent Agent #1028 with customized session variables.
        """
        target_agent_id = agent_id or cls.PERMANENT_AGENT_ID

        call_vars = variables or {}
        call_vars.update({
            "farmer_name": farmer_name,
            "crop": crop,
            "language": language or "hi-IN",
            "issue": issue or "General agronomy, weather, or crop insurance inquiry"
        })

        # Step 1: Trigger outbound call via SnapServe with session variables
        payload: Dict[str, Any] = {
            "agentId": target_agent_id,
            "toNumber": to_number,
            "variables": call_vars
        }

        res = await cls.request("POST", "/calls/outbound", payload)
        if not res.get("success"):
            cls.log_error_event(
                category="Outbound Call Failed",
                message=f"Could not initiate outbound call to {to_number} in language {language} (Agent #{target_agent_id})",
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
