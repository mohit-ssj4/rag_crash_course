---
title: 'Story 1.2: Centralized Global Logging Module'
type: 'feature'
created: '2026-09-12'
status: 'done'
route: 'oneshot'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Standard print statements are scattered throughout the codebase (e.g., `vector_store.py`, `data_loader.py`, etc.) which cannot be dynamically configured, severity-graded, routed to log files, or silenced during unit testing.

**Approach:** Implement a centralized global logging module `src/logger.py` that configures a formatted standard Python logger with togglable logging levels. Other modules will use this module's loggers instead of raw `print()` statements.

</frozen-after-approval>

## Implementation Notes

- **Created centralized logger (`src/logger.py`):** Configured standardized formatting: `[YYYY-MM-DD HH:MM:SS] [LEVEL] [MODULE] - MESSAGE`.
- **Integrated with Configuration:** Integrated `LOG_LEVEL` parsing inside `src/config.py` with full `.env` loading and uppercase string validation.
- **Added Automated Testing (`tests/test_logger.py`):** Validated singleton properties, non-propagation, levels, and regex formatting outputs on `sys.stderr`.
- **Patched Zero-Overlap Support:** Implemented `_get_env_non_negative_int` in `src/config.py` to allow valid `CHUNK_OVERLAP=0` settings, fixing a major gap.
- **Patched secure level resolution:** Strictly validated `LOG_LEVEL` lookup values in `src/logger.py` using `VALID_LOG_LEVELS` whitelist to block lookups of illegal attributes or injection.

## Review Triage Log

- Strict validation in _get_env_positive_int prevents zero-overlap -- Verdict: `high` -- Validated gap resolved as custom patch (added `_get_env_non_negative_int` and updated `CHUNK_OVERLAP`).
- Insecure lookup using getattr on logging -- Verdict: `medium` -- Validated security risk resolved as custom patch (restricted log levels to `VALID_LOG_LEVELS` whitelist).
- No support for numeric logging levels -- Verdict: `low` -- Standard named levels (DEBUG, INFO, etc.) are sufficient and preferred for simplicity.
- Module-level side effects from load_dotenv() -- Verdict: `false` -- Module load side effect is consistent with the rest of the workspace and original scripts.
- Lack of sub-second (millisecond) precision -- Verdict: `false` -- Excluded to remain strictly compliant with exact date format specification in PRD (`YYYY-MM-DD HH:MM:SS`).
- Unconditional suppression of logger propagation -- Verdict: `low` -- Propagate is set to `False` to prevent double prints in standard CLI stderr outputs.
- State leakage across unit tests -- Verdict: `false` -- Test cases utilize unique logger namespaces, preventing any state leakage or collision.
- Whitespace-padded logging variables -- Verdict: `low` -- Level strings are safe-trimmed via `.strip().upper()`.

