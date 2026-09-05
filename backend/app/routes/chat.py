from typing import Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.chat_service import ChatService
from app.services.snapserve_service import SnapServeService
from app.core.database import Database

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class CallEnquiryRequest(BaseModel):
    farmer_name: str
    phone_number: str
    crop: Optional[str] = "Paddy / Rice"
    issue: Optional[str] = "General Agronomy Query"
    language: Optional[str] = "hi-IN"


@router.post("/chat")
async def chat(
    payload: Optional[ChatRequest] = None,
    question: Optional[str] = None
):
    q = ""
    if payload and payload.question:
        q = payload.question
    elif question:
        q = question

    if not q:
        return JSONResponse(
            status_code=400,
            content={"error": "Question parameter or JSON payload is required."}
        )

    try:
        response = await ChatService.answer(q)
        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to process agronomy advisory query.",
                "detail": str(e)
            }
        )


class InsuranceCallEnquiryRequest(BaseModel):
    farmer_name: str
    phone_number: str
    location: str
    language: Optional[str] = "hi-IN"
    disaster_type: Optional[str] = "Crop Loss / Natural Calamity"
    crop: Optional[str] = "Paddy / Standing Crop"


@router.post("/api/request-call")
async def request_instant_call(payload: CallEnquiryRequest):
    """
    Handle farmer agronomy enquiry form submission and trigger an instant AI voice call.
    """
    phone = payload.phone_number.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        if len(phone) == 10:
            phone = f"+91{phone}"
        elif len(phone) == 11 and phone.startswith("0"):
            phone = f"+91{phone[1:]}"
        elif len(phone) == 12 and phone.startswith("91"):
            phone = f"+{phone}"
        else:
            phone = f"+91{phone}"

    # Permanently target Stellar Agri Voice Advisor (Agent #1028)
    agent_id = SnapServeService.PERMANENT_AGENT_ID

    variables = {
        "farmer_name": payload.farmer_name,
        "crop": payload.crop,
        "issue": payload.issue,
        "language": payload.language or "hi-IN",
        "alert": f"Farmer {payload.farmer_name} requested advisory for {payload.crop}. Issue: {payload.issue}"
    }

    result = await SnapServeService.trigger_outbound_call(
        agent_id=agent_id,
        to_number=phone,
        language=payload.language or "hi-IN",
        farmer_name=payload.farmer_name,
        crop=payload.crop,
        issue=payload.issue,
        variables=variables
    )

    call_id = None
    status_str = "call_initiated"
    if result.get("success") or result.get("id") or (result.get("data") and result.get("data", {}).get("id")):
        call_id = result.get("id") or (result.get("data", {}).get("id"))
    else:
        status_str = "failed"

    # Persist enquiry to MongoDB / Storage
    saved_enquiry = await Database.save_enquiry({
        "farmer_name": payload.farmer_name,
        "phone_number": phone,
        "crop": payload.crop,
        "language": payload.language,
        "issue": payload.issue,
        "call_id": call_id,
        "agent_id": agent_id,
        "status": status_str
    })

    if call_id or result.get("success"):
        return JSONResponse({
            "success": True,
            "call_id": call_id,
            "enquiry_id": saved_enquiry.get("id"),
            "phone_number": phone,
            "agent_id": agent_id,
            "message": f"Calling {phone} now! Please answer your phone to talk with your AI Agronomist."
        })
    else:
        err_msg = result.get("error") or result.get("details") or "Failed to initiate call."
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": err_msg,
                "enquiry_id": saved_enquiry.get("id")
            }
        )


