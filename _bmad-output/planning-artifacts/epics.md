---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
inputDocuments:
  - C:\Users\mohit.singh1\Documents\Workspace\Personal\Projects\AI\Learnings\RAG\rag_crash_course\_bmad-output\planning-artifacts\prds\prd-rag_crash_course-2026-09-12\prd.md
  - C:\Users\mohit.singh1\Documents\Workspace\Personal\Projects\AI\Learnings\RAG\rag_crash_course\REFACTORING_PLAN.md
---

# rag_crash_course - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for rag_crash_course, decomposing the requirements from the PRD and Architecture refactoring plan into implementable stories.

## Requirements Inventory

### Functional Requirements

- **FR-1: Environment-Validated Settings Module** - Parse and validate configuration settings from environment variables with safe, documented defaults.
- **FR-2: Centralized Global Logger** - Output all standard logs via Python’s standard logging library instead of print() statements, using formatting `[YYYY-MM-DD HH:MM:SS] [LEVEL] [MODULE] - MESSAGE`.
- **FR-3: Rename RAGRetiever to RAGRetriever** - Rename the file rag_retriever.py's class RAGRetiever to RAGRetriever and update all associated imports and comments throughout the codebase.
- **FR-4: Strict Type Annotations** - Ensure all core functions in src/ feature explicit type annotations for parameters and return types.
- **FR-5: Ingest Subcommand** - Expose a subcommand `python src/cli.py ingest` to load data from the configured directory, chunk, embed, and store files into ChromaDB only when requested.
- **FR-6: Query Subcommand** - Expose a subcommand `python src/cli.py query "<query>"` to perform a single semantic search and text generation sequence.
- **FR-7: Interactive Subcommand** - Expose a subcommand `python src/cli.py interactive` to start an interactive multi-turn loop.
- **FR-8: Groq API Error boundaries** - Wrap the Groq API integration client with retry capabilities (up to 3 retries) and clean fallback logging in case of network outages or rate limit limits.
- **FR-9: Vector Store Verification Check** - Verify ChromaDB directory and collection state before starting the retrieval process. Warn the user if empty instead of throwing raw exceptions.
- **FR-10: HuggingFace Embedding Mocking** - Mock SentenceTransformer.encode to return mock NumPy arrays, verifying vector store integration without downloading model weights or allocating GPU resources.
- **FR-11: Groq LLM API Mocking** - Mock the Groq client response generation using unittest mocks to verify QA template construction and synthesis logic.
- **FR-12: CLI Output Enhancement** - Format and output the generated LLM response, confidence score, and document source citations on separate lines.

### NonFunctional Requirements

- **NFR-1: Performance Budget** - Under preloaded vector DB collection state, a single query executes and generates response within under 1.5 seconds.
- **NFR-2: Test Isolation** - 100% of automated tests pass without an internet connection or active API keys.
- **NFR-3: Code Hygiene** - Static verification shows zero PEP 8 violations and full type safety across new/refactored modules.

### Additional Requirements

- **AR-1: Unified Command Interface (`src/cli.py`)** - Build a single entry point utilizing argparse to dispatch to separate subcommands (ingest, query, interactive).
- **AR-2: Run Pipeline Retrofit (`src/run_pipeline.py`)** - Retain run_pipeline.py but retrofit it as a backward-compatible wrapper that invokes the new cli.py subcommands, preserving the original outer workflow contract.
- **AR-3: Simple, Explicit Python Implementation** - Avoid complex design patterns (factories, providers, interfaces) in favor of clear, linear standard library or lightweight direct implementations.

### UX Design Requirements

*(No UX Design Requirements - This is a pure command-line developer product. All interface criteria are covered under CLI Functional Requirements.)*

### FR Coverage Map

- **FR-1: Environment-Validated Settings Module** - Epic 1: Core Infrastructure and Codebase Standardization
- **FR-2: Centralized Global Logger** - Epic 1: Core Infrastructure and Codebase Standardization
- **FR-3: Rename RAGRetiever to RAGRetriever** - Epic 1: Core Infrastructure and Codebase Standardization
- **FR-4: Strict Type Annotations** - Epic 1: Core Infrastructure and Codebase Standardization
- **FR-5: Ingest Subcommand** - Epic 2: Decoupled Command-Line Interface (Ingestion vs. Retrieval)
- **FR-6: Query Subcommand** - Epic 2: Decoupled Command-Line Interface (Ingestion vs. Retrieval)
- **FR-7: Interactive Subcommand** - Epic 2: Decoupled Command-Line Interface (Ingestion vs. Retrieval)
- **FR-8: Groq API Error boundaries** - Epic 3: Resilient Service Boundaries & Mocked Verification Suite
- **FR-9: Vector Store Verification Check** - Epic 2: Decoupled Command-Line Interface (Ingestion vs. Retrieval)
- **FR-10: HuggingFace Embedding Mocking** - Epic 3: Resilient Service Boundaries & Mocked Verification Suite
- **FR-11: Groq LLM API Mocking** - Epic 3: Resilient Service Boundaries & Mocked Verification Suite
- **FR-12: CLI Output Enhancement** - Epic 2: Decoupled Command-Line Interface (Ingestion vs. Retrieval)

