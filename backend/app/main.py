import os
from typing import Optional
from fastapi import FastAPI, Request, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from app.core.config import settings
from app.core.logger import logger
from app.rag.rag_service import RAGService
from app.routes.chat import router as chat_router
from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router, verify_session_token
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for all-in-one deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(backend_dir)

frontend_dir = os.path.join(root_dir, "frontend")
index_path = os.path.join(root_dir, "index.html")
admin_page_path = os.path.join(frontend_dir, "pages", "admin.html")
login_page_path = os.path.join(frontend_dir, "pages", "login.html")

if os.path.exists(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")


@app.get("/")
async def root():
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "Welcome to Stellar Agri API"
    }


@app.get("/login")
async def login_page(
    request: Request,
    stellar_admin_session: Optional[str] = Cookie(None)
):
    token = stellar_admin_session
    if not token:
        auth_hdr = request.headers.get("Authorization", "")
        if auth_hdr.startswith("Bearer "):
            token = auth_hdr.split("Bearer ")[1].strip()

    # If already logged in, redirect directly to /admin
    if token and verify_session_token(token):
        return RedirectResponse(url="/admin", status_code=302)

    if os.path.exists(login_page_path):
        return FileResponse(login_page_path)
    return {
        "message": "Login HTML page not found."
    }


@app.get("/admin")
async def admin_page(
    request: Request,
    stellar_admin_session: Optional[str] = Cookie(None)
):
    token = stellar_admin_session
    if not token:
        auth_hdr = request.headers.get("Authorization", "")
        if auth_hdr.startswith("Bearer "):
            token = auth_hdr.split("Bearer ")[1].strip()

    # Guard: Redirect unauthenticated requests to /login
    if not token or not verify_session_token(token):
        return RedirectResponse(url="/login", status_code=302)

    if os.path.exists(admin_page_path):
        return FileResponse(admin_page_path)
    return {
        "message": "Admin Dashboard HTML not found."
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


@app.on_event("startup")
async def startup():
    logger.info("Starting Stellar Agri Backend...")
    try:
        count = RAGService.ingest_folder("uploads")
        logger.info(f"{count} chunks indexed / available in knowledge base.")
    except Exception as e:
        logger.warning(f"Startup document ingestion notice: {e}")


@app.on_event("shutdown")
async def shutdown():

    logger.info("Stopping Stellar Agri Backend...")


app.include_router(
    auth_router
)
app.include_router(
    chat_router
)
app.include_router(
    admin_router
)


@app.get("/api/storage/recordings/{call_id}")
async def global_call_recording_stream(call_id: int):
    from app.routes.admin import get_call_audio_stream
    return await get_call_audio_stream(call_id)