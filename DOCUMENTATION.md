# 📊 Aurora Dynamics RAG Project Documentation

## Executive Summary

This document provides a comprehensive technical overview and architectural blueprint of the **Aurora Dynamics RAG (Retrieval-Augmented Generation)** pipeline. Designed as a localized knowledge retrieval system, the pipeline loads corporate policy and operational manuals, chunks the data, embeds the text using localized sentence-transformer models, stores them in a persistent ChromaDB database, and queries Groq's LLM cloud service for context-bounded QA.

---

## 🏗️ System Architecture

The pipeline follows a modular, feed-forward RAG architecture:

```
[ Raw Text Data ] 📂 (data/*.txt)
        │
        ▼
 [ DataLoader ] 🔄 (langchain Documents with Metadata)
        │
        ▼
[ DataChunker ] ✂️ (Recursive Splitter: CHUNK_SIZE, CHUNK_OVERLAP)
        │
        ▼
[ EmbeddingManager ] 🧠 (sentence-transformers: EMBEDDING_MODEL_NAME)
        │
        ▼
 [ VectorStore ] 💾 (ChromaDB Persistent Client / cosine space)
        │
        ▼
[ RAGRetriever ] 🔍 (Similarity search & exponential retries)
        │
        ▼
  [ LLM Client ] 💬 (Groq API / LLM_MODEL_NAME)
        │
        ▼
  [ Single CLI ] 🚀 (src/cli.py: ingest, query, interactive)
```

---

## 🧩 Architectural Modules

### 1. Centralized Settings & Validation (`config`)

- **Location:** `src/config.py`
- **Functionality:**
  - Standardizes settings loading from `.env` environment files utilizing `python-dotenv`.
  - Enforces type validation via helper functions `_get_env_positive_int` (for model batch sizes and chunk sizes) and `_get_env_non_negative_int` (supporting zero-overlap chunk configurations).
  - Enforces logical invariant constraints: raises an informative `ValueError` if `CHUNK_OVERLAP` is greater than or equal to `CHUNK_SIZE`.
  - **Exposed Constants:**
    - `PERSIST_DIRECTORY` (default: `"data/vector_store"`)
    - `COLLECTION_NAME` (default: `"aurora_docs"`)
    - `EMBEDDING_MODEL_NAME` (default: `"all-MiniLM-L6-v2"`)
    - `EMBEDDING_BATCH_SIZE` (default: `32`)
    - `LLM_MODEL_NAME` (default: `"openai/gpt-oss-120b"`)
    - `CHUNK_SIZE` (default: `1000`)
    - `CHUNK_OVERLAP` (default: `200`)
    - `LOG_LEVEL` (default: `"INFO"`)
    - `CONSOLE_LOGGING` (default: `True`)

### 2. Standardized Global Logging (`logger`)

- **Location:** `src/logger.py`
- **Functionality:**
  - Instantiates standardized, severity-aware loggers utilizing Python's built-in `logging` module.
  - Formats all log lines globally: `[YYYY-MM-DD HH:MM:SS] [LEVEL] [MODULE] - MESSAGE`.
  - Supports disabling terminal-oriented log outputs via `CONSOLE_LOGGING = False` (attaches a `logging.NullHandler` instead of `StreamHandler(sys.stderr)`), ensuring clean output for scripts and query mode.
  - Features strict logging level whitelisting (`VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}`) to block malicious lookup injection or class TypeErrors.
  - Controls handler propagation to prevent double logging inside standard CLI outputs.

### 3. Data Ingestion & Loader (`DataLoader`)

- **Location:** `src/data_loader.py`
- **Class:** `DataLoader`
- **Functionality:**
  - Scans a target directory (`data/`) for files matching a glob pattern (default `*.txt`).
  - Reads text files using `utf-8` encoding.
  - Converts raw content into standard LangChain `Document` objects.
  - Attaches semantic metadata for tracking and provenance:
    - `source`: Absolute or relative path to the file.
    - `file_name`: Name of the file.
    - `file_type`: File extension (e.g., `.txt`).
  - Rewritten to utilize global loggers instead of print statements.

### 4. Text Partitioning & Segmentation (`DataChunker`)

- **Location:** `src/data_chunker.py`
- **Class:** `DataChunker`
- **Functionality:**
  - Ingests loaded LangChain `Document` objects.
  - Uses LangChain's `RecursiveCharacterTextSplitter` to partition long text files into digestible chunks.
  - Uses centralized constants `CHUNK_SIZE` and `CHUNK_OVERLAP` from `src/config.py`.

