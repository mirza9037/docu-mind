"""
Tests for /documents endpoints.
Covers: upload, list, delete — happy paths and error cases.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """GET /health should always return 200 with status=ok."""
    with patch("app.api.routes.health.get_vectorstore") as mock_vs:
        mock_vs.return_value = MagicMock()
        response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_upload_txt_success(tmp_path):
    """POST /documents/upload with a valid .txt should return 201."""
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("This is a test document about AI and machine learning.")

    with patch("app.api.routes.documents.ingest_file") as mock_ingest:
        mock_ingest.return_value = ("doc-123", "test.txt", 3)

        with open(txt_file, "rb") as f:
            response = client.post(
                "/documents/upload",
                files={"file": ("test.txt", f, "text/plain")},
            )

    assert response.status_code == 201
    data = response.json()
    assert data["document_id"] == "doc-123"
    assert data["chunk_count"] == 3
    assert "Successfully ingested" in data["message"]


def test_upload_unsupported_type(tmp_path):
    """Uploading a .csv should return 415 Unsupported Media Type."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("col1,col2\nval1,val2")

    with open(csv_file, "rb") as f:
        response = client.post(
            "/documents/upload",
            files={"file": ("data.csv", f, "text/csv")},
        )

    assert response.status_code == 415


def test_list_documents_empty():
    """GET /documents/ with no docs should return total=0."""
    with patch("app.api.routes.documents.list_documents") as mock_list:
        mock_list.return_value = []
        response = client.get("/documents/")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["documents"] == []


def test_list_documents_with_data():
    """GET /documents/ should return all stored doc metadata."""
    mock_docs = [
        {"document_id": "abc", "filename": "resume.pdf", "uploaded_at": "2026-01-01", "chunk_count": 5},
        {"document_id": "xyz", "filename": "notes.txt", "uploaded_at": "2026-01-02", "chunk_count": 2},
    ]
    with patch("app.api.routes.documents.list_documents") as mock_list:
        mock_list.return_value = mock_docs
        response = client.get("/documents/")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


def test_delete_existing_document():
    """DELETE /documents/{id} for existing doc should return 200."""
    with patch("app.api.routes.documents.delete_document") as mock_del:
        mock_del.return_value = True
        response = client.delete("/documents/doc-123")

    assert response.status_code == 200
    assert response.json()["document_id"] == "doc-123"


def test_delete_nonexistent_document():
    """DELETE /documents/{id} for missing doc should return 404."""
    with patch("app.api.routes.documents.delete_document") as mock_del:
        mock_del.return_value = False
        response = client.delete("/documents/ghost-id")

    assert response.status_code == 404
