---
title: Project Aurora Production-Grade RAG Refactoring
created: 2026-09-12
updated: 2026-09-12
status: final
---

# PRD: Project Aurora Production-Grade RAG Refactoring
*Working title — Production-Grade Decoupled RAG System*

## 0. Document Purpose
This Product Requirement Document (PRD) is for Product Managers, Developers, and QA Engineers involved in Project Aurora's transition from a single-script localized RAG prototype into a modular, production-ready RAG application. It details the separation of offline ingestion and online retrieval pipelines, centralized configuration/logging, type safety standards, API error resilience, and a comprehensive, fully mocked verification suite. This PRD builds directly upon the strategic directions outlined in `REFACTORING_PLAN.md`.

## 1. Vision
Project Aurora's current prototype provides excellent localized context-bounded Q&A over corporate policies, but suffers from tight coupling (ingesting files on every single run), lack of logging, hardcoded settings, and zero test coverage. The vision of this refactoring is to deliver a highly modular, decoupled, and production-ready CLI application. By separating offline data ingestion from online retrieval, centralizing configuration, adding structured logging, and establishing robust error boundaries, we will dramatically lower latency, reduce API costs, improve developer velocity, and ensure long-term system stability without sacrificing simplicity.

## 2. Target User

### 2.1 Jobs To Be Done
- **Developer/Operator running the RAG CLI:** Needs a fast, robust interface to ingest new corporate policy files and query the existing knowledge base instantly, without redundant embedding operations or startup delays.
- **Maintenance/Platform Engineer:** Needs clear, structured logs and centralized configuration to diagnose issues (e.g., failed API connections, invalid document chunks, or vector DB failures) quickly in production.
- **QA/Validation Engineer:** Needs a comprehensive, isolated automated test suite to ensure no code regressions break pipeline functionality, without depending on live API tokens or heavy network model downloads.

### 2.2 Non-Users (v1)
- **Non-Technical Corporate Employees:** This release will not feature a graphical or web-based UI; it is strictly a developer-focused command-line interface.
- **Real-Time Streaming Users:** The current version will use standard block response generation rather than chunk-by-chunk token streaming.

### 2.3 Key User Journeys

- **UJ-1. Admin ingests documents offline and verifies indexing.**
  - **Persona + context:** Mohit, the platform developer, wants to index the new 2026 Q1 updates.
  - **Entry state:** CLI environment with access to source PDF/TXT files and configured environment variables.
  - **Path:**
    1. Mohit places files in `data/` and runs `python src/cli.py ingest`.
    2. The pipeline loads, chunks, embeds (via local HuggingFace embeddings), and indices the new text documents into ChromaDB.
    3. The CLI prints a structured summary of the operation: total files loaded, total chunks generated, and database insertion confirmation.
  - **Climax:** Mohit checks the database status and sees that the ingestion completed successfully in one offline step.
  - **Resolution:** ChromaDB is persisted to disk, ready for fast, immediate querying.

- **UJ-2. Developer executes a single context-bounded query instantly.**
  - **Persona + context:** Mohit wants to run a single check about the company's remote work policy.
  - **Entry state:** CLI environment with an existing pre-built ChromaDB collection.
  - **Path:**
    1. Mohit executes `python src/cli.py query "What is the remote work policy?"`.
    2. The CLI loads the pre-existing ChromaDB collection directly *without* reading files or regenerating embeddings for raw texts.
    3. The system retrieves relevant chunks, crafts the bound prompt, and sends it to the Groq API.
  - **Climax:** The terminal outputs a clean, well-synthesized answer and list of source files within under 1 second.
  - **Resolution:** The query completes and returns control back to the shell immediately.

