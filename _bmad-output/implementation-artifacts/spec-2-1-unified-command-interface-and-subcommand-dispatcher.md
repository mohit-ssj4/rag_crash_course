---
title: 'Story 2.1: Unified Command Interface and Subcommand Dispatcher'
type: 'feature'
created: '2026-09-12'
status: 'done'
route: 'oneshot'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The current prototype lacks a command-line entry point to drive offline ingestion and online retrieval separately, forcing redundant data loading and embedding on every single search.

**Approach:** Implement `src/cli.py` utilizing Python's built-in `argparse` module to define three subcommands: `ingest` (runs document parsing and store indexing), `query` (performs a single search), and `interactive` (drops into a multi-turn chat session).

</frozen-after-approval>

## Implementation Notes

- **Created unified CLI (`src/cli.py`):** Configured standard Python `argparse` to handle routing for `ingest`, `query <query>`, and `interactive` commands.
- **Implemented offline ingestion pipeline:** Tied loading, chunking, and embedding to run strictly on-demand inside `handle_ingest()`.
- **Implemented zero-ingestion retrieval:** Integrated pre-computed index retrieval inside `handle_query()` and `handle_interactive()`, completely isolating raw files during online sessions.
- **Implemented multi-turn warm loop:** Added a standard command loop in `handle_interactive()` using a warm connection to avoid instantiation lag.
- **Retro-fitted legacy script (`src/run_pipeline.py`):** Replaced legacy logic with direct clean delegation to `cli.py` handlers, preserving backwards-compatibility and ensuring zero logic duplication.
- **Added safety warnings (`tests/test_cli.py`):** Added a check in `cli.py` that fails-safe with a warnings log if a query/session is executed on an empty or missing store. Verified with unit tests capturing logger outputs via `caplog`.

