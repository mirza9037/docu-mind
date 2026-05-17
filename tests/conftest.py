"""
Shared fixtures for all tests.
Uses pytest fixtures so test setup/teardown is clean and reusable.
"""
import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app


@pytest.fixture(scope="module")
def client():
    """
    FastAPI TestClient — makes real HTTP calls to your app in-process.
    No server needed; this is how FastAPI recommends testing.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_txt_file(tmp_path):
    """Creates a temporary .txt file for upload tests."""
    f = tmp_path / "sample.txt"
    f.write_text(
        "DocuMind is a RAG-based document Q&A system. "
        "It uses ChromaDB for vector storage and Groq for LLM inference. "
        "Users can upload PDF or text files and ask questions about them."
    )
    return f


@pytest.fixture
def mock_vectorstore():
    """Mocks ChromaDB so tests don't need a real DB."""
    with patch("app.services.vectorstore.get_vectorstore") as mock:
        vs = MagicMock()
        mock.return_value = vs
        yield vs


@pytest.fixture
def mock_groq():
    """Mocks Groq LLM so tests don't consume API credits."""
    with patch("app.services.rag._build_llm") as mock:
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(content="Mocked LLM answer.")
        mock.return_value = llm
        yield llm
