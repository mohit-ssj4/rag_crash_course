---
title: 'Epic 3: Resilient Service Boundaries & Mocked Verification Suite'
type: 'feature'
created: '2026-09-12'
status: 'done'
route: 'oneshot'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The system relies on third-party network APIs (Groq LLM completions) and local model downloads (SentenceTransformer embeddings) during pipeline runs. Transient network drops can crash queries, and testing requires active tokens and internet connections, which increases latency and cost.

**Approach:** Implement linear retry boundaries with exponential backoffs around the Groq API call inside `src/rag_retriever.py`, and introduce global automated offline mocks for embeddings and Groq completions in `tests/conftest.py` to achieve 100% isolated offline testing.

</frozen-after-approval>

## Implementation Notes

- **Implemented Groq Retry Boundaries (`src/rag_retriever.py`):** Added a loop executing up to 3 retries with exponential backoffs on Groq completion exceptions, preventing unexpected crashes on transient API hiccups.
- **Implemented Global Test Mocks (`tests/conftest.py`):** Created global autouse fixtures in `conftest.py` that mock both `SentenceTransformer` and `Groq` clients, establishing 100% network isolation across the entire project's tests.
- **Added Robust Verification Tests (`tests/test_retriever.py`):** Wrote unit tests specifically targeting the retry loop (verifying it retries and succeeds on the 3rd attempt, and falls back gracefully to a friendly default answer when retries are completely exhausted).
- **Verified Offline Execution:** Confirmed all 17 unit tests run completely offline and finish in under 8 seconds.

