# Epic 2 Context: Decoupled Command-Line Interface (Ingestion vs. Retrieval)

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Implement the command-line interface that allows developers to run offline ingestion and online queries separately. This includes the `ingest`, `query`, and `interactive` subcommands under a single `src/cli.py` entrypoint, retrofitting `src/run_pipeline.py` as a backward-compatible wrapper, and verifying store states safely on query.

## Stories

- Story 2.1: Unified Command Interface and Subcommand Dispatcher
- Story 2.2: On-Demand Offline Ingestion Pipeline
- Story 2.3: Zero-Ingestion Search & Generation CLI
- Story 2.4: Multi-Turn Interactive Chat CLI Mode
- Story 2.5: Retrofit run_pipeline.py as CLI Wrapper
- Story 2.6: Vector Store Empty State Verification

## Requirements & Constraints

- A unified interface inside `src/cli.py` utilizing Python's built-in `argparse` module.
- Ingestion (`python src/cli.py ingest`) must run on-demand and modify ChromaDB, outputting total count of documents and chunks generated.
- Query (`python src/cli.py query "<query>"`) must load the pre-computed collection directly from disk without reading raw source files or regenerating embeddings.
- Interactive mode (`python src/cli.py interactive`) must provide a multi-turn chat shell (`Aurora-RAG >`) that remains warm, handling user input loops and exit keywords cleanly.
- `src/run_pipeline.py` must be retrofitted to call `cli.py`'s `ingest` and `interactive` subcommands to maintain 100% backward compatibility.
- Empty State Validation: Executing queries or interactive sessions on missing or un-ingested databases must warning-fail gracefully, asking users to run ingestion first.

## Technical Decisions

- **Entrypoint:** Use standard standard-library `argparse` in `src/cli.py`. Avoid any complex interactive shells or visual UI packages.
- **Warm database connection:** Keep the same vector store client and database objects active during interactive loop turns to prevent instantiation delays.
- **Separation validation:** Query mode must have zero filesystem reads inside document directories.