- **UJ-3. Support Agent uses the interactive chat session for multi-turn Q&A.**
  - **Persona + context:** An internal operator needs to ask multiple follow-up questions about leave policies.
  - **Entry state:** Pre-existing ChromaDB vector store collection is available.
  - **Path:**
    1. The operator runs `python src/cli.py interactive`.
    2. The terminal displays a welcome message and interactive prompt: `Aurora-RAG >`.
    3. The operator enters a query, gets a synthesized response instantly, and is immediately presented with another prompt.
  - **Climax:** The operator performs multiple separate searches in seconds, saving hours of manual document review.
  - **Resolution:** The operator enters `exit` or `quit` to cleanly terminate the session.

## 3. Glossary
- **Ingestion Pipeline** — The offline process of reading raw source files, partitioning them into deterministic chunks, generating vector representations (embeddings), and saving them into a database.
- **Retrieval Pipeline** — The online process of taking a user query, querying the vector database for semantically similar document chunks, and combining them into a prompt for a Large Language Model (LLM) to generate a response.
- **Vector Store** — A specialized database (ChromaDB) that indexes documents by their semantic vector embeddings to allow extremely fast nearest-neighbor similarity searches.
- **HuggingFace Embedder** — A local model (SentenceTransformer) used to convert text sequences into mathematical vectors of fixed dimension.
- **Groq LLM Client** — The API integration layer that connects to Groq services for high-speed text generation.
- **RAGRetriever** — The unified engine that orchestrates the semantic search query and prompt synthesis. (Renamed from typo `RAGRetiever`).

## 4. Features

### 4.1 Feature 1: Centralized Configuration and Logging Module
**Description:** Consolidates all hardcoded values into a single settings module and replaces standard `print()` statements with structured, severity-aware logging. Realizes UJ-1, UJ-2, and UJ-3.

**Functional Requirements:**

#### FR-1: Environment-Validated Settings Module
The system must parse and validate configuration settings from environment variables with safe, documented defaults.
**Consequences (testable):**
- System loads `.env` or defaults automatically.
- Setting `model_name` can be changed in environment without editing code.
- If invalid values are provided, the module logs a warning or raises a descriptive error.

#### FR-2: Centralized Global Logger
The system must output all standard logs via Python’s standard `logging` library instead of `print()` statements, following a consistent format: `[YYYY-MM-DD HH:MM:SS] [LEVEL] [MODULE] - MESSAGE`.
**Consequences (testable):**
- Output can be directed to stderr, stdout, or a log file.
- Logging levels (DEBUG, INFO, WARNING, ERROR) can be toggled via config.
- Unit tests can suppress/silence logging outputs during execution.

### 4.2 Feature 2: Codebase Typo & Dependency Cleanup
**Description:** Eliminates minor spelling mistakes and structural flaws to enforce PEP 8 guidelines and type safety across modules.

**Functional Requirements:**

#### FR-3: Rename RAGRetiever to RAGRetriever
Surgically rename the file `rag_retriever.py`'s class `RAGRetiever` to `RAGRetriever` and update all associated imports and comments throughout the codebase.
**Consequences (testable):**
- Code contains zero occurrences of the string `RAGRetiever`.
- Module import statement: `from src.rag_retriever import RAGRetriever` succeeds.

#### FR-4: Strict Type Annotations
All core functions in `src/` must feature explicit type annotations for parameters and return types.
**Consequences (testable):**
- Run-time type check or static check (`mypy` or similar) passes without errors.

### 4.3 Feature 3: Decoupled CLI Pipeline (Ingestion vs Retrieval)
**Description:** Decouples offline ingestion from online retrieval, exposing a unified CLI with subcommands to support separate workflows. Realizes UJ-1, UJ-2, and UJ-3.

**Functional Requirements:**

#### FR-5: Ingest Subcommand
Expose a subcommand `python src/cli.py ingest` to load data from the configured directory, chunk, embed, and store files into ChromaDB only when requested.
**Consequences (testable):**
- Ingestion runs on-demand and modifies ChromaDB.
- Running query command does *not* trigger file parsing or indexing.