### 5. Numerical Vector Embedding (`EmbeddingManager`)

- **Location:** `src/embedding_manager.py`
- **Class:** `EmbeddingManager`
- **Functionality:**
  - Employs the `sentence-transformers` library to run semantic modeling locally.
  - Uses centralized constants `EMBEDDING_MODEL_NAME` and `EMBEDDING_BATCH_SIZE` from `src/config.py`.
  - Normalizes the generated embeddings so they represent unit vectors, optimizing distance comparisons.

### 6. Vector Database & Storage (`VectorStore`)

- **Location:** `src/vector_store.py`
- **Class:** `VectorStore`
- **Functionality:**
  - Manages storage using `chromadb` (ChromaDB persistent client).
  - Uses centralized constants `PERSIST_DIRECTORY` and `COLLECTION_NAME` from `src/config.py`.
  - **Distance Metric:** Cosine similarity (specified via metadata `{"hnsw:space": "cosine"}`).
  - Each stored document record maps a unique ID, vector embedding, and metadata dictionary. Corrected PEP 8 singleton comparisons (`is None`).

### 7. LLM Client Gateway (`LLMClient`)

- **Location:** `src/llm_client.py`
- **Functionality:**
  - Instantiates the `Groq` client wrapper.
  - Uses centralized constant `LLM_MODEL_NAME` from `src/config.py` as default model.

### 8. Retrieval & Context Synthesis (`RAGRetriever`)

- **Location:** `src/rag_retriever.py`
- **Class:** `RAGRetriever`
- **Functionality:**
  - Executes the core Retrieval-Augmented Generation.
  - **Vector Querying:** Converts user query into an embedding and searches `VectorStore` for top-k results.
  - **Filtering:** Converts Chroma cosine distances into similarity scores and filters out matches that fall below `score_threshold`.
  - **Contextual Injection:** Aggregates raw text of the top matches into a cohesive single string context.
  - **Standardized Schema:** Re-written to guarantee consistent return shapes (always dictionary matching schema: `{answer, sources, confidence}`).
  - **Robust Retries:** Features automatic request retry loops (up to 3 retries) with exponential backoffs to recover from transient remote HTTP failures safely, falling back to clean warning messages instead of tracebacks on total outage.

### 9. Decoupled CommandLine Interface (`cli`)

- **Location:** `src/cli.py`
- **Functionality:**
  - Acts as the primary application entrypoint.
  - Configures standard `argparse` to handle subcommand dispatching:
    - `ingest`: Execute document loader, chunker, and database indexing.
    - `query "<query>"`: Direct-load pre-computed collections, execute retrieval, and format/print LLM response.
    - `interactive`: Start a warm chat shell loop (`Aurora-RAG >`) for rapid multi-turn searches.
  - **Database Empty Protection:** Verifies collection state before queries, gracefully warning users to run `ingest` first on missing on-disk collections.
  - **CLI Formatting:** Visually separates responses into dedicated blocks:
    - `LLM Response:` - The generated text answer.
    - `Confidence Score:` - The highest matching similarity score in percentages.
    - `Sources:` - Bulleted list of retrieved file paths and individual distance scores.

### 10. Legacy Retrospective Wrapper (`run_pipeline`)

- **Location:** `src/run_pipeline.py`
- **Functionality:**
  - Maintained to support legacy calling interfaces without breaking backward-compatibility.
  - Fully retrofitted to remove all logic duplication and directly delegate calls to `cli.py` handlers.

---

## 📊 Sample Corporate Dataset

The default corpus resides in `data/` and contains operational materials for **Aurora Dynamics** (a fictional robotics startup based in Bengaluru):

- `01-company-overview.txt`: Corporate history, mission statement, office locations, and funding history.
- `02-product-overview.txt`: Flagship robot Carrier X2 specs, payloads, navigation, and lidar tech.
- `03-leave-policy.txt`: Standard annual, parental, and sick leave guidelines.
- `04-remote-work-policy.txt`: Core hours, stipends, and physical/digital security requirements.
- `05-support-runbook.txt`: Maintenance, troubleshooting, and error codes for Carrier X2.
- `06-q1-2025-update.txt`: Latest performance updates, hospital deployments, and revenue reports.
