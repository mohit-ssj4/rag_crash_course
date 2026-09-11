---
title: 'Story 1.1: Environment-Validated Settings Module'
type: 'feature'
created: '2026-09-12'
status: 'done'
route: 'oneshot'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The current RAG prototype has multiple hardcoded configuration values (e.g., database path, chunk size, overlap, embedding model, LLM model) scattered across files, violating Twelve-Factor App principles and preventing simple, environment-controlled customization.

**Approach:** Create `src/config.py` using standard environment variable loading (via `os.environ` and `.env` parsing) with robust validation and safe defaults to centralize and validate all system parameters.

</frozen-after-approval>

## Implementation Notes

- **Created config settings (`src/config.py`):** Established a centralized `src/config.py` configuration loader that loads configurations from `.env` or system environment variables, with strict type casting and validation.
- **Added safety bounds:** Added validation to raise an informative `ValueError` if `CHUNK_SIZE`, `CHUNK_OVERLAP`, or `EMBEDDING_BATCH_SIZE` are not positive integers, or if `CHUNK_OVERLAP` is greater than or equal to `CHUNK_SIZE`.
- **Created automated tests (`tests/test_config.py`):** Implemented unit tests covering default values, custom overrides, and negative validation limits.
- **Verified build:** Ran `uv run --with pytest python -m pytest tests/test_config.py` with 100% test success (5/5 passed).

## Review Triage Log

- Global/Module-Level State Mutation via importlib.reload -- Verdict: `false` -- Standard Python CLI pattern; a config module with simple, module-level settings is explicit and linear, fitting project refactoring goals (no factories/providers).
- Silently Defaulting on Empty/Blank Environment Variables -- Verdict: `low` -- Defaulting empty environment overrides to safe system fallbacks is standard, user-convenient fallback behavior.
- Inflexible Validator Name and Logic for Integer Configuration -- Verdict: `low` -- Naming of validator helper resolved as custom patch (renamed `_get_env_int` to `_get_env_positive_int`).
- Missing Validation of Critical String Configurations -- Verdict: `low` -- Fallback and ChromaDB's native directory error handling is sufficient for basic string configurations.
- Incomplete Custom Value Coverage in Tests -- Verdict: `medium` -- Validated gap resolved as custom patch (added string override asserts to `tests/test_config.py`).
- No Support or Parsers for Other Config Types -- Verdict: `false` -- Out of scope for current specifications and MVP requirements.


