from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from pydantic import BaseModel

from app.core.config import settings
from app.services.snapserve_service import SnapServeService
from app.core.database import Database

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])


class OutboundCallRequest(BaseModel):
    agentId: int
    toNumber: str
    farmerName: Optional[str] = "Farmer"
    crop: Optional[str] = "Rice"
    language: Optional[str] = "hi-IN"
    alertMessage: Optional[str] = None


class AssignPhoneRequest(BaseModel):
    agentId: int


@router.get("/status")
async def get_status():
    """
    Get live MCP connection health, SnapServe wallet balance, telephony, and agent counts.
    """
    status_data = await SnapServeService.get_system_status()
    return JSONResponse(content=status_data)


@router.get("/agents")
async def get_agents():
    """
    List all configured agents.
    """
    agents = await SnapServeService.get_agents()
    return JSONResponse(content=agents)


@router.patch("/agents/{agent_id}/toggle")
async def toggle_agent(agent_id: int):
    """
    Toggle agent active / draft status.
    """
    result = await SnapServeService.toggle_agent(agent_id)
    return JSONResponse(content=result)


@router.get("/phone-numbers")
async def get_phone_numbers():
    """
    List all available and assigned phone numbers.
    """
    phones = await SnapServeService.get_phone_numbers()
    return JSONResponse(content=phones)


@router.patch("/phone-numbers/{phone_id}/assign")
async def assign_phone(phone_id: int, payload: AssignPhoneRequest):
    """
    Assign a phone number to an agent.
    """
    result = await SnapServeService.assign_phone(phone_id, payload.agentId)
    return JSONResponse(content=result)