## Epic List

### Epic 1: Core Infrastructure and Codebase Standardization
**Epic Goal:** Establish the robust, standardized foundational environment for the system. This includes environment-validated configurations, a centralized logger, strict type hinting, and correcting the core `RAGRetriever` class name typos so subsequent development is built on stable, clean code.
**FRs covered:** FR-1, FR-2, FR-3, FR-4

### Epic 2: Decoupled Command-Line Interface (Ingestion vs. Retrieval)
**Epic Goal:** Implement the command-line interface that allows developers to run offline ingestion and online queries separately. This includes the `ingest`, `query`, and `interactive` subcommands under a single `src/cli.py` entrypoint, retrofitting `src/run_pipeline.py` as a backward-compatible wrapper, and verifying store states safely on query.
**FRs covered:** FR-5, FR-6, FR-7, FR-9, FR-12

### Epic 3: Resilient Service Boundaries & Mocked Verification Suite
**Epic Goal:** Implement error-tolerant boundaries around remote network endpoints (Groq client retries and fallbacks) and establish 100% test coverage using pytest with offline mocks (mocked HuggingFace embeddings and Groq responses) so that code changes can be verified quickly without network or token overhead.
**FRs covered:** FR-8, FR-10, FR-11

---

## Epic 1: Core Infrastructure and Codebase Standardization

Establish the robust, standardized foundational environment for the system. This includes environment-validated configurations, a centralized logger, strict type hinting, and correcting the core `RAGRetriever` class name typos so subsequent development is built on stable, clean code.

### Story 1.1: Environment-Validated Settings Module

As a Platform Developer,
I want to load and validate system configurations from environment variables or safe defaults,
So that I can configure Chunk sizes, database paths, and API parameters without editing code.

**Acceptance Criteria:**

**Given** a valid `.env` file exists or default system values are available
**When** the module `src/config.py` is loaded
**Then** settings for database persistence directory, chunk size, chunk overlap, embedding model, and LLM model are exposed as validated constants
**And** any invalid environment variable types raise an informative configuration error at initialization time.

### Story 1.2: Centralized Global Logging Module

As a Platform Operator,
I want the application to use a standard Python logger instead of raw print statements,
So that I can routing levels, parse output logs dynamically, and suppress them during tests.

**Acceptance Criteria:**

**Given** logging level is set (e.g., via config variable)
**When** any pipeline or retrieval operation runs
**Then** log lines are written in the format `[YYYY-MM-DD HH:MM:SS] [LEVEL] [MODULE] - MESSAGE`
**And** raw `print()` statements are replaced across all core modules in `src/`.

### Story 1.3: Typo Renaming & Strict Codebase Typing

As a Maintenance Engineer,
I want to rename RAGRetiever to RAGRetriever and enforce explicit Python type annotations,
So that the codebase aligns with PEP 8 styling, reduces cognitive load, and passes static analysis cleanly.

**Acceptance Criteria:**

**Given** the file `src/rag_retriever.py` contains class `RAGRetiever`
**When** class and file renames are executed
**Then** all files import `from src.rag_retriever import RAGRetriever` cleanly
**And** all core functions inside `src/` include explicit type hints for parameters and return types
**And** zero occurrences of `RAGRetiever` remain in the code.

---

## Epic 2: Decoupled Command-Line Interface (Ingestion vs. Retrieval)

Implement the command-line interface that allows developers to run offline ingestion and online queries separately. This includes the `ingest`, `query`, and `interactive` subcommands under a single `src/cli.py` entrypoint, retrofitting `src/run_pipeline.py` as a backward-compatible wrapper, and verifying store states safely on query.

### Story 2.1: Unified Command Interface and Subcommand Dispatcher

As a Developer,
I want a single CLI entry point with a dispatching interface,
So that I can easily navigate separate ingestion and query workflows.

**Acceptance Criteria:**

**Given** a command-line environment
**When** I run `python src/cli.py --help`
**Then** the terminal outputs clear instructions for `ingest`, `query`, and `interactive` subcommands
**And** running an invalid subcommand returns a clean exit code with syntax help.

### Story 2.2: On-Demand Offline Ingestion Pipeline

As an Ingestion Admin,
I want to execute document parsing, chunking, and embedding as an explicit offline command,
So that ChromaDB is updated only when new files are present, preventing startup indexing overhead.

