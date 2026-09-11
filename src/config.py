import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _get_env_positive_int(key: str, default: int) -> int:
    """Helper function to safely cast and validate environment variables as positive integers (> 0)."""
    val = os.getenv(key)
    if val is None or val.strip() == "":
        return default
    try:
        parsed = int(val)
        if parsed <= 0:
            raise ValueError("Value must be a positive integer.")
        return parsed
    except ValueError as e:
        raise ValueError(
            f"Invalid configuration value for '{key}': '{val}'. "
            f"Configuration error: expected a positive integer."
        ) from e


def _get_env_non_negative_int(key: str, default: int) -> int:
    """Helper function to safely cast and validate environment variables as non-negative integers (>= 0)."""
    val = os.getenv(key)
    if val is None or val.strip() == "":
        return default
    try:
        parsed = int(val)
        if parsed < 0:
            raise ValueError("Value must be a non-negative integer.")
        return parsed
    except ValueError as e:
        raise ValueError(
            f"Invalid configuration value for '{key}': '{val}'. "
            f"Configuration error: expected a non-negative integer."
        ) from e


def _get_env_bool(key: str, default: bool) -> bool:
    """Helper function to safely cast and validate environment variables as booleans."""
    val = os.getenv(key)
    if val is None or val.strip() == "":
        return default
    val_stripped = val.strip().lower()
    if val_stripped in ("true", "1", "t", "y", "yes"):
        return True
    elif val_stripped in ("false", "0", "f", "n", "no"):
        return False
    else:
        raise ValueError(
            f"Invalid configuration value for '{key}': '{val}'. "
            f"Configuration error: expected a boolean value."
        )


# Vector Database settings
PERSIST_DIRECTORY: str = os.getenv("PERSIST_DIRECTORY", "data/vector_store")
COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "aurora_docs")

# Embedding settings
EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
EMBEDDING_BATCH_SIZE: int = _get_env_positive_int("EMBEDDING_BATCH_SIZE", 32)

# LLM model settings
LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "openai/gpt-oss-120b")

# Document chunking settings
CHUNK_SIZE: int = _get_env_positive_int("CHUNK_SIZE", 1000)
CHUNK_OVERLAP: int = _get_env_non_negative_int("CHUNK_OVERLAP", 200)

# Logging settings
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").strip().upper()
CONSOLE_LOGGING: bool = _get_env_bool("CONSOLE_LOGGING", True)

# Validate that overlap is smaller than chunk size
if CHUNK_OVERLAP >= CHUNK_SIZE:
    raise ValueError(
        f"Configuration error: CHUNK_OVERLAP ({CHUNK_OVERLAP}) must be less than CHUNK_SIZE ({CHUNK_SIZE})."
    )