@router.post("/api/insurance-request-call")
async def request_insurance_call(payload: InsuranceCallEnquiryRequest):
    """
    Handle crop insurance / disaster loss intimation call request.
    Cross-verifies disaster plausibility, logs PMFBY claim docket, and triggers instant voice intake.
    """
    from app.rag.plausibility_engine import PlausibilityEngine
    from datetime import datetime

    phone = payload.phone_number.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        if len(phone) == 10:
            phone = f"+91{phone}"
        elif len(phone) == 11 and phone.startswith("0"):
            phone = f"+91{phone[1:]}"
        elif len(phone) == 12 and phone.startswith("91"):
            phone = f"+{phone}"
        else:
            phone = f"+91{phone}"

    # Evaluate claim plausibility in real time using satellite & meteorological records
    eval_res = PlausibilityEngine.evaluate_claim(
        crop=payload.crop or "Paddy / Standing Crop",
        damage_type=payload.disaster_type or "Flood / Inundation",
        location=payload.location,
        event_date=datetime.now().strftime("%Y-%m-%d"),
        acres_affected=2.0
    )

    initial_status = "flagged_mismatch" if eval_res.get("is_mismatch") else "pending_surveyor_review"

    # Save claim to Claims Docket
    claim_record = await Database.save_claim({
        "farmer_name": payload.farmer_name,
        "phone_number": phone,
        "crop": payload.crop or "Standing Crop",
        "damage_type": payload.disaster_type or "Crop Damage",
        "affected_acres": 2.0,
        "event_date": datetime.now().strftime("%Y-%m-%d"),
        "location": payload.location,
        "plausibility_score": eval_res.get("plausibility_score", 0.90),
        "status": initial_status,
        "flags": eval_res.get("flags", []),
        "notes": f"Voice claim intake initiated from web portal. Applicable clause: {eval_res.get('applicable_pmfby_clause')}"
    })

    # Prepare rich PMFBY session variables for Voice Agent #1028
    variables = {
        "farmer_name": payload.farmer_name,
        "location": payload.location,
        "crop": payload.crop or "Standing Crop",
        "disaster_type": payload.disaster_type or "Crop Damage",
        "is_insurance_claim": True,
        "language": payload.language or "hi-IN",
        "plausibility_score": eval_res.get("plausibility_score", 0.90),
        "pmfby_clause": eval_res.get("applicable_pmfby_clause", "PMFBY Localized Calamity"),
        "alert": f"PMFBY CLAIM INTAKE: Farmer {payload.farmer_name} reporting {payload.disaster_type} in {payload.location}."
    }

    result = await SnapServeService.trigger_outbound_call(
        agent_id=SnapServeService.PERMANENT_AGENT_ID,
        to_number=phone,
        language=payload.language or "hi-IN",
        farmer_name=payload.farmer_name,
        crop=payload.crop or "Standing Crop",
        issue=f"PMFBY Claim: {payload.disaster_type} in {payload.location}",
        variables=variables
    )

    call_id = None
    status_str = "insurance_call_initiated"
    if result.get("success") or result.get("id") or (result.get("data") and result.get("data", {}).get("id")):
        call_id = result.get("id") or (result.get("data", {}).get("id"))
    else:
        status_str = "failed"

    # Persist enquiry to MongoDB
    saved_enquiry = await Database.save_enquiry({
        "farmer_name": payload.farmer_name,
        "phone_number": phone,
        "crop": payload.crop or "Standing Crop",
        "language": payload.language,
        "issue": f"PMFBY CLAIM INTAKE: {payload.disaster_type} in {payload.location} (Claim #{claim_record.get('id')})",
        "call_id": call_id,
        "agent_id": SnapServeService.PERMANENT_AGENT_ID,
        "status": status_str
    })

    if call_id or result.get("success"):
        return JSONResponse({
            "success": True,
            "call_id": call_id,
            "claim_id": claim_record.get("id"),
            "enquiry_id": saved_enquiry.get("id"),
            "plausibility_score": eval_res.get("plausibility_score", 0.90),
            "phone_number": phone,
            "message": f"Calling {phone} now! Please answer your phone to record your PMFBY claim intimation with our Voice Claims Specialist."
        })
    else:
        err_msg = result.get("error") or result.get("details") or "Failed to initiate call."
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": err_msg,
                "claim_id": claim_record.get("id"),
                "enquiry_id": saved_enquiry.get("id")
            }
        )