**Acceptance Criteria:**

**Given** source documents exist in the configured `data/` directory
**When** I execute `python src/cli.py ingest`
**Then** the system loads files, splits texts using configured chunk parameters, generates vector embeddings, and saves them to the persistent vector store
**And** the terminal outputs a clear summary log of the count of loaded documents and generated chunks.

### Story 2.3: Zero-Ingestion Search & Generation CLI

As an Operator,
I want to run a query subcommand that instantly loads the pre-existing ChromaDB index without checking source documents,
So that I receive answers under a fast 1.5-second SLA.

**Acceptance Criteria:**

**Given** a pre-built ChromaDB persistent collection exists
**When** I run `python src/cli.py query "My query"`
**Then** the system loads the persistent store collection directly, performs a semantic search, and prints the synthesized LLM response
**And** the query executes without reading files from the document directory or regenerating embeddings for raw texts.

### Story 2.4: Multi-Turn Interactive Chat CLI Mode

As a Support Operator,
I want to run an interactive loop that keeps the database connection warm,
So that I can conduct multiple sequential searches rapidly.

**Acceptance Criteria:**

**Given** a pre-built persistent vector database
**When** I run `python src/cli.py interactive`
**Then** I am dropped into an active interactive prompt: `Aurora-RAG >`
**And** typing a query outputs the synthesized answer and presents the prompt again
**And** typing `exit` or `quit` terminates the session and returns control to the shell cleanly.

### Story 2.5: Retrofit run_pipeline.py as CLI Wrapper

As a Legacy Integrator,
I want run_pipeline.py to remain in the project as a backward-compatible wrapper,
So that existing automations do not break while leveraging the new decoupled CLI logic.

**Acceptance Criteria:**

**Given** a legacy system calling `python src/run_pipeline.py`
**When** the runner script is invoked
**Then** it internally delegates to `src/cli.py`'s `ingest` command, then launches the `interactive` CLI mode
**And** no duplication of data loaders, chunkers, or embedding logic occurs between modules.

### Story 2.6: Vector Store Empty State Verification

As an Operator,
I want a warning if I execute a query on an empty or missing database index,
So that I am guided to run the ingestion command instead of encountering raw on-disk failures.

**Acceptance Criteria:**

**Given** ChromaDB persistent collection does not exist or has zero records
**When** I run `python src/cli.py query "My query"` or `python src/cli.py interactive`
**Then** the system outputs a clear user-friendly warning: "Database empty. Please run ingestion first via `python src/cli.py ingest`"
**And** the process terminates cleanly without throwing raw on-disk file tracebacks.

### Story 2.7: CLI Source and Confidence Visualization

As an Operator,
I want the CLI to print confidence percentages and file sources on dedicated, separate lines,
So that I can easily verify where information was retrieved from and how certain the system is.

**Acceptance Criteria:**

**Given** a query is executed via direct `query` subcommand or inside an `interactive` loop
**When** a successful response is generated by the retriever
**Then** the output prints the text answer on its own line
**And** the confidence score in percentages is printed on its own line (e.g. `Confidence Score: 85.00%`)
**And** the list of individual source file names and similarity scores are printed on separate lines immediately below.

---

## Epic 3: Resilient Service Boundaries & Mocked Verification Suite

Implement error-tolerant boundaries around remote network endpoints (Groq client retries and fallbacks) and establish 100% test coverage using pytest with offline mocks (mocked HuggingFace embeddings and Groq responses) so that code changes can be verified quickly without network or token overhead.

### Story 3.1: Resilient Groq Client Retries & Fallbacks

As an Operator,
I want the Groq client to retry failed requests during brief network glitches,
So that my active query or interactive session does not terminate unexpectedly.

**Acceptance Criteria:**

**Given** the Groq service returns transient HTTP errors (e.g., 503, 502, or rate limit 429)
**When** the system makes a completion request
**Then** it automatically retries the request up to 3 times with brief backoffs
**And** if all retries fail, it falls back to printing a user-friendly connection warning instead of raw traceback crashes.

### Story 3.2: 100% Mocked Pytest Suite for Offline Testing

As a Validation Engineer,
I want to run a pytest suite that is completely isolated from internet access or live API tokens,
So that I can verify pipeline and search behavioral correctness in under 5 seconds.

**Acceptance Criteria:**

**Given** a test environment without internet access or valid `GROQ_API_KEY`
**When** I run `pytest tests/`
**Then** all tests pass successfully
**And** `sentence_transformers.SentenceTransformer.encode` is mocked to return constant NumPy vector arrays of matching dimension
**And** `groq.Groq` completions are mocked to return deterministic synthetic responses
**And** automated unit tests verify correct behavior for `DataLoader`, `DataChunker`, `VectorStore`, and `RAGRetriever`.
