# Epic 3 Context: Resilient Service Boundaries & Mocked Verification Suite

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Implement error-tolerant boundaries around remote network endpoints (Groq client retries and fallbacks) and establish 100% test coverage using pytest with offline mocks (mocked HuggingFace embeddings and Groq responses) so that code changes can be verified quickly without network or token overhead.

## Stories

- Story 3.1: Resilient Groq Client Retries & Fallbacks
- Story 3.2: 100% Mocked Pytest Suite for Offline Testing

## Requirements & Constraints

- Groq client request retries: automatically retry up to 3 times on transient errors (e.g., 502, 503, 429 rate limits) before raising a user-friendly error or fallback answer.
- 100% Offline testing: All tests must run successfully with no network connections or active API keys.
- HuggingFace embedding mocking: Mock `SentenceTransformer.encode` to return deterministic Mock NumPy arrays of identical shape (vector dimensions).
- Groq API Mocking: Mock `groq.Groq` completions using unittest mocks to return custom response strings and mock structure validation.

## Technical Decisions

- **Resiliency boundary:** Implement retry logic using standard library methods or direct loop handlers within `src/llm_client.py` or `src/rag_retriever.py` to handle Groq API connection and retry errors gracefully.
- **Offline testing architecture:** Put all mocks inside `tests/conftest.py` or individual test fixtures using pytest `monkeypatch` or `unittest.mock` to guarantee that live APIs are never triggered during run.
