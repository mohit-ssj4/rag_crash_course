import importlib

import pytest

from src import config


def test_config_defaults(monkeypatch):
    # Clear environment variables to force defaults
    monkeypatch.delenv("PERSIST_DIRECTORY", raising=False)
    monkeypatch.delenv("COLLECTION_NAME", raising=False)
    monkeypatch.delenv("EMBEDDING_MODEL_NAME", raising=False)
    monkeypatch.delenv("EMBEDDING_BATCH_SIZE", raising=False)
    monkeypatch.delenv("LLM_MODEL_NAME", raising=False)
    monkeypatch.delenv("CHUNK_SIZE", raising=False)
    monkeypatch.delenv("CHUNK_OVERLAP", raising=False)

    importlib.reload(config)

    assert config.COLLECTION_NAME == "aurora_docs"
    assert config.PERSIST_DIRECTORY == "data/vector_store"
    assert config.EMBEDDING_MODEL_NAME == "all-MiniLM-L6-v2"
    assert config.EMBEDDING_BATCH_SIZE == 32
    assert config.CHUNK_SIZE == 1000
    assert config.CHUNK_OVERLAP == 200
    assert config.LLM_MODEL_NAME == "openai/gpt-oss-120b"


def test_config_custom_values(monkeypatch):
    monkeypatch.setenv("CHUNK_SIZE", "500")
    monkeypatch.setenv("CHUNK_OVERLAP", "0")  # Support 0 overlap
    monkeypatch.setenv("EMBEDDING_BATCH_SIZE", "16")
    monkeypatch.setenv("PERSIST_DIRECTORY", "custom_dir")
    monkeypatch.setenv("COLLECTION_NAME", "custom_collection")
    monkeypatch.setenv("EMBEDDING_MODEL_NAME", "custom_embed")
    monkeypatch.setenv("LLM_MODEL_NAME", "custom_llm")

    importlib.reload(config)

    assert config.CHUNK_SIZE == 500
    assert config.CHUNK_OVERLAP == 0
    assert config.EMBEDDING_BATCH_SIZE == 16
    assert config.PERSIST_DIRECTORY == "custom_dir"
    assert config.COLLECTION_NAME == "custom_collection"
    assert config.EMBEDDING_MODEL_NAME == "custom_embed"
    assert config.LLM_MODEL_NAME == "custom_llm"


def test_config_validation_invalid_int(monkeypatch):
    monkeypatch.setenv("CHUNK_SIZE", "invalid_int")
    with pytest.raises(
        ValueError, match="Invalid configuration value for 'CHUNK_SIZE'"
    ):
        importlib.reload(config)


def test_config_validation_negative_int(monkeypatch):
    monkeypatch.setenv("CHUNK_SIZE", "-100")
    with pytest.raises(
        ValueError, match="Invalid configuration value for 'CHUNK_SIZE'"
    ):
        importlib.reload(config)


def test_config_validation_negative_overlap(monkeypatch):
    monkeypatch.setenv("CHUNK_OVERLAP", "-50")
    with pytest.raises(
        ValueError, match="Invalid configuration value for 'CHUNK_OVERLAP'"
    ):
        importlib.reload(config)


def test_config_validation_overlap_exceeds(monkeypatch):
    monkeypatch.setenv("CHUNK_SIZE", "500")
    monkeypatch.setenv("CHUNK_OVERLAP", "600")
    with pytest.raises(ValueError, match="must be less than"):
        importlib.reload(config)


def test_config_console_logging_defaults(monkeypatch):
    monkeypatch.delenv("CONSOLE_LOGGING", raising=False)
    importlib.reload(config)
    assert config.CONSOLE_LOGGING is True


@pytest.mark.parametrize(
    "env_val, expected",
    [
        ("true", True),
        ("TRUE", True),
        ("1", True),
        ("t", True),
        ("yes", True),
        ("y", True),
        ("false", False),
        ("FALSE", False),
        ("0", False),
        ("f", False),
        ("no", False),
        ("n", False),
    ],
)
def test_config_console_logging_custom_values(monkeypatch, env_val, expected):
    monkeypatch.setenv("CONSOLE_LOGGING", env_val)
    importlib.reload(config)
    assert config.CONSOLE_LOGGING is expected


def test_config_console_logging_invalid(monkeypatch):
    monkeypatch.setenv("CONSOLE_LOGGING", "invalid_boolean_string")
    with pytest.raises(
        ValueError, match="Invalid configuration value for 'CONSOLE_LOGGING'"
    ):
        importlib.reload(config)
