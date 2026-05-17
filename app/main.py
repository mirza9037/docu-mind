"""
DocuMind API — Entry point
FastAPI app wiring: routers, middleware, startup/shutdown events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.logging import logger
from app.api.routes import health, documents, chat

settings = get_settings()


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
# Allow all origins in dev. Tighten this in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────
from fastapi.staticfiles import StaticFiles
import os

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(chat.router)

# Ensure frontend directory exists
os.makedirs("frontend", exist_ok=True)

# Mount the frontend directory to serve static files (HTML, CSS, JS)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
