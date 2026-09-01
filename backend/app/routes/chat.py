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

    response = await ChatService.answer(q)

    return JSONResponse(content=response)


@router.post("/api/request-call")
async def request_instant_call(payload: CallEnquiryRequest):
    """
    Handle farmer enquiry form submission and trigger an instant AI voice call.
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

    # Get active voice agent
    agents = await SnapServeService.get_agents()
    active_agent = next((a for a in agents if a.get("status") == "active"), None)
    agent_id = active_agent.get("id", 1028) if active_agent else 1028

    variables = {
        "farmer_name": payload.farmer_name,
        "crop": payload.crop,
        "issue": payload.issue,
        "language": payload.language,
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