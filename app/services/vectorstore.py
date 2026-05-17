"""
VectorStore service — wraps ChromaDB via LangChain.
ChromaDB natively supports metadata filtering, persistent SQLite storage,
and targeted deletions, making it highly scalable for production.
"""
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import chromadb

from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


def _get_embeddings() -> HuggingFaceEmbeddings:
    """Local sentence-transformers embeddings — no API key needed."""
    return HuggingFaceEmbeddings(model_name=settings.embedding_model)


def _get_db() -> Chroma:
    """
    Initialize or load the persistent ChromaDB instance.
    Chroma automatically handles the SQLite connection and file locking.
    """
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    
    return Chroma(
        client=client,
        collection_name=settings.chroma_collection,
        embedding_function=_get_embeddings(),
    )


def add_chunks(chunks: list[Document], document_id: str, filename: str) -> int:
    """
    Add document chunks to ChromaDB.
    Persistence to disk happens automatically under the hood.
    """
    db = _get_db()
    db.add_documents(chunks)
    
    logger.info(f"Stored {len(chunks)} chunks for '{filename}' (id={document_id})")
    return len(chunks)


def similarity_search(query: str, document_id: str | None = None, k: int = None) -> list[Document]:
    """
    Search the vector database.
    We pass the document_id directly to Chroma's native 'filter' parameter,
    ensuring we only ever query the exact chunks we need.
    """
    k = k or settings.top_k_results
    db = _get_db()
    
    # Native metadata pre-filtering (No more k * 4 post-filtering hacks)
    filter_dict = {"document_id": document_id} if document_id else None
    
    results = db.similarity_search(query, k=k, filter=filter_dict)
    return results


def list_documents() -> list[dict]:
    """
    Use the underlying Chroma client to fetch metadata efficiently 
    without loading heavy vector arrays into memory.
    """
    db = _get_db()
    
    # Fetch only the metadata dictionary from the SQLite database
    collection_data = db._collection.get(include=["metadatas"])
    metadatas = collection_data.get("metadatas", [])
    
    # Group the chunks by document_id to rebuild the document summary
    docs_map = {}
    for meta in metadatas:
        if not meta:
            continue
            
        doc_id = meta.get("document_id")
        if not doc_id:
            continue
            
        if doc_id not in docs_map:
            docs_map[doc_id] = {
                "document_id": doc_id,
                "filename": meta.get("filename", meta.get("source", "unknown")),
                "uploaded_at": meta.get("uploaded_at", ""),
                "chunk_count": 0,
            }
        docs_map[doc_id]["chunk_count"] += 1
        
    return list(docs_map.values())


def delete_document(document_id: str) -> bool:
    """
    Chroma supports native deletion by metadata.
    This executes a single SQLite command without having to rebuild the index.
    """
    db = _get_db()
    
    # Check if the document exists by looking for its IDs
    existing = db._collection.get(where={"document_id": document_id}, include=[])
    if not existing or not existing.get("ids"):
        return False
        
    # Perform an O(1) native deletion
    db._collection.delete(where={"document_id": document_id})
    
    logger.info(f"Deleted document {document_id} from ChromaDB")
    return True


def get_vectorstore():
    """Compatibility shim used by the health check endpoint."""
    return _get_db()