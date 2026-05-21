"""
DocuMind API — Entry point
FastAPI app wiring: routers, middleware, startup/shutdown events.
"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import logger
from app.api.routes import health, documents, chat

settings = get_settings()

# Resolve frontend dir relative to this file so it works regardless of CWD
# __file__ = .../documind/app/main.py  →  parent.parent = .../documind/
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup / shutdown logic.
    FastAPI's recommended way (replaces deprecated @app.on_event).
    """
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"LLM: Groq / {settings.groq_model}")
    logger.info(f"Vector store: ChromaDB @ {settings.chroma_persist_dir}")
    yield
    logger.info("Shutting down DocuMind API")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A production-ready RAG API. Upload documents, then chat with them.\n\n"
        "Built with FastAPI · LangChain · ChromaDB · Groq"
    ),
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────
# Configured for decoupled architecture
app.add_middleware(
    CORSMiddleware,
    # Replace "*" with your actual Vercel domain (e.g., ["https://documind.vercel.app"]) once deployed
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(chat.router)

# ── Frontend ──────────────────────────────────────────────────────────
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")