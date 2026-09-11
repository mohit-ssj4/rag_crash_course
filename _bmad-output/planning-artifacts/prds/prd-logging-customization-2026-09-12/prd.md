---
title: Project Aurora Logging Customization and Terminal Log Disabling
created: 2026-09-12
updated: 2026-09-12
status: final
---

# PRD: Project Aurora Logging Customization and Terminal Log Disabling
*Working title — Configurable Console Logging & Clean Query Output*

## 0. Document Purpose
This Product Requirement Document (PRD) defines the requirements for adding a new configuration-driven feature to Project Aurora. The feature enables developers and operators to disable logging from printing to the terminal (stderr) via environment variables. This allows running queries or ingestion commands in a completely clean mode where only the final structured outputs are shown, which is highly beneficial for downstream tool integrations, scripting, and shell piping.

## 1. Vision
While centralized logging (introduced in the previous refactoring phase) is critical for system observability and diagnostics, always outputting log messages to the terminal can clutter standard CLI outputs, especially when executing quick single-shot queries (`python src/cli.py query "<text>"`). 
The vision for this feature is to introduce a flexible, robust environment variable `CONSOLE_LOGGING` that controls whether standard log messages are printed to the terminal (via `sys.stderr` StreamHandler). When disabled, the application runs in a "quiet" or "silent" mode from a log perspective, while still outputting the final retrieved RAG answers, confidence scores, and citations to standard output. This ensures seamless integration with automated scripts, pipelines, and terminal utilities.

## 2. Target User

### 2.1 Jobs To Be Done
- **Automation Engineer / DevOps Specialist:** Wants to pipe the clean output of `cli.py query` into other CLI commands (e.g., jq, grep) without log lines cluttering the payload.
- **Power User / Developer:** Wants to focus entirely on the generated RAG response and sources in their terminal without verbose diagnostic logs unless troubleshooting is actively required.

### 2.2 Key User Journeys
- **UJ-4. User disables console logging to run a clean query.**
  - **Persona:** Mohit, the platform developer.
  - **Context:** Mohit wants to run a query and capture only the final answer without any of the background initialization logs.
  - **Steps:**
    1. Mohit configures `CONSOLE_LOGGING=false` in the `.env` file or passes it as an environment variable: `$env:CONSOLE_LOGGING="false"`.
    2. Mohit executes `python src/cli.py query "What is the remote work policy?"`.
    3. The application loads, initializes the pre-existing ChromaDB store, and performs retrieval and LLM synthesis. No background logs are written to the terminal.
    4. The terminal cleanly prints only the RAG Response, Confidence Score, and Source file citations.

## 3. Features & Requirements

### 4.1 Feature 1: Configuration-Driven Console Logging Toggle
**Description:** Introduces a new boolean config parameter `CONSOLE_LOGGING` loaded from `.env` or system environment variables to control logger stream output.

**Functional Requirements:**

#### FR-13: Configuration for Disabling Console Logging
The configuration module (`src/config.py`) must parse, validate, and expose `CONSOLE_LOGGING` as a global boolean constant.
- **Key:** `CONSOLE_LOGGING`
- **Supported Values:** `true`, `1`, `t`, `y`, `yes` (evaluate to `True`), and `false`, `0`, `f`, `n`, `no` (evaluate to `False`).
- **Default Value:** `True` (if missing or empty, to preserve backward compatibility).
- **Validation:** If an invalid string value (e.g., `invalid_bool`) is provided, the configuration initialization must raise a descriptive `ValueError`.

#### FR-14: Logger Integration for Terminal Log Suppression
The logging module (`src/logger.py`) must respect `CONSOLE_LOGGING`.
- If `CONSOLE_LOGGING` is `True`, the `StreamHandler(sys.stderr)` must be registered on all generated loggers as normal.
- If `CONSOLE_LOGGING` is `False`, the `StreamHandler` must not be added. No log handlers printing to terminal/console should be registered, effectively silencing console logs.
- The system must ensure that loggers do not propagate messages to a default root logger that might print them, maintaining absolute terminal silence for logs.

#### FR-15: Clean Query and Ingestion CLI Modes
- When `CONSOLE_LOGGING` is disabled, running `python src/cli.py query "<text>"` or `python src/cli.py ingest` must not print log lines (like `Starting offline data ingestion...`) to the console.
- In query mode, the final output produced by `print_formatted_response` (which writes to stdout) must remain fully functional and visible, ensuring clean, machine-parseable RAG outputs.

## 4. Non-Functional Requirements
- **NFR-4: Zero Overhead** - Disabling console logging must not introduce any performance penalty or measurable latency in pipeline execution.
- **NFR-5: Backward Compatibility** - Existing deployments that do not define `CONSOLE_LOGGING` in their environment must default to `True` and maintain identical terminal output.

## 5. Verification and Test Plan
- **Test Case 1: Config Parsing of Boolean Constants**
  - Verify that `src/config.py` correctly parses truthy and falsy strings to booleans.
  - Verify that an invalid string raises a `ValueError` with a helpful message.
- **Test Case 2: Logger Silence Integration**
  - Verify that when `CONSOLE_LOGGING` is `True`, handlers include the `StreamHandler`.
  - Verify that when `CONSOLE_LOGGING` is `False`, the logger contains no stream handlers that output to console (e.g., registers a `NullHandler` or simply skips adding `StreamHandler`).
- **Test Case 3: Output Formatting and Silence Validation**
  - Verify via end-to-end / capsys tests that when logging is disabled, query and ingest execution results in 0 standard error / log lines in capsys, while query results are still fully present in standard output.
