import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.logger import logger
from app.rag.rag_service import RAGService
from app.routes.chat import router as chat_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for all-in-one deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(backend_dir)

frontend_dir = os.path.join(root_dir, "frontend")
index_path = os.path.join(root_dir, "index.html")

if os.path.exists(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")


@app.get("/")
async def root():
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "Welcome to Stellar Agri API"
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


@app.on_event("startup")
async def startup():

    logger.info(
        "Starting Stellar Agri Backend..."
    )

    count = RAGService.ingest_folder(
        "uploads"
    )

    logger.info(
        f"{count} chunks indexed."
    )


@app.on_event("shutdown")
async def shutdown():

    logger.info("Stopping Stellar Agri Backend...")


app.include_router(
    chat_router
)