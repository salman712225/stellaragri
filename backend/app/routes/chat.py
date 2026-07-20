from typing import Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.chat_service import ChatService

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


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