from unittest.mock import MagicMock

import pytest

from src.embedding_manager import EmbeddingManager
from src.rag_retriever import RAGRetriever
from src.vector_store import VectorStore


def test_rag_retriever_initialization(monkeypatch):
    monkeypatch.setattr(
        "src.vector_store.chromadb.PersistentClient", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        "src.vector_store.VectorStore._initialize_store", lambda *args, **kwargs: None
    )

    vector_store = VectorStore()
    embedding_manager = EmbeddingManager()

    retriever = RAGRetriever(vector_store, embedding_manager)
    assert retriever.vector_store is vector_store
    assert retriever.embedding_manager is embedding_manager


def test_rag_retriever_empty_query(monkeypatch):
    monkeypatch.setattr(
        "src.vector_store.VectorStore._initialize_store", lambda *args, **kwargs: None
    )

    vector_store = VectorStore()
    embedding_manager = EmbeddingManager()
    retriever = RAGRetriever(vector_store, embedding_manager)

    response = retriever.generate_response("")
    assert response["answer"] == "I don't know based on the available documents."
    assert response["confidence"] == "0.00%"
    assert response["sources"] == []


def test_rag_retriever_groq_retry_success(monkeypatch):
    """Verifies that retriever retries and succeeds if Groq fails transiently."""
    monkeypatch.setattr(
        "src.vector_store.VectorStore._initialize_store", lambda *args, **kwargs: None
    )
    # Mock retriever _retrieve method to return dummy document context
    monkeypatch.setattr(
        "src.rag_retriever.RAGRetriever._retrieve",
        lambda *args, **kwargs: [
            {
                "content": "hello text",
                "metadata": {"source": "f.txt"},
                "similarity_score": 0.85,
            }
        ],
    )

    vector_store = VectorStore()
    embedding_manager = EmbeddingManager()
    retriever = RAGRetriever(vector_store, embedding_manager)

    # Mock groq completion with a function that fails twice, then succeeds on 3rd attempt
    call_count = 0
    mock_choice = MagicMock()
    mock_choice.message.content = "Retried answer."
    success_response = MagicMock(choices=[mock_choice])

    def mock_create(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Transient Groq HTTP Error")
        return success_response

    monkeypatch.setattr("src.rag_retriever.groq_client.chat.completions.create", mock_create)
    # Mock sleep to run instantly without delay during test execution
    monkeypatch.setattr("time.sleep", lambda *args, **kwargs: None)

    result = retriever.generate_response("hello query")
    assert result["answer"] == "Retried answer."
    assert call_count == 3


def test_rag_retriever_groq_retry_exhausted_fallback(monkeypatch):
    """Verifies that if Groq fails continuously, the system returns a friendly default response."""
    monkeypatch.setattr(
        "src.vector_store.VectorStore._initialize_store", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        "src.rag_retriever.RAGRetriever._retrieve",
        lambda *args, **kwargs: [
            {
                "content": "hello text",
                "metadata": {"source": "f.txt"},
                "similarity_score": 0.85,
            }
        ],
    )

    vector_store = VectorStore()
    embedding_manager = EmbeddingManager()
    retriever = RAGRetriever(vector_store, embedding_manager)

    # Always raise errors
    def mock_create(*args, **kwargs):
        raise Exception("Fatal Groq API Outage")

    monkeypatch.setattr("src.rag_retriever.groq_client.chat.completions.create", mock_create)
    monkeypatch.setattr("time.sleep", lambda *args, **kwargs: None)

    result = retriever.generate_response("hello query")
    assert result["answer"] == "I don't know based on the available documents."
    assert result["confidence"] == "0.00%"
