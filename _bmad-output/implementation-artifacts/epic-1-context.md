# Epic 1 Context: Core Infrastructure and Codebase Standardization

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Establish the robust, standardized foundational environment for the system. This includes environment-validated configurations, a centralized logger, strict type hinting, and correcting the core `RAGRetriever` class name typos so subsequent development is built on stable, clean code.

## Stories

- Story 1.1: Environment-Validated Settings Module
- Story 1.2: Centralized Global Logging Module
- Story 1.3: Typo Renaming & Strict Codebase Typing

## Requirements & Constraints

- System must load and validate configurations from environment variables or safe, documented defaults.
- All standard outputs and logging must flow through Python’s standard `logging` library instead of raw `print()` statements.
- Strict type annotations must be enforced across all parameters and return values inside the core source directory (`src/`).
- Renaming class `RAGRetiever` to `RAGRetriever` must be performed cleanly, maintaining backwards compatibility where required.

## Technical Decisions

- **Config Module (`src/config.py`):** Use standard library features (like `os` and type-cast handlers) to load `.env` parameters cleanly. Define constants with safe fallbacks.
- **Logger Module (`src/logger.py`):** Set up global formatting: `[YYYY-MM-DD HH:MM:SS] [LEVEL] [MODULE] - MESSAGE`. Provide functions or hooks to easily get pre-configured loggers and toggle logging levels (DEBUG, INFO, etc.).
- **Code Standards:** Adhere strictly to PEP 8 styling guidelines and eliminate all un-typed or weakly typed declarations in core files. Do not use complex factories or abstractions; write clear, explicit, linear Python code.