#### FR-6: Query Subcommand
Expose a subcommand `python src/cli.py query "<query>"` to perform a single semantic search and text generation sequence.
**Consequences (testable):**
- Loads ChromaDB collection directly without file reads.
- Synthesizes and prints response within 1.5 seconds under standard network conditions.

#### FR-7: Interactive Subcommand
Expose a subcommand `python src/cli.py interactive` to start an interactive multi-turn loop.
**Consequences (testable):**
- Drops user into interactive shell `Aurora-RAG >`.
- Supports typing `exit` or `quit` to cleanly exit.

### 4.4 Feature 4: Resilient Service Error Boundaries
**Description:** Implements robust error validation and automatic retries for third-party network APIs to prevent sudden script crashes.

**Functional Requirements:**

#### FR-8: Groq API Error boundaries
Wrap the Groq API integration client with retry capabilities and clean fallback logging in case of network outages or rate limit limits.
**Consequences (testable):**
- Failed Groq network requests retry up to 3 times before failing gracefully.
- User is shown a friendly error message detailing connection issues rather than an unhandled traceback.

#### FR-9: Vector Store Verification Check
Verify ChromaDB directory and collection state before starting the retrieval process.
**Consequences (testable):**
- Running a query when the database is empty outputs a warning instruction to run the `ingest` command first, rather than throwing a raw ChromaDB read exception.

### 4.5 Feature 5: Mocked Pytest Verification Suite
**Description:** Establishes a comprehensive automated testing module to verify system behavior without actual API key usage or remote network dependencies.

**Functional Requirements:**

#### FR-10: HuggingFace Embedding Mocking
The test suite must mock `SentenceTransformer.encode` to return mock NumPy arrays, verifying vector store integration without downloading model weights or allocating GPU resources.
**Consequences (testable):**
- Tests run completely offline and finish in under 5 seconds.

#### FR-11: Groq LLM API Mocking
The test suite must mock the `Groq` client response generation using unittest mocks to verify QA template construction and synthesis logic.
**Consequences (testable):**
- Verification of retriever logic runs without an active `GROQ_API_KEY`.

---

## 5. Non-Goals (Explicit)
- **Web UI / Graphical Dashboard:** Building a frontend user interface is explicitly out of scope for this CLI-only release.
- **Multi-tenant Document isolation:** Support for separating document index structures for multiple independent users or accounts.
- **Dynamic model switching during runtime:** The system is restricted to a single configured embedding model and LLM client model per execution.

---

## 6. MVP Scope

### 6.1 In Scope
- Separated offline ingestion CLI subcommand.
- Centralized `.env` and `src/config.py` loading module.
- Glob-configured `src/logger.py` for structured logs.
- Rename of `RAGRetiever` to `RAGRetriever` and general variable cleanup.
- Standard retry handling for Groq API.
- Fully isolated pytest suite inside `tests/` with 100% mocked embeddings and API calls.

### 6.2 Out of Scope for MVP
- Live internet/web search fallbacks (deferred to v2).
- Automatic database sync on document directory updates (relying on manual `ingest` CLI call).
- Persistent conversation history storage across sessions (deferred to v2).

---

## 7. Success Metrics
- **Performance Budget**: Under preloaded vector DB collection state, a single query executes and generates response within under 1.5 seconds.
- **Test Isolation**: 100% of automated tests pass without an internet connection or active API keys.
- **Code Hygiene**: Static verification shows zero PEP 8 violations and full type safety across new/refactored modules.

---

## 8. Open Questions
1. Should we support file hashing during ingestion to allow incremental ingestion (only indexing files that changed)?
2. What are the fallback procedures if ChromaDB files on disk become corrupted?

---

## 9. Assumptions Index
- **[ASSUMPTION: ChromaDB Persistence]** ChromaDB's persistent on-disk format is compatible between ingestion and retrieval runs without active lock conflicts.
- **[ASSUMPTION: local model cache]** SentenceTransformer models can run offline when cached, and our mock suite completely isolates any initial load phase.
