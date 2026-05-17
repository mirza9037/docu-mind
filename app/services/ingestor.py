"""
Ingestor service — handles file reading and chunking.
Supports PDF and plain text files for now.
"""
import uuid
import tempfile
import os
from datetime import datetime, timezone
from fastapi import UploadFile, HTTPException
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()

SUPPORTED_TYPES = {
    "application/pdf": ".pdf",
    "text/plain": ".txt",
}


def _get_loader(filepath: str, content_type: str):
    """Pick the right LangChain loader based on file type."""
    if content_type == "application/pdf":
        return PyPDFLoader(filepath)
    return TextLoader(filepath, encoding="utf-8")


def ingest_file(file: UploadFile) -> tuple[str, str, int]:
    """
    Main entry point for document ingestion.
    
    Steps:
      1. Validate file type and size
      2. Save to a temp file (LangChain loaders need a path)
      3. Load and split into chunks
      4. Add metadata (uploaded_at, source)
      5. Push chunks to ChromaDB via vectorstore service
    
    Returns: (document_id, filename, chunk_count)
    """
    from app.services.vectorstore import add_chunks  # avoid circular import

    # 1. Validate
    content_type = file.content_type or ""
    if content_type not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{content_type}'. Allowed: PDF, plain text."
        )

    # 2. Save to temp file
    suffix = SUPPORTED_TYPES[content_type]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = file.file.read()

        max_bytes = settings.max_upload_size_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_upload_size_mb}MB"
            )

        tmp.write(content)
        tmp_path = tmp.name

    try:
        # 3. Load document
        loader = _get_loader(tmp_path, content_type)
        raw_docs = loader.load()

        # 4. Split into overlapping chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_documents(raw_docs)

        if not chunks:
            raise HTTPException(status_code=422, detail="Document appears to be empty.")

        # 5. Attach metadata to every chunk
        document_id = str(uuid.uuid4())
        uploaded_at = datetime.now(timezone.utc).isoformat()
        for chunk in chunks:
            chunk.metadata["document_id"] = document_id
            chunk.metadata["uploaded_at"] = uploaded_at
            chunk.metadata["source"] = file.filename

        # 6. Store
        chunk_count = add_chunks(chunks, document_id, file.filename)
        logger.info(f"Ingested '{file.filename}' → {chunk_count} chunks (id={document_id})")
        return document_id, file.filename, chunk_count

    finally:
        os.unlink(tmp_path)   # always clean up the temp file