@router.get("/calls")
async def get_calls(
    agentId: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    Fetch live call logs, audio recordings, and transcripts.
    """
    calls = await SnapServeService.get_calls(agent_id=agentId, status=status)
    
    if search:
        s = search.lower()
        calls = [
            c for c in calls
            if s in (c.get("toNumber") or "").lower()
            or s in (c.get("transcript") or "").lower()
            or s in (c.get("callSummary") or "").lower()
            or s in (c.get("agentName") or "").lower()
        ]
        
    return JSONResponse(content=calls)


@router.get("/calls/{call_id}")
async def get_call_detail(call_id: int):
    """
    Fetch deep details and transcript for a specific call.
    """
    call = await SnapServeService.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call record not found.")
    return JSONResponse(content=call)


@router.get("/storage/recordings/{call_id}")
@router.get("/calls/{call_id}/audio")
async def get_call_audio_stream(call_id: int):
    """
    Stream audio recording from SnapServe API with full authentication and range headers.
    """
    url = f"{settings.SNAPSERVE_BASE_URL.rstrip('/')}/storage/recordings/{call_id}"
    req = urllib.request.Request(url, headers=SnapServeService.get_headers())
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        media_type = resp.headers.get("Content-Type", "audio/wav")

        def iter_stream():
            try:
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    yield chunk
            finally:
                resp.close()

        return StreamingResponse(
            iter_stream(),
            media_type=media_type,
            headers={
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Content-Disposition": f'inline; filename="call_{call_id}.wav"'
            }
        )
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise HTTPException(status_code=404, detail="Audio recording not available for this call.")
        raise HTTPException(status_code=e.code, detail=f"SnapServe audio error: {e.reason}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calls/outbound")
async def initiate_test_call(payload: OutboundCallRequest):
    """
    Trigger an outbound test call to a farmer with custom advisory variables.
    """
    variables = {
        "farmer_name": payload.farmerName,
        "crop": payload.crop,
        "language": payload.language or "hi-IN"
    }
    if payload.alertMessage:
        variables["alert"] = payload.alertMessage

    result = await SnapServeService.trigger_outbound_call(
        agent_id=payload.agentId,
        to_number=payload.toNumber,
        language=payload.language or "hi-IN",
        farmer_name=payload.farmerName,
        crop=payload.crop,
        issue=payload.alertMessage,
        variables=variables
    )
    return JSONResponse(content=result)


@router.get("/errors-and-logs")
async def get_errors_and_logs():
    """
    Aggregated error log stream, latency benchmarks, and diagnostics.
    """
    status_data = await SnapServeService.get_system_status()
    calls = await SnapServeService.get_calls()
    
    # Calculate performance metrics
    total_calls = len(calls)
    completed_calls = [c for c in calls if c.get("status") == "completed"]
    failed_calls = [c for c in calls if c.get("status") in ["failed", "no_pickup", "cancelled", "busy"]]
    
    avg_stt_latency = 0
    avg_llm_latency = 0
    avg_tts_latency = 0
    
    stt_vals = [c.get("sttLatencyMs") for c in calls if c.get("sttLatencyMs") is not None]
    llm_vals = [c.get("llmLatencyMs") for c in calls if c.get("llmLatencyMs") is not None]
    tts_vals = [c.get("ttsFirstChunkMs") for c in calls if c.get("ttsFirstChunkMs") is not None]
    
    if stt_vals:
        avg_stt_latency = int(sum(stt_vals) / len(stt_vals))
    if llm_vals:
        avg_llm_latency = int(sum(llm_vals) / len(llm_vals))
    if tts_vals:
        avg_tts_latency = int(sum(tts_vals) / len(tts_vals))

    return JSONResponse(content={
        "recentErrors": status_data.get("recentErrors", []),
        "metrics": {
            "totalCalls": total_calls,
            "completedCalls": len(completed_calls),
            "failedCalls": len(failed_calls),
            "successRate": round((len(completed_calls) / total_calls * 100), 1) if total_calls > 0 else 100.0,
            "avgSttLatencyMs": avg_stt_latency,
            "avgLlmLatencyMs": avg_llm_latency,
            "avgTtsFirstChunkMs": avg_tts_latency
        },
        "mcpStatus": status_data.get("mcp", {}),
        "wallet": status_data.get("wallet", {})
    })


@router.post("/provision-stellar-agent")
async def provision_stellar_agent():
    """
    Auto-provision or update the specialized Stellar Agri Voice Advisor agent on SnapServe.
    """
    agent_payload = {
        "name": "Stellar Agri Voice Advisor",
        "agentMode": "managed",
        "agentType": "customer_support",
        "status": "active",
        "language": "hi-IN",
        "asrProvider": "sarvam",
        "asrModel": "saaras:v3",
        "asrLanguage": "hi-IN",
        "asrBackgroundDenoising": True,
        "asrSmartEndpointing": "livekit",
        "llmProvider": "sarvam",
        "llmModel": "sarvam-105b-conversations",
        "ttsProvider": "sarvam",
        "ttsVoice": "ritu",
        "ttsModel": "bulbul:v3",
        "telephonyProvider": "vobiz",
        "firstSpeaker": "assistant",
        "greetingMessage": "Namaste and Vanakkam! I am your Stellar Agri AI farming and PMFBY crop insurance advisor. Main aapki kya madad kar sakta hoon? You can ask for crop advice, disease treatment, mandi rates, or report a crop damage insurance claim.",
        "systemPrompt": SnapServeService.get_universal_system_prompt(),
        "endCallPhrases": "dhanyawad,alvida,goodbye,bye,ram ram,namaste,thank you",
        "silenceTimeoutSeconds": 25,
        "backchannelingEnabled": True,
        "backchannelingFrequency": 0.4,
        "noiseCancellationEnabled": True,
        "tools": [
            {
                "type": "end_call",
                "name": "end_call",
                "description": "End call when conversation is finished"
            }
        ]
    }
    
    result = await SnapServeService.create_agent(agent_payload)
    if result.get("success") and result.get("data", {}).get("id"):
        agent_id = result["data"]["id"]
        # Try assigning existing phone number
        phones = await SnapServeService.get_phone_numbers()
        if phones:
            await SnapServeService.assign_phone(phones[0]["id"], agent_id)
            
    return JSONResponse(content=result)


# ── MongoDB Farmer Enquiries Management ──

class UpdateEnquiryStatusRequest(BaseModel):
    status: str


@router.get("/enquiries")
async def get_enquiries(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100)
):
    """
    Fetch all farmer call enquiries from MongoDB.
    """
    enquiries = await Database.get_enquiries(search=search, status=status, limit=limit)
    return JSONResponse(content=enquiries)


@router.patch("/enquiries/{enquiry_id}/status")
async def update_enquiry_status(enquiry_id: str, payload: UpdateEnquiryStatusRequest):
    """
    Update enquiry resolution state (e.g. resolved, pending, follow_up).
    """
    success = await Database.update_enquiry_status(enquiry_id, payload.status)
    if not success:
        raise HTTPException(status_code=404, detail="Enquiry not found.")
    return {"success": True, "message": "Enquiry status updated."}


@router.delete("/enquiries/{enquiry_id}")
async def delete_enquiry(enquiry_id: str):
    """
    Delete an enquiry record from the database.
    """
    success = await Database.delete_enquiry(enquiry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Enquiry not found.")
    return {"success": True, "message": "Enquiry deleted."}


@router.get("/database-status")
async def get_database_status():
    """
    Get MongoDB Atlas connection status and storage mode.
    """
    db_status = await Database.get_status()
    return JSONResponse(content=db_status)


# ── PMFBY Crop Insurance Claims Docket Endpoints ──

class ClaimCreateRequest(BaseModel):
    farmer_name: str
    phone_number: str
    crop: str
    damage_type: str
    affected_acres: float
    event_date: Optional[str] = None
    location: str
    notes: Optional[str] = None


class ClaimStatusUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = None


class PlausibilityCheckRequest(BaseModel):
    crop: str
    damage_type: str
    location: str
    event_date: Optional[str] = None
    acres_affected: Optional[float] = None


@router.get("/claims")
async def get_claims(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100)
):
    """
    Fetch all crop insurance claims docket records.
    """
    claims = await Database.get_claims(search=search, status=status, limit=limit)
    return JSONResponse(content=claims)


@router.post("/claims")
async def create_claim(payload: ClaimCreateRequest):
    """
    Create a new structured claim record with automatic weather plausibility evaluation.
    """
    from app.rag.plausibility_engine import PlausibilityEngine

    eval_result = PlausibilityEngine.evaluate_claim(
        crop=payload.crop,
        damage_type=payload.damage_type,
        location=payload.location,
        event_date=payload.event_date,
        acres_affected=payload.affected_acres
    )

    initial_status = "flagged_mismatch" if eval_result.get("is_mismatch") else "pending_surveyor_review"

    claim_data = {
        "farmer_name": payload.farmer_name,
        "phone_number": payload.phone_number,
        "crop": payload.crop,
        "damage_type": payload.damage_type,
        "affected_acres": payload.affected_acres,
        "event_date": payload.event_date,
        "location": payload.location,
        "plausibility_score": eval_result.get("plausibility_score", 0.85),
        "status": initial_status,
        "flags": eval_result.get("flags", []),
        "notes": payload.notes or f"Plausibility status: {eval_result.get('status')}. Notes: {'; '.join(eval_result.get('evidence_notes', []))}"
    }

    saved = await Database.save_claim(claim_data)
    return JSONResponse(content={"success": True, "claim": saved, "evaluation": eval_result})


@router.post("/claims/evaluate-plausibility")
async def evaluate_claim_plausibility(payload: PlausibilityCheckRequest):
    """
    Evaluate damage claim plausibility in real-time against live weather and disaster registries.
    """
    from app.rag.plausibility_engine import PlausibilityEngine

    result = PlausibilityEngine.evaluate_claim(
        crop=payload.crop,
        damage_type=payload.damage_type,
        location=payload.location,
        event_date=payload.event_date,
        acres_affected=payload.acres_affected
    )
    return JSONResponse(content=result)


@router.patch("/claims/{claim_id}/status")
async def update_claim_status(claim_id: str, payload: ClaimStatusUpdateRequest):
    """
    Update claim review/escalation status.
    """
    success = await Database.update_claim_status(claim_id, payload.status, payload.notes)
    if not success:
        raise HTTPException(status_code=404, detail="Claim record not found.")
    return {"success": True, "message": "Claim status updated."}


# ── Proactive Hazard Detection & Outreach Endpoints ──

class TriggerHazardCampaignRequest(BaseModel):
    district: str
    phone_numbers: Optional[List[str]] = None
    custom_hazard_msg: Optional[str] = None


@router.get("/hazards")
async def get_regional_hazards():
    """
    Scan real-time meteorological & ISRO Bhuvan satellite hazards across agricultural zones.
    """
    from app.services.proactive_disaster_monitor import ProactiveDisasterMonitor
    hazards = await ProactiveDisasterMonitor.scan_regional_hazards()
    return JSONResponse(content=hazards)


@router.post("/hazards/trigger-campaign")
async def trigger_hazard_campaign(payload: TriggerHazardCampaignRequest):
    """
    1-Click Trigger proactive outbound AI calls (Mode B) to farmers in an affected district.
    """
    from app.services.proactive_disaster_monitor import ProactiveDisasterMonitor
    result = await ProactiveDisasterMonitor.trigger_proactive_outreach(
        district=payload.district,
        phone_numbers=payload.phone_numbers,
        custom_hazard_msg=payload.custom_hazard_msg
    )
    return JSONResponse(content=result)
