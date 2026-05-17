from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Document Schemas ──────────────────────────────────────────────────

class DocumentUploadResponse(BaseModel):
    """Returned after a successful document upload."""
    document_id: str
    filename: str
    chunk_count: int
    message: str


class DocumentInfo(BaseModel):
    """Metadata for a single stored document."""
    document_id: str
    filename: str
    uploaded_at: str
    chunk_count: int


class DocumentListResponse(BaseModel):
    """Returned from GET /documents."""
    total: int
    documents: list[DocumentInfo]


class DeleteResponse(BaseModel):
    """Returned after deleting a document."""
    document_id: str
    message: str


# ── Chat Schemas ──────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    """A single message in a conversation."""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    """Request body for POST /chat."""
    question: str = Field(..., min_length=1, max_length=2000)
    document_id: Optional[str] = Field(
        default=None,
        description="Scope the query to a specific document. If None, searches all docs."
    )
    history: list[ChatMessage] = Field(
        default=[],
        description="Previous conversation turns for context-aware answers."
    )


class Source(BaseModel):
    """A retrieved chunk used to generate the answer."""
    document_id: str
    filename: str
    excerpt: str   # first 200 chars of the chunk
    page: Optional[int] = None


class ChatResponse(BaseModel):
    """Returned from POST /chat."""
    answer: str
    sources: list[Source]
    model_used: str


# ── Health Schema ─────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    vector_store: str
