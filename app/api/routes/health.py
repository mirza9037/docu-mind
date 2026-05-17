from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Liveness check. Verifies the app is running and ChromaDB is accessible."""
    from app.services.vectorstore import get_vectorstore
    
    try:
        db = get_vectorstore()
        count = db._collection.count()
        vs_status = f"connected ({count} chunks loaded)"
    except Exception:
        vs_status = "error connecting to database"

    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        vector_store=vs_status,
    )