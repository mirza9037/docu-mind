from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag import answer_question
from app.core.config import get_settings

router = APIRouter(prefix="/chat", tags=["Chat"])
settings = get_settings()


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Ask a question against your uploaded documents.
    
    - Optionally pass a document_id to restrict search to one document.
    - Pass previous turns in history[] for multi-turn conversations.
    - Returns the answer plus the source chunks it was derived from.
    """
    try:
        answer, sources = answer_question(
            question=request.question,
            document_id=request.document_id,
            history=request.history,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    return ChatResponse(
        answer=answer,
        sources=sources,
        model_used=settings.groq_model,
    )
