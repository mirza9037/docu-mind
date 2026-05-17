from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    All settings are read from environment variables or .env file.
    pydantic-settings handles type casting and validation automatically.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # LLM
    groq_api_key: str = "dummy"
    groq_model: str = "llama-3.1-8b-instant"

    # Vector Store
    chroma_persist_dir: str = "./data/chroma_db"
    chroma_collection: str = "documind"

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"

    # App
    app_name: str = "DocuMind API"
    app_version: str = "1.0.0"
    debug: bool = False
    max_upload_size_mb: int = 10
    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k_results: int = 4


@lru_cache()
def get_settings() -> Settings:
    """
    Cached singleton — settings are loaded once, reused everywhere.
    lru_cache means this runs only on first call.
    """
    return Settings()
