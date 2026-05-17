"""
Tests for POST /chat endpoint.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_basic_question():
    """POST /chat with a valid question should return an answer and sources."""
    mock_sources = [
        MagicMock(
            document_id="doc-1",
            filename="notes.txt",
            excerpt="DocuMind uses ChromaDB for vector storage.",
            page=None,
        )
    ]

    with patch("app.api.routes.chat.answer_question") as mock_answer:
        mock_answer.return_value = ("DocuMind uses ChromaDB.", mock_sources)

        response = client.post(
            "/chat/",
            json={"question": "What does DocuMind use for storage?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "model_used" in data
    assert data["answer"] == "DocuMind uses ChromaDB."


def test_chat_with_document_id():
    """Passing document_id should scope the search to that document."""
    with patch("app.api.routes.chat.answer_question") as mock_answer:
        mock_answer.return_value = ("Scoped answer.", [])

        response = client.post(
            "/chat/",
            json={
                "question": "Summarize this document",
                "document_id": "doc-abc",
            },
        )

    assert response.status_code == 200
    # Verify the service was called with the correct document_id
    mock_answer.assert_called_once_with(
        question="Summarize this document",
        document_id="doc-abc",
        history=[],
    )


def test_chat_with_history():
    """Multi-turn conversation: history should be passed to answer_question."""
    history = [
        {"role": "user", "content": "What is RAG?"},
        {"role": "assistant", "content": "RAG stands for Retrieval-Augmented Generation."},
    ]

    with patch("app.api.routes.chat.answer_question") as mock_answer:
        mock_answer.return_value = ("Follow-up answer.", [])

        response = client.post(
            "/chat/",
            json={
                "question": "Can you give me an example?",
                "history": history,
            },
        )

    assert response.status_code == 200
    call_kwargs = mock_answer.call_args.kwargs
    assert len(call_kwargs["history"]) == 2


def test_chat_empty_question():
    """Empty question string should be rejected with 422."""
    response = client.post("/chat/", json={"question": ""})
    assert response.status_code == 422


def test_chat_question_too_long():
    """Question over 2000 chars should be rejected with 422."""
    response = client.post("/chat/", json={"question": "a" * 2001})
    assert response.status_code == 422


def test_chat_llm_error_returns_500():
    """If the LLM throws, the endpoint should return 500."""
    with patch("app.api.routes.chat.answer_question") as mock_answer:
        mock_answer.side_effect = Exception("Groq rate limit hit")

        response = client.post(
            "/chat/",
            json={"question": "What is in this document?"},
        )

    assert response.status_code == 500
    assert "LLM error" in response.json()["detail"]
