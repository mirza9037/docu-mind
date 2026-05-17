from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import DocumentUploadResponse, DocumentListResponse, DeleteResponse
from app.services.ingestor import ingest_file
from app.services.vectorstore import list_documents, delete_document

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF or text file and ingest it into the vector store.
    The document is chunked, embedded, and stored in ChromaDB.
    Returns a document_id you can use for scoped queries.
    """
    document_id, filename, chunk_count = ingest_file(file)
    return DocumentUploadResponse(
        document_id=document_id,
        filename=filename,
        chunk_count=chunk_count,
        message=f"Successfully ingested '{filename}' into {chunk_count} chunks.",
    )


@router.get("/", response_model=DocumentListResponse, tags=["Documents"])
def list_all_documents():
    """
    List all documents currently stored in the vector store.
    Returns metadata: filename, upload time, chunk count.
    """
    docs = list_documents()
    return DocumentListResponse(total=len(docs), documents=docs)


@router.delete("/{document_id}", response_model=DeleteResponse)
def delete_document_by_id(document_id: str):
    """
    Remove all chunks of a document from the vector store.
    After deletion the document is no longer searchable.
    """
    deleted = delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")
    return DeleteResponse(
        document_id=document_id,
        message="Document deleted successfully.",
    )
