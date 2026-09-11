from unittest.mock import MagicMock

import numpy as np
import pytest


@pytest.fixture(autouse=True)
def mock_sentence_transformer(monkeypatch):
    """Global autouse fixture to mock SentenceTransformer across all test modules."""

    class MockSentenceTransformer:
        def __init__(self, *args, **kwargs):
            self.model_name = "mock-model"

        def encode(self, texts, *args, **kwargs):
            # Force list type
            if isinstance(texts, str):
                texts = [texts]
            # Return a mock numpy array of float coordinates (matching the sentence-transformer dimension size 384)
            return np.ones((len(texts), 384))

    monkeypatch.setattr(
        "sentence_transformers.SentenceTransformer", MockSentenceTransformer
    )
    monkeypatch.setattr(
        "src.embedding_manager.SentenceTransformer", MockSentenceTransformer
    )


@pytest.fixture(autouse=True)
def mock_groq_client(monkeypatch):
    """Global autouse fixture to mock Groq client across all test modules."""
    mock_client = MagicMock()
    mock_response = MagicMock()

    # Mock output hierarchy: response.choices[0].message.content
    mock_choice = MagicMock()
    mock_choice.message.content = (
        "This is a mock response from Aurora Dynamics RAG LLM."
    )
    mock_response.choices = [mock_choice]

    mock_client.chat.completions.create.return_value = mock_response

    # Apply monkeypatching
    monkeypatch.setattr("groq.Groq", lambda *args, **kwargs: mock_client)
    monkeypatch.setattr("src.llm_client.groq_client", mock_client)


@pytest.fixture(autouse=True)
def mock_load_dotenv(monkeypatch):
    """Global autouse fixture to disable load_dotenv and enforce complete test isolation from local .env."""
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: None)